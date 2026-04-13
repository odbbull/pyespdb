"""
Line Graph screen — plot metric data over time for selected databases.

Flow:
  1. Select a collection  →  database checklist appears (colored swatches).
  2. Check one or more databases.
  3. Select a category  →  acronym multi-select appears (if > 1 acronym).
  4. Optionally filter acronyms.
  5. Click Generate — one line per (database × acronym):
       X axis : date / time  (mp_plotdate)
       Y axis : metric value (mp_plotvalue), summed across RAC instances.
       Each database uses the color shown in the checklist.
       Multiple acronyms within the same database use different dash styles.
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

_DASHES = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]

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


def _collection_opts():
    rows = _run("""
        SELECT co.coll_id,
               co.coll_name || '  (' || c.cl_name || ' / ' || p.pr_name || ')' AS label
          FROM sp_collection co
          JOIN sp_project p ON p.pr_id = co.sp_project_pr_id
          JOIN sp_client  c ON c.cl_id = p.sp_client_cl_id
         WHERE co.is_active_fg = TRUE
         ORDER BY co.coll_name
    """)
    return [{"label": r["label"], "value": r["coll_id"]} for r in rows]


def _databases_for_collection(coll_id):
    """Return list of dicts with db_id, db_name, db_metrics_date for a collection."""
    return _run("""
        SELECT db_id, db_name, db_metrics_date
          FROM sp_database
         WHERE sp_collection_coll_id = %s
           AND db_metrics_date IS NOT NULL
         ORDER BY db_name
    """, (coll_id,))


def _checklist_opts(db_rows):
    """
    Build dbc.Checklist options with a colored swatch next to each db name.
    Prepends an "All Databases" option.
    Returns (options_list, color_map {str(db_id): color}).
    """
    opts      = [{
        "label": html.Span([
            html.Span("\u25A0 ",
                      style={"color": "#5a5c69", "fontSize": "1.0rem", "marginRight": "4px"}),
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
                html.Span("\u25CF ",
                          style={"color": color, "fontSize": "1.1rem", "marginRight": "4px"}),
                r["db_name"] + date_str,
            ]),
            "value": r["db_id"],
        })
    return opts, color_map


def _resolve_db_ids(selected, color_map):
    """Expand _ALL_VALUE sentinel to all real db_ids from the color map."""
    if _ALL_VALUE in (selected or []):
        return [int(k) for k in color_map]
    return [v for v in (selected or []) if v != _ALL_VALUE]


def _category_opts_for_dbs(db_ids):
    """Distinct category names available across all selected databases."""
    if not db_ids:
        return []
    rows = _run("""
        SELECT DISTINCT mp_metricname AS cat_name
          FROM sp_metricplot
         WHERE sp_database_db_id = ANY(%s)
         ORDER BY mp_metricname
    """, (list(db_ids),))
    return [{"label": r["cat_name"], "value": r["cat_name"]} for r in rows]


def _acronym_opts_for_dbs(db_ids, cat_name):
    """Distinct acronyms for a category across all selected databases."""
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
        SELECT cat_yaxis_unit
          FROM sp_category
         WHERE cat_name = %s AND is_active_fg = TRUE
         LIMIT 1
    """, (cat_name,))
    if rows and rows[0]["cat_yaxis_unit"]:
        unit = rows[0]["cat_yaxis_unit"]
        m = re.search(r'\(([^)]+)\)$', unit)
        return m.group(1) if m else unit
    return cat_name


def _fetch_plot_data(db_ids, cat_name, acronyms=None):
    """
    Return rows with db_id, db_name, series_acr, mp_plotdate, plot_value
    for the selected databases and category, summed across RAC instances.
    """
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

    # Organise into series: {(db_id, acr): [(date, value), ...]}
    series: dict = {}
    for r in rows:
        key = (r["db_id"], r["series_acr"])
        series.setdefault(key, []).append((r["mp_plotdate"], float(r["plot_value"] or 0)))

    # Build a stable acronym → dash-style index
    present_acrs = sorted({k[1] for k in series})
    acr_dash_idx = {acr: i for i, acr in enumerate(present_acrs)}

    y_label = _y_axis_label(cat_name)

    fig = go.Figure()
    for (db_id, acr), points in sorted(series.items(), key=lambda x: (x[0][0], x[0][1])):
        # Look up db_name from first matching row
        db_name = next((r["db_name"] for r in rows if r["db_id"] == db_id), str(db_id))
        color   = color_map.get(str(db_id), _COLOURS[0])
        dash    = _DASHES[acr_dash_idx[acr] % len(_DASHES)]

        name = acr

        dates  = [p[0] for p in points]
        values = [p[1] for p in points]

        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode="lines",
            name=name,
            line=dict(color=color, width=2, dash=dash),
            hovertemplate=f"<b>{name}</b><br>%{{x}}<br>%{{y:.3f}} {y_label}<extra></extra>",
        ))

    fig.update_layout(
        xaxis=dict(
            title="Date / Time",
            showgrid=True,
            gridcolor="#f0f0f0",
            tickformat="%Y-%m-%d %H:%M",
        ),
        yaxis=dict(
            title=y_label,
            showgrid=True,
            gridcolor="#f0f0f0",
            zeroline=True,
            zerolinecolor="#e0e0e0",
        ),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=60, l=70, r=30),
        height=480,
        hovermode="x unified",
    )
    return fig, None


# ── Page layout ───────────────────────────────────────────────────────────────

def generate_line_graph_page():
    return html.Div([
        html.H2("Metric Line Graph"),
        html.Hr(className="mb-4"),

        # Stores the {db_id_str: color} mapping for the current collection
        dcc.Store(id="lg-color-store"),

        # ── Selection card ────────────────────────────────────────────────────
        dbc.Card([
            dbc.CardHeader(html.Span("Select Collection, Databases & Category",
                                     className="fw-semibold")),
            dbc.CardBody([
                # Row 1: collection | database checklist | category
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Collection", className="fw-semibold"),
                        dcc.Dropdown(
                            id="lg-collection-dd",
                            options=_collection_opts(),
                            placeholder="Select a collection…",
                            clearable=True,
                        ),
                    ], width=4),

                    dbc.Col([
                        dbc.Label("Databases", className="fw-semibold"),
                        html.Div(
                            dbc.Checklist(
                                id="lg-db-checklist",
                                options=[],
                                value=[],
                                inputStyle={"marginRight": "6px"},
                            ),
                            style={
                                "maxHeight": "160px",
                                "overflowY": "auto",
                                "border": "1px solid #ced4da",
                                "borderRadius": "4px",
                                "padding": "6px 10px",
                                "backgroundColor": "#fff",
                            },
                            id="lg-db-checklist-box",
                        ),
                        html.Small("Only databases with metrics generated are shown.",
                                   className="text-muted"),
                    ], width=4),

                    dbc.Col([
                        dbc.Label("Category", className="fw-semibold"),
                        dcc.Dropdown(
                            id="lg-category-dd",
                            options=[],
                            placeholder="Select a category…",
                            clearable=True,
                            disabled=True,
                        ),
                    ], width=4),
                ], className="g-3"),

                # Row 2: acronym filter, aligned under Category
                dbc.Row([
                    dbc.Col(width={"size": 4, "offset": 8}, children=[
                        dbc.Label("Acronyms", className="fw-semibold"),
                        dcc.Dropdown(
                            id="lg-acronym-dd",
                            options=[],
                            placeholder="All acronyms — select to filter…",
                            multi=True,
                            clearable=True,
                            disabled=True,
                        ),
                        html.Small("Leave blank to plot all acronyms.",
                                   className="text-muted"),
                    ]),
                ], className="g-3 mt-1"),
            ]),
        ], className="mb-4"),

        # ── Generate button ───────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    [html.I(className="fas fa-chart-line me-2"), "Generate Graph"],
                    id="lg-generate-btn",
                    color="primary",
                    size="lg",
                    disabled=True,
                ),
                className="text-center",
            ),
            className="mb-4",
        ),

        # ── Chart output ──────────────────────────────────────────────────────
        html.Div(id="lg-chart-output"),
    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_callbacks(app):

    # Collection → populate database checklist + store colors; reset category/acronym
    @app.callback(
        Output("lg-db-checklist", "options"),
        Output("lg-db-checklist", "value"),
        Output("lg-color-store",  "data"),
        Output("lg-category-dd",  "options"),
        Output("lg-category-dd",  "value"),
        Output("lg-category-dd",  "disabled"),
        Output("lg-acronym-dd",   "options"),
        Output("lg-acronym-dd",   "value"),
        Output("lg-acronym-dd",   "disabled"),
        Input("lg-collection-dd", "value"),
        prevent_initial_call=True,
    )
    def _on_collection(coll_id):
        blank_cat = ([], None, True)
        blank_acr = ([], None, True)
        if not coll_id:
            return [], [], {}, *blank_cat, *blank_acr
        db_rows = _databases_for_collection(coll_id)
        if not db_rows:
            return [], [], {}, *blank_cat, *blank_acr
        opts, color_map = _checklist_opts(db_rows)
        return opts, [], color_map, *blank_cat, *blank_acr

    # Database selection → populate category; reset acronym
    @app.callback(
        Output("lg-category-dd", "options",  allow_duplicate=True),
        Output("lg-category-dd", "value",    allow_duplicate=True),
        Output("lg-category-dd", "disabled", allow_duplicate=True),
        Output("lg-acronym-dd",  "options",  allow_duplicate=True),
        Output("lg-acronym-dd",  "value",    allow_duplicate=True),
        Output("lg-acronym-dd",  "disabled", allow_duplicate=True),
        Input("lg-db-checklist", "value"),
        State("lg-color-store",  "data"),
        prevent_initial_call=True,
    )
    def _on_db_selection(db_ids, color_map):
        blank = ([], None, True)
        real  = _resolve_db_ids(db_ids, color_map or {})
        if not real:
            return [], None, True, *blank
        opts = _category_opts_for_dbs(real)
        return opts, None, len(opts) == 0, *blank

    # Category → populate acronym multi-select
    @app.callback(
        Output("lg-acronym-dd", "options",  allow_duplicate=True),
        Output("lg-acronym-dd", "value",    allow_duplicate=True),
        Output("lg-acronym-dd", "disabled", allow_duplicate=True),
        Input("lg-category-dd",  "value"),
        State("lg-db-checklist", "value"),
        State("lg-color-store",  "data"),
        prevent_initial_call=True,
    )
    def _on_category(cat_name, db_ids, color_map):
        if not cat_name or not db_ids:
            return [], None, True
        real     = _resolve_db_ids(db_ids, color_map or {})
        opts     = _acronym_opts_for_dbs(real, cat_name)
        disabled = len(opts) <= 1
        return opts, None, disabled

    # Enable generate button when at least one database + category selected
    @app.callback(
        Output("lg-generate-btn", "disabled"),
        Input("lg-db-checklist",  "value"),
        Input("lg-category-dd",   "value"),
        State("lg-color-store",   "data"),
    )
    def _toggle_btn(db_ids, cat_name, color_map):
        real = _resolve_db_ids(db_ids, color_map or {})
        return not (real and cat_name)

    # Generate → render chart
    @app.callback(
        Output("lg-chart-output", "children"),
        Input("lg-generate-btn",  "n_clicks"),
        State("lg-db-checklist",  "value"),
        State("lg-category-dd",   "value"),
        State("lg-acronym-dd",    "value"),
        State("lg-color-store",   "data"),
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
            title = f"{cat_name} \u2014 All Databases"
        elif len(real) == 1:
            db_rows = _run("SELECT db_name FROM sp_database WHERE db_id = %s", (real[0],))
            title   = f"{cat_name} \u2014 {db_rows[0]['db_name'] if db_rows else real[0]}"
        else:
            title = f"{cat_name} \u2014 {len(real)} databases"

        if acronyms:
            title += f"  ({', '.join(sorted(acronyms))})"

        fig, err = _build_chart(real, cat_name, color_map, acronyms=acronyms)

        if err or fig is None:
            return dbc.Alert(
                [html.I(className="fas fa-exclamation-triangle me-2"), err or "No data."],
                color="warning",
            )

        return dbc.Card([
            dbc.CardHeader(html.Strong(title)),
            dbc.CardBody(
                dcc.Graph(
                    figure=fig,
                    config={"displayModeBar": True,
                            "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
                )
            ),
        ], style={"borderRadius": "0.5rem", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"})
