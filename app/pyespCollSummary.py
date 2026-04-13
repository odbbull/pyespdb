"""
Collection Summary screen — select a collection, view per-database peak and
average utilization across five metric categories in scrollable tables.

Left three panels (CPU, MBPS, IOPS) are fixed.
Right two panels have a dropdown to switch between any of the five categories.

Each database row is a clickable link that jumps to the Database Graph screen
pre-populated with that database and category, auto-generating the chart.
"""

import math

from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc

from pyespUtil import connect_postgres_db


# ── Fixed panel definitions (left three) ─────────────────────────────────────

# (metric_name, label, unit, accent_color, icon_class)
FIXED_CATEGORIES = [
    ("CPU",  "CPU",  "sessions", "#4e73df", "fas fa-microchip"),
    ("MBPS", "MBPS", "MB/s",     "#1cc88a", "fas fa-network-wired"),
    ("IOPS", "IOPS", "req/s",    "#36b9cc", "fas fa-hdd"),
]

# Color palette cycled for dynamically discovered categories
_PALETTE = ["#f6c23e", "#e74a3b", "#858796", "#5a5c69", "#2e59d9",
            "#17a673", "#2c9faf", "#36b9cc", "#1cc88a", "#4e73df"]

# The two right selectable panels: (panel_id, default encoded value)
_SELECTABLE_PANELS = [
    ("panel4", "DISK::PERM"),
    ("panel5", "MEM::SGA"),
]


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


def _all_category_opts():
    rows = _run("""
        SELECT cat_name, cat_acronym, cat_yaxis_unit
          FROM sp_category
         WHERE is_active_fg = TRUE
         ORDER BY cat_name, cat_acronym
    """)
    return [
        {
            "label": r["cat_yaxis_unit"] or f"{r['cat_name']} / {r['cat_acronym']}",
            "value": f"{r['cat_name']}::{r['cat_acronym']}",
        }
        for r in rows
    ]


def _parse_cat_value(value):
    if value and "::" in value:
        cat_name, cat_acronym = value.split("::", 1)
        return cat_name, cat_acronym
    return value, None


def _cat_unit(cat_name, cat_acronym):
    rows = _run("""
        SELECT cat_yaxis_unit FROM sp_category
         WHERE cat_name = %s AND cat_acronym = %s AND is_active_fg = TRUE
         LIMIT 1
    """, (cat_name, cat_acronym))
    return rows[0]["cat_yaxis_unit"] if rows else ""


def _cat_color(cat_name):
    fixed = {m: c for m, _, _, c, _ in FIXED_CATEGORIES}
    if cat_name in fixed:
        return fixed[cat_name]
    return _PALETTE[hash(cat_name) % len(_PALETTE)]


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


def _metric_summary(coll_id, metric_name, cat_acronym=None):
    """
    Return (db_id, db_name, max_value, avg_value) per database, ordered by max descending.
    """
    acr_clause = "AND mp.mp_metricacronym = %s" if cat_acronym else ""
    params = [metric_name]
    if cat_acronym:
        params.append(cat_acronym)
    params.append(coll_id)

    return _run(f"""
        WITH per_instance AS (
            SELECT mp.sp_database_db_id,
                   mp.mp_metricacronym,
                   mp.mp_plotdate,
                   SUM(CAST(mp.mp_plotvalue AS NUMERIC)) AS inst_sum
              FROM sp_metricplot mp
             WHERE mp.mp_metricname = %s
               {acr_clause}
               AND mp.sp_database_db_id IN (
                   SELECT db_id FROM sp_database
                    WHERE sp_collection_coll_id = %s
               )
             GROUP BY mp.sp_database_db_id, mp.mp_metricacronym, mp.mp_plotdate
        ),
        per_snapshot AS (
            SELECT sp_database_db_id,
                   mp_plotdate,
                   SUM(inst_sum) AS combined
              FROM per_instance
             GROUP BY sp_database_db_id, mp_plotdate
        )
        SELECT db.db_id,
               db.db_name,
               CEIL(MAX(ps.combined))::BIGINT AS max_value,
               CEIL(AVG(ps.combined))::BIGINT AS avg_value
          FROM per_snapshot ps
          JOIN sp_database db ON db.db_id = ps.sp_database_db_id
         GROUP BY db.db_id, db.db_name
         ORDER BY max_value DESC
    """, params)


# ── Component builders ────────────────────────────────────────────────────────

_TABLE_FONT   = "0.72rem"
_ROW_H        = 26
_HEADER_H     = 34
_VISIBLE_ROWS = 10
_TABLE_MAX_H  = _HEADER_H + _ROW_H * _VISIBLE_ROWS


def _metric_table(rows, col_header, href_fn):
    """
    Compact scrollable table — 10 rows visible, sticky header.
    Each database name is a link built by href_fn(db_id).
    """
    thead = html.Thead(
        html.Tr([
            html.Th("Database",
                    style={"fontSize": _TABLE_FONT, "padding": "4px 6px", "width": "65%"}),
            html.Th(col_header,
                    className="text-end",
                    style={"fontSize": _TABLE_FONT, "padding": "4px 6px"}),
        ]),
        style={"position": "sticky", "top": 0, "backgroundColor": "#f8f9fa", "zIndex": 1},
    )

    cell_style = {"fontSize": _TABLE_FONT, "padding": "3px 6px"}

    tbody_rows = [
        html.Tr([
            html.Td(
                html.A(
                    r["db_name"],
                    href=href_fn(r["db_id"]),
                    title="Click to graph this database",
                    style={"textDecoration": "none", "color": "#2e59d9",
                           "overflow": "hidden", "textOverflow": "ellipsis",
                           "whiteSpace": "nowrap", "display": "block"},
                ),
                style={**cell_style, "fontWeight": "600",
                       "overflow": "hidden", "maxWidth": "0",
                       "maxHeight": f"{_ROW_H}px"},
            ),
            html.Td(f"{int(r['max_value'] or 0):,}",
                    className="text-end font-monospace",
                    style=cell_style),
        ])
        for r in rows
    ]

    return html.Div(
        dbc.Table(
            [thead, html.Tbody(tbody_rows)],
            bordered=False, striped=True, hover=True, size="sm", className="mb-0",
            style={"tableLayout": "fixed", "width": "100%"},
        ),
        style={
            "maxHeight": f"{_TABLE_MAX_H}px",
            "overflowY": "auto",
            "border": "1px solid #dee2e6",
            "borderRadius": "0.375rem",
        },
    )


def _avg_stat(rows, unit, color):
    if not rows:
        return html.Div()
    avg = sum(float(r["avg_value"] or 0) for r in rows) / len(rows)
    return html.Div([
        html.Span("Avg  ", style={"fontSize": "0.68rem", "color": "#718096",
                                   "textTransform": "uppercase", "fontWeight": "700",
                                   "letterSpacing": "0.04em"}),
        html.Span(f"{math.ceil(avg):,}", style={"fontSize": "1.05rem", "fontWeight": "800",
                                                 "color": color}),
        html.Span(f"  {unit}", style={"fontSize": "0.68rem", "color": "#718096"}),
    ], style={"marginTop": "0.5rem", "paddingLeft": "2px"})


def _table_and_avg(rows, unit, color, href_fn):
    if not rows:
        return html.Small("No data — run Workload Analysis first.", className="text-muted")
    return html.Div([
        _metric_table(rows, f"Peak ({unit})", href_fn),
        _avg_stat(rows, unit, color),
    ])


def _make_href(coll_id, cat_name, cat_acronym=None):
    """Return a function: db_id → /dbGraph URL with pre-selection params."""
    if cat_acronym:
        return lambda db_id: f"/dbGraph/{coll_id}/{db_id}/{cat_name}/{cat_acronym}"
    return lambda db_id: f"/dbGraph/{coll_id}/{db_id}/{cat_name}"


def _fixed_panel(metric, label, unit, color, icon, rows, coll_id):
    # CPU has a single acronym; MBPS/IOPS sum all — pass no acronym for the latter
    cat_acronym = metric if metric == "CPU" else None
    href_fn = _make_href(coll_id, metric, cat_acronym)
    return dbc.Card([
        dbc.CardHeader(
            html.Span([
                html.I(className=f"{icon} me-2", style={"color": color}),
                html.Strong(label),
            ], style={"fontSize": "0.8rem"}),
            style={"padding": "6px 12px", "borderLeft": f"4px solid {color}"},
        ),
        dbc.CardBody(
            _table_and_avg(rows, unit, color, href_fn),
            style={"padding": "10px 12px"},
        ),
    ], style={"borderRadius": "0.5rem", "boxShadow": "0 2px 6px rgba(0,0,0,0.07)",
              "height": "100%"})


def _selectable_panel(panel_id, default_value, rows, coll_id):
    cat_name, cat_acronym = _parse_cat_value(default_value)
    color   = _cat_color(cat_name)
    unit    = _cat_unit(cat_name, cat_acronym)
    href_fn = _make_href(coll_id, cat_name, cat_acronym)
    return dbc.Card([
        dbc.CardHeader(
            dcc.Dropdown(
                id=f"cs-{panel_id}-cat-dd",
                options=_all_category_opts(),
                value=default_value,
                clearable=False,
                style={"fontSize": _TABLE_FONT, "border": "none",
                       "boxShadow": "none", "padding": 0},
            ),
            style={"padding": "4px 8px", "borderLeft": f"4px solid {color}",
                   "backgroundColor": "#f8f9fa"},
        ),
        dbc.CardBody(
            html.Div(_table_and_avg(rows, unit, color, href_fn), id=f"cs-{panel_id}-content"),
            style={"padding": "10px 12px"},
        ),
    ], style={"borderRadius": "0.5rem", "boxShadow": "0 2px 6px rgba(0,0,0,0.07)",
              "height": "100%"})


def _no_data_alert():
    return dbc.Alert(
        [html.I(className="fas fa-exclamation-triangle me-2"),
         "No metric data found for this collection. "
         "Run Workload Analysis first to generate metrics."],
        color="warning", className="mt-3",
    )


# ── Page layout ───────────────────────────────────────────────────────────────

def generate_collection_summary_page():
    return html.Div([
        html.H2("Collection Summary"),
        html.Hr(className="mb-4"),

        # Persists the last selected collection across navigations
        dcc.Store(id="cs-last-collection", storage_type="local"),

        # Fires once on page load to restore the last selection
        dcc.Interval(id="cs-restore-once", interval=50, n_intervals=0, max_intervals=1),

        dbc.Card([
            dbc.CardHeader(html.Span("Select Collection", className="fw-semibold")),
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Collection", className="fw-semibold"),
                        dcc.Dropdown(
                            id="cs-collection-dd",
                            options=_collection_opts(),
                            placeholder="Select a collection…",
                            clearable=True,
                        ),
                    ], width=7),
                ], className="g-3"),
            ),
        ], className="mb-4"),

        html.Div(id="cs-output"),
    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_callbacks(app):

    # Restore last selection on page load — reads store as State (no dependency edge)
    @app.callback(
        Output("cs-collection-dd",  "value"),
        Input("cs-restore-once",    "n_intervals"),
        State("cs-last-collection", "data"),
    )
    def _restore_collection(_, stored):
        return stored  # None on first visit, last value thereafter

    @app.callback(
        Output("cs-output",           "children"),
        Output("cs-last-collection",  "data"),
        Input("cs-collection-dd",     "value"),
        prevent_initial_call=True,
    )
    def _on_collection(coll_id):
        if not coll_id:
            return no_update, no_update

        fixed_metrics = [m for m, *_ in FIXED_CATEGORIES]
        datasets = {m: _metric_summary(coll_id, m) for m in fixed_metrics}

        sel_datasets = {}
        for panel_id, default_value in _SELECTABLE_PANELS:
            cat_name, cat_acronym = _parse_cat_value(default_value)
            sel_datasets[panel_id] = _metric_summary(coll_id, cat_name, cat_acronym)

        if not any(datasets.values()) and not any(sel_datasets.values()):
            return _no_data_alert()

        fixed_cols = [
            dbc.Col(
                _fixed_panel(metric, label, unit, color, icon, datasets[metric], coll_id),
                xs=12, sm=6, lg=4, xl=True, className="mb-3",
            )
            for metric, label, unit, color, icon in FIXED_CATEGORIES
        ]

        selectable_cols = [
            dbc.Col(
                _selectable_panel(panel_id, default_value, sel_datasets[panel_id], coll_id),
                xs=12, sm=6, lg=4, xl=True, className="mb-3",
            )
            for panel_id, default_value in _SELECTABLE_PANELS
        ]

        link_bar = dbc.Row(
            dbc.Col(
                dcc.Link(
                    dbc.Button(
                        [html.I(className="fas fa-chart-line me-2"), "Analyze Databases →"],
                        color="primary", outline=True, size="sm",
                    ),
                    href=f"/dbGraph/{coll_id}",
                ),
                className="text-end mb-3",
            )
        )

        return html.Div([link_bar, dbc.Row(fixed_cols + selectable_cols, className="g-3")]), coll_id

    # Right panel callbacks
    for panel_id, _ in _SELECTABLE_PANELS:

        def _make_callback(pid):
            @app.callback(
                Output(f"cs-{pid}-content", "children"),
                Input(f"cs-{pid}-cat-dd",   "value"),
                State("cs-collection-dd",   "value"),
                prevent_initial_call=True,
            )
            def _on_cat_change(value, coll_id, _pid=pid):
                if not coll_id or not value:
                    return no_update
                cat_name, cat_acronym = _parse_cat_value(value)
                unit    = _cat_unit(cat_name, cat_acronym)
                color   = _cat_color(cat_name)
                rows    = _metric_summary(coll_id, cat_name, cat_acronym)
                href_fn = _make_href(coll_id, cat_name, cat_acronym)
                return _table_and_avg(rows, unit, color, href_fn)

        _make_callback(panel_id)
