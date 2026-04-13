"""
Database Graph screen — jumped to from Collection Summary.

URL formats:
  /dbGraph/{coll_id}                              — blank, user picks everything
  /dbGraph/{coll_id}/{db_id}/{cat_name}           — pre-select db + category, auto-generate
  /dbGraph/{coll_id}/{db_id}/{cat_name}/{cat_acr} — pre-select db + category + acronym, auto-generate

When db_id and cat_name are present the chart is generated immediately on page load.
"""

import re

from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from pyespUtil import connect_postgres_db


# ── Palette ───────────────────────────────────────────────────────────────────

_COLOURS = [
    "#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b",
    "#858796", "#5a5c69", "#2e59d9", "#17a673", "#2c9faf",
]
_DASHES   = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]
_ALL_VALUE = "__all__"


# ── DB helpers ────────────────────────────────────────────────────────────────

def _run(sql, params=None):
    conn = connect_postgres_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def _collection_info(coll_id):
    rows = _run("""
        SELECT co.coll_name, c.cl_name, p.pr_name
          FROM sp_collection co
          JOIN sp_project p ON p.pr_id = co.sp_project_pr_id
          JOIN sp_client  c ON c.cl_id = p.sp_client_cl_id
         WHERE co.coll_id = %s
    """, (coll_id,))
    return rows[0] if rows else None


def _databases_for_collection(coll_id):
    return _run("""
        SELECT db_id, db_name, db_metrics_date
          FROM sp_database
         WHERE sp_collection_coll_id = %s
           AND db_metrics_date IS NOT NULL
         ORDER BY db_name
    """, (coll_id,))


def _checklist_opts(db_rows):
    opts = [{
        "label": html.Span([
            html.Span("\u25A0 ", style={"color": "#5a5c69", "fontSize": "1.0rem",
                                        "marginRight": "4px"}),
            html.Strong("\u2500\u2500 All Databases \u2500\u2500"),
        ]),
        "value": _ALL_VALUE,
    }]
    color_map = {}
    for idx, r in enumerate(db_rows):
        color = _COLOURS[idx % len(_COLOURS)]
        color_map[str(r["db_id"])] = color
        date_str = f"  \u2713 {str(r['db_metrics_date'])[:10]}" if r["db_metrics_date"] else ""
        opts.append({
            "label": html.Span([
                html.Span("\u25CF ", style={"color": color, "fontSize": "1.1rem",
                                             "marginRight": "4px"}),
                r["db_name"] + date_str,
            ]),
            "value": r["db_id"],
        })
    return opts, color_map


def _resolve_db_ids(selected, color_map):
    if _ALL_VALUE in (selected or []):
        return [int(k) for k in color_map]
    return [v for v in (selected or []) if v != _ALL_VALUE]


def _category_opts(db_ids):
    if not db_ids:
        return []
    rows = _run("""
        SELECT DISTINCT mp_metricname AS cat_name
          FROM sp_metricplot
         WHERE sp_database_db_id = ANY(%s)
         ORDER BY mp_metricname
    """, (list(db_ids),))
    return [{"label": r["cat_name"], "value": r["cat_name"]} for r in rows]


def _acronym_opts(db_ids, cat_name):
    if not db_ids or not cat_name:
        return []
    rows = _run("""
        SELECT DISTINCT mp_metricacronym AS acronym
          FROM sp_metricplot
         WHERE sp_database_db_id = ANY(%s)
           AND mp_metricname     = %s
         ORDER BY mp_metricacronym
    """, (list(db_ids), cat_name))
    return [{"label": r["acronym"], "value": r["acronym"]} for r in rows]


def _y_axis_label(cat_name):
    rows = _run("""
        SELECT cat_yaxis_unit FROM sp_category
         WHERE cat_name = %s AND is_active_fg = TRUE
         LIMIT 1
    """, (cat_name,))
    if rows and rows[0]["cat_yaxis_unit"]:
        unit = rows[0]["cat_yaxis_unit"]
        m = re.search(r'\(([^)]+)\)$', unit)
        return m.group(1) if m else unit
    return cat_name


def _fetch_plot_data(db_ids, cat_name, acronyms=None):
    acr_clause = "AND mp.mp_metricacronym = ANY(%s)" if acronyms else ""
    params = [list(db_ids), cat_name]
    if acronyms:
        params.append(list(acronyms))
    return _run(f"""
        SELECT db.db_id,
               db.db_name,
               mp.mp_metricacronym                   AS series_acr,
               mp.mp_plotdate,
               SUM(CAST(mp.mp_plotvalue AS NUMERIC))  AS plot_value
          FROM sp_metricplot mp
          JOIN sp_database db ON db.db_id = mp.sp_database_db_id
         WHERE mp.sp_database_db_id = ANY(%s)
           AND mp.mp_metricname     = %s
           {acr_clause}
         GROUP BY db.db_id, db.db_name, mp.mp_metricacronym, mp.mp_plotdate
         ORDER BY db.db_name, mp.mp_metricacronym, mp.mp_plotdate
    """, params)


# ── Chart builder ─────────────────────────────────────────────────────────────

def _build_chart(db_ids, cat_name, color_map, acronyms=None):
    rows = _fetch_plot_data(db_ids, cat_name, acronyms=acronyms or None)
    if not rows:
        return None, "No metric data found for this selection."

    series = {}
    for r in rows:
        key = (r["db_id"], r["series_acr"])
        series.setdefault(key, []).append((r["mp_plotdate"], float(r["plot_value"] or 0)))

    present_acrs = sorted({k[1] for k in series})
    acr_dash_idx = {acr: i for i, acr in enumerate(present_acrs)}
    y_label      = _y_axis_label(cat_name)

    fig = go.Figure()
    for (db_id, acr), points in sorted(series.items(), key=lambda x: (x[0][0], x[0][1])):
        db_name = next((r["db_name"] for r in rows if r["db_id"] == db_id), str(db_id))
        color   = color_map.get(str(db_id), _COLOURS[0])
        dash    = _DASHES[acr_dash_idx[acr] % len(_DASHES)]
        fig.add_trace(go.Scatter(
            x=[p[0] for p in points],
            y=[p[1] for p in points],
            mode="lines",
            name=f"{db_name} / {acr}",
            line=dict(color=color, width=2, dash=dash),
            hovertemplate=(
                f"<b>{db_name} — {acr}</b><br>%{{x}}<br>%{{y:.3f}} {y_label}<extra></extra>"
            ),
        ))

    fig.update_layout(
        xaxis=dict(title="Date / Time", showgrid=True, gridcolor="#f0f0f0",
                   tickformat="%Y-%m-%d %H:%M"),
        yaxis=dict(title=y_label, showgrid=True, gridcolor="#f0f0f0",
                   zeroline=True, zerolinecolor="#e0e0e0"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=60, b=60, l=70, r=30),
        height=480, hovermode="x unified",
    )
    return fig, None


def _chart_card(title, fig, err):
    if err or fig is None:
        return dbc.Alert(
            [html.I(className="fas fa-exclamation-triangle me-2"), err or "No data."],
            color="warning",
        )
    return dbc.Card([
        dbc.CardHeader(html.Strong(title)),
        dbc.CardBody(dcc.Graph(
            figure=fig,
            config={"displayModeBar": True,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
        )),
    ], style={"borderRadius": "0.5rem", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"})


# ── Page layout ───────────────────────────────────────────────────────────────

def generate_db_graph_page(coll_id, db_id=None, cat_name=None, cat_acronym=None):
    try:
        coll_id = int(coll_id)
    except (TypeError, ValueError):
        return html.Div([html.H2("Invalid collection ID")])

    info = _collection_info(coll_id)
    if not info:
        return html.Div([html.H2("Collection not found"),
                         html.P(f"No collection with ID {coll_id}.")])

    coll_name = info["coll_name"]
    cl_name   = info["cl_name"]
    pr_name   = info["pr_name"]

    db_rows = _databases_for_collection(coll_id)
    checklist_opts, color_map_init = _checklist_opts(db_rows) if db_rows else ([], {})

    # ── Pre-selection from URL params ─────────────────────────────────────────
    pre_db_id      = int(db_id) if db_id else None
    pre_cat_name   = cat_name or None
    pre_cat_acronym = cat_acronym or None

    initial_db_value  = [pre_db_id] if pre_db_id else []
    initial_cat_value = pre_cat_name
    initial_acr_value = [pre_cat_acronym] if pre_cat_acronym else None

    if pre_db_id:
        cat_opts     = _category_opts([pre_db_id])
        cat_disabled = len(cat_opts) == 0
    else:
        cat_opts     = []
        cat_disabled = True

    if pre_db_id and pre_cat_name:
        acr_opts     = _acronym_opts([pre_db_id], pre_cat_name)
        acr_disabled = len(acr_opts) <= 1
        btn_disabled = False
    else:
        acr_opts     = []
        acr_disabled = True
        btn_disabled = True

    # ── Auto-generate chart when fully pre-selected ───────────────────────────
    initial_chart = html.Div()
    if pre_db_id and pre_cat_name:
        acronyms  = [pre_cat_acronym] if pre_cat_acronym else None
        db_name   = next((r["db_name"] for r in db_rows if r["db_id"] == pre_db_id),
                         str(pre_db_id))
        title     = f"{pre_cat_name} — {db_name}"
        if pre_cat_acronym:
            title += f"  ({pre_cat_acronym})"
        fig, err  = _build_chart([pre_db_id], pre_cat_name, color_map_init, acronyms=acronyms)
        initial_chart = _chart_card(title, fig, err)

    return html.Div([

        # Back link
        html.Div(
            dcc.Link(
                [html.I(className="fas fa-arrow-left me-2"), "Back to Collection Summary"],
                href="/collSummary",
                style={"textDecoration": "none", "color": "#4e73df", "fontSize": "0.875rem"},
            ),
            className="mb-3",
        ),

        # Header
        html.Div([
            html.Div([
                html.I(className="fas fa-chart-line me-3",
                       style={"fontSize": "2rem", "color": "#4e73df"}),
                html.Div([
                    html.H2(f"Database Graph — {coll_name}",
                            style={"margin": 0, "fontWeight": "800", "color": "#2d3748"}),
                    html.P(f"Client: {cl_name}  |  Project: {pr_name}",
                           style={"margin": 0, "color": "#718096", "fontSize": "0.85rem"}),
                ]),
            ], style={"display": "flex", "alignItems": "center"}),
        ], style={
            "background": "linear-gradient(135deg, #f7faff 0%, #eef2ff 100%)",
            "borderRadius": "0.75rem", "padding": "1.25rem 1.5rem",
            "marginBottom": "1.5rem", "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
        }),

        dcc.Store(id="dg-color-store", data=color_map_init),

        # Selection card
        dbc.Card([
            dbc.CardHeader(html.Span("Select Databases & Category", className="fw-semibold")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Databases", className="fw-semibold"),
                        html.Div(
                            dbc.Checklist(
                                id="dg-db-checklist",
                                options=checklist_opts,
                                value=initial_db_value,
                                inputStyle={"marginRight": "6px"},
                            ),
                            style={
                                "maxHeight": "180px", "overflowY": "auto",
                                "border": "1px solid #ced4da", "borderRadius": "4px",
                                "padding": "6px 10px", "backgroundColor": "#fff",
                            },
                        ),
                        html.Small("Only databases with metrics generated are shown.",
                                   className="text-muted"),
                    ], width=4),

                    dbc.Col([
                        dbc.Label("Category", className="fw-semibold"),
                        dcc.Dropdown(
                            id="dg-category-dd",
                            options=cat_opts,
                            value=initial_cat_value,
                            placeholder="Select a category…",
                            clearable=True,
                            disabled=cat_disabled,
                        ),
                    ], width=4),

                    dbc.Col([
                        dbc.Label("Acronyms", className="fw-semibold"),
                        dcc.Dropdown(
                            id="dg-acronym-dd",
                            options=acr_opts,
                            value=initial_acr_value,
                            placeholder="All acronyms — select to filter…",
                            multi=True,
                            clearable=True,
                            disabled=acr_disabled,
                        ),
                        html.Small("Leave blank to plot all acronyms.", className="text-muted"),
                    ], width=4),
                ], className="g-3"),
            ]),
        ], className="mb-4"),

        dbc.Row(
            dbc.Col(
                dbc.Button(
                    [html.I(className="fas fa-chart-line me-2"), "Generate Graph"],
                    id="dg-generate-btn",
                    color="primary", size="lg", disabled=btn_disabled,
                ),
                className="text-center",
            ),
            className="mb-4",
        ),

        html.Div(initial_chart, id="dg-chart-output"),
    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_callbacks(app):

    @app.callback(
        Output("dg-category-dd", "options"),
        Output("dg-category-dd", "value"),
        Output("dg-category-dd", "disabled"),
        Output("dg-acronym-dd",  "options"),
        Output("dg-acronym-dd",  "value"),
        Output("dg-acronym-dd",  "disabled"),
        Input("dg-db-checklist", "value"),
        State("dg-color-store",  "data"),
        prevent_initial_call=True,
    )
    def _on_db_selection(db_ids, color_map):
        blank = ([], None, True)
        real  = _resolve_db_ids(db_ids, color_map or {})
        if not real:
            return [], None, True, *blank
        opts = _category_opts(real)
        return opts, None, len(opts) == 0, *blank

    @app.callback(
        Output("dg-acronym-dd", "options",  allow_duplicate=True),
        Output("dg-acronym-dd", "value",    allow_duplicate=True),
        Output("dg-acronym-dd", "disabled", allow_duplicate=True),
        Input("dg-category-dd",  "value"),
        State("dg-db-checklist", "value"),
        State("dg-color-store",  "data"),
        prevent_initial_call=True,
    )
    def _on_category(cat_name, db_ids, color_map):
        if not cat_name or not db_ids:
            return [], None, True
        real = _resolve_db_ids(db_ids, color_map or {})
        opts = _acronym_opts(real, cat_name)
        return opts, None, len(opts) <= 1

    @app.callback(
        Output("dg-generate-btn", "disabled"),
        Input("dg-db-checklist",  "value"),
        Input("dg-category-dd",   "value"),
        State("dg-color-store",   "data"),
    )
    def _toggle_btn(db_ids, cat_name, color_map):
        real = _resolve_db_ids(db_ids, color_map or {})
        return not (real and cat_name)

    @app.callback(
        Output("dg-chart-output", "children"),
        Input("dg-generate-btn",  "n_clicks"),
        State("dg-db-checklist",  "value"),
        State("dg-category-dd",   "value"),
        State("dg-acronym-dd",    "value"),
        State("dg-color-store",   "data"),
        prevent_initial_call=True,
    )
    def _generate(_, db_ids, cat_name, acronyms, color_map):
        if not db_ids or not cat_name:
            return no_update

        color_map = color_map or {}
        real      = _resolve_db_ids(db_ids, color_map)
        if not real:
            return no_update

        if _ALL_VALUE in (db_ids or []):
            title = f"{cat_name} — All Databases"
        elif len(real) == 1:
            rows  = _run("SELECT db_name FROM sp_database WHERE db_id = %s", (real[0],))
            title = f"{cat_name} — {rows[0]['db_name'] if rows else real[0]}"
        else:
            title = f"{cat_name} — {len(real)} databases"

        if acronyms:
            title += f"  ({', '.join(sorted(acronyms))})"

        fig, err = _build_chart(real, cat_name, color_map, acronyms=acronyms)
        return _chart_card(title, fig, err)
