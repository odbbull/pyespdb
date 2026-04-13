"""
Workload Analysis screen — generate metric plots for a selected database
from its raw sp_dbmetric records, driven by sp_category definitions.

Replicates the logic of AcmeESP/aaGenMetrics.py, adapted for the
PostgreSQL backend (psycopg2) and the Dash application framework.

Process (per database):
  1. Load all active categories from sp_category.
  2. Clear any existing sp_metricplot rows for that database.
  3. For each category:
       • Static  (is_static_fg=True)  — use raw metric value directly.
       • Dynamic (is_static_fg=False) — compute delta between consecutive
         cumulative-counter rows, resetting per RAC instance.
     Apply add_interval_fg and cat_yaxis_divisor scaling, then INSERT
     the resulting plot values into sp_metricplot.
  4. Stamp db_metrics_date on sp_database so the UI can track which
     databases have already been processed.

Collection status bar:
  When a collection is selected the progress bar appears immediately,
  spanning 0 → total databases in the collection.  The filled portion
  shows how many databases already have metrics generated
  (db_metrics_date IS NOT NULL).  During generation the bar updates live
  via a background thread + 500 ms dcc.Interval poll.  The bar remains
  visible after generation is complete, reflecting the new state.
"""

import threading

from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc

from pyespUtil import connect_postgres_db


# ── Module-level progress state ─────────────────────────────────────────────────

_lock  = threading.Lock()
_state = {
    "running":           False,
    "current":           0,      # databases completed in this run
    "total_in_coll":     0,      # total databases in the collection
    "initial_processed": 0,      # databases already processed before this run
    "results":           [],
    "coll_id":           None,
}

_ALL_VALUE = "__all__"   # sentinel value used in the database dropdown


# ── DB helpers ──────────────────────────────────────────────────────────────────

def _run(sql, params=None, fetch=False):
    """Execute a query; commit on write, return rows on fetch."""
    conn = connect_postgres_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if fetch:
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        conn.commit()
    except Exception:
        if not fetch:
            conn.rollback()
        raise
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
    """, fetch=True)
    return [{"label": r["label"], "value": r["coll_id"]} for r in rows]


def _collection_status(coll_id):
    """
    Return (total, processed) for a collection.
    total     = total number of databases
    processed = number with db_metrics_date IS NOT NULL
    COUNT(col) ignores NULLs, so COUNT(db_metrics_date) gives processed count.
    """
    rows = _run("""
        SELECT COUNT(*)                AS total,
               COUNT(db_metrics_date) AS processed
          FROM sp_database
         WHERE sp_collection_coll_id = %s
    """, (coll_id,), fetch=True)
    if rows:
        return int(rows[0]["total"]), int(rows[0]["processed"])
    return 0, 0


def _bar_props(total: int, processed: int, running: bool = False) -> tuple:
    """
    Derive (bar_label, bar_color, status_text) from collection counts.
    bar_label   — text rendered inside the dbc.Progress bar
    bar_color   — Bootstrap colour name for the bar
    status_text — descriptive text shown above the bar
    """
    db_word = "database" if total == 1 else "databases"
    bar_label = f"{processed} of {total}"

    if running:
        bar_color   = "primary"
        status_text = f"Processing\u2026  {processed} of {total} {db_word} processed"
    elif total > 0 and processed >= total:
        bar_color   = "success"
        status_text = f"\u2713 All {total} {db_word} processed"
    else:
        bar_color   = "primary"
        status_text = f"{processed} of {total} {db_word} processed"

    return bar_label, bar_color, status_text


def _database_opts(coll_id):
    """
    Return dropdown options for all databases in a collection.
    Prepends an "All Databases" sentinel.  Each label shows a checkmark
    and the last-generated date when db_metrics_date is set.
    """
    rows = _run("""
        SELECT db_id, db_name, db_metrics_date
          FROM sp_database
         WHERE sp_collection_coll_id = %s
         ORDER BY db_name
    """, (coll_id,), fetch=True)

    opts = [{"label": "\u2500\u2500 All Databases \u2500\u2500", "value": _ALL_VALUE}]
    for r in rows:
        if r["db_metrics_date"]:
            date_str = str(r["db_metrics_date"])[:10]
            label = f"{r['db_name']}  \u2713 {date_str}"
        else:
            label = r["db_name"]
        opts.append({"label": label, "value": r["db_id"]})
    return opts


def _databases_for_collection(coll_id):
    return _run("""
        SELECT db_id, db_name
          FROM sp_database
         WHERE sp_collection_coll_id = %s
         ORDER BY db_name
    """, (coll_id,), fetch=True)


def _active_categories():
    return _run("""
        SELECT cat_name, cat_acronym, is_static_fg, add_interval_fg,
               cat_yaxis_unit, cat_yaxis_divisor
          FROM sp_category
         WHERE is_active_fg = TRUE
         ORDER BY cat_name, cat_acronym
    """, fetch=True)


# ── Core metric generation ──────────────────────────────────────────────────────

def _clear_metricplot(conn, db_id):
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM sp_metricplot WHERE sp_database_db_id = %s", (db_id,)
    )
    conn.commit()
    cur.close()


def _stamp_metrics_date(db_id):
    _run(
        "UPDATE sp_database SET db_metrics_date = NOW() WHERE db_id = %s",
        (db_id,),
    )


def _load_static_metric(conn, db_id, cat_name, cat_acronym,
                         add_interval, divisor, awr_interval):
    cur = conn.cursor()
    cur.execute("""
        SELECT metr_instance, metr_metricdate, metr_metricvalue
          FROM sp_dbmetric
         WHERE sp_database_db_id = %s
           AND metr_metric  = %s
           AND metr_acronym = %s
         ORDER BY metr_instance, metr_metricdate
    """, (db_id, cat_name, cat_acronym))

    ins_count = 0
    for instance, metric_date, raw in cur.fetchall():
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        plot_value = value / awr_interval if add_interval else value
        plot_value = plot_value / float(divisor)
        cur.execute("""
            INSERT INTO sp_metricplot
              (mp_metricname, mp_metricacronym, mp_instance,
               mp_plotdate, mp_plotvalue, sp_database_db_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (cat_name, cat_acronym, instance,
              metric_date, f'{plot_value:.3f}', db_id))
        ins_count += 1

    conn.commit()
    cur.close()
    return ins_count


def _load_dynamic_metric(conn, db_id, cat_name, cat_acronym,
                          add_interval, divisor, awr_interval):
    cur = conn.cursor()
    cur.execute("""
        SELECT metr_instance, metr_metricdate, metr_metricvalue
          FROM sp_dbmetric
         WHERE sp_database_db_id = %s
           AND metr_metric  = %s
           AND metr_acronym = %s
         ORDER BY metr_instance, metr_metricdate
    """, (db_id, cat_name, cat_acronym))

    active_instance = None
    prev_value      = None
    ins_count       = 0

    for instance, metric_date, raw in cur.fetchall():
        try:
            current = float(raw)
        except (TypeError, ValueError):
            continue
        if instance != active_instance:
            prev_value      = None
            active_instance = instance
        if prev_value is not None:
            delta = current - prev_value if current > prev_value else 0.0
            plot_value = delta / awr_interval if add_interval else delta
            plot_value = plot_value / float(divisor)
            cur.execute("""
                INSERT INTO sp_metricplot
                  (mp_metricname, mp_metricacronym, mp_instance,
                   mp_plotdate, mp_plotvalue, sp_database_db_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (cat_name, cat_acronym, instance,
                  metric_date, f'{plot_value:.3f}', db_id))
            ins_count += 1
        prev_value = current

    conn.commit()
    cur.close()
    return ins_count


def generate_metrics(db_id: int, awr_interval: int = 3600) -> dict:
    results = {
        "db_id":                db_id,
        "db_name":              str(db_id),
        "awr_interval":         awr_interval,
        "categories_processed": 0,
        "plots_generated":      0,
        "errors":               [],
        "success":              False,
    }

    conn = connect_postgres_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT db_name FROM sp_database WHERE db_id = %s", (db_id,))
        row = cur.fetchone()
        if row:
            results["db_name"] = row[0]
        cur.close()

        categories = _active_categories()
        _clear_metricplot(conn, db_id)

        for cat in categories:
            cat_name     = cat["cat_name"]
            cat_acronym  = cat["cat_acronym"]
            is_static    = cat["is_static_fg"]
            add_interval = cat["add_interval_fg"]
            divisor      = float(cat["cat_yaxis_divisor"] or 1)
            try:
                if is_static:
                    n = _load_static_metric(
                        conn, db_id, cat_name, cat_acronym,
                        add_interval, divisor, awr_interval,
                    )
                else:
                    n = _load_dynamic_metric(
                        conn, db_id, cat_name, cat_acronym,
                        add_interval, divisor, awr_interval,
                    )
                results["plots_generated"]      += n
                results["categories_processed"] += 1
            except Exception as exc:
                results["errors"].append(f"{cat_name}/{cat_acronym}: {exc}")

        results["success"] = True

    except Exception as exc:
        results["errors"].append(str(exc))
    finally:
        conn.close()

    if results["success"]:
        _stamp_metrics_date(db_id)

    return results


# ── Background runner ───────────────────────────────────────────────────────────

def _run_in_background(db_list: list, awr_interval: int, coll_id: int):
    """
    Process each database sequentially, updating _state so the polling
    callback can reflect live progress in the collection status bar.
    Queries the initial processed count before starting so the bar value
    advances correctly from the pre-existing baseline.
    """
    total, initial_processed = _collection_status(coll_id)

    with _lock:
        _state.update({
            "running":           True,
            "current":           0,
            "total_in_coll":     total,
            "initial_processed": initial_processed,
            "results":           [],
            "coll_id":           coll_id,
        })
    try:
        for db in db_list:
            r = generate_metrics(db["db_id"], awr_interval)
            with _lock:
                _state["results"].append(r)
                _state["current"] += 1
    finally:
        with _lock:
            _state["running"] = False


# ── Results panels ──────────────────────────────────────────────────────────────

def _results_panel(r: dict) -> dbc.Card:
    color = "success" if r["success"] else "danger"
    icon  = "fas fa-check-circle" if r["success"] else "fas fa-times-circle"
    title = (f"\u2713 {r['db_name']} \u2014 metrics generated successfully"
             if r["success"]
             else f"\u2717 {r['db_name']} \u2014 generation failed")

    table = dbc.Table(
        html.Tbody([
            html.Tr([html.Th(k, style={"width": "45%"}), html.Td(v)])
            for k, v in [
                ("Database",             r["db_name"]),
                ("AWR Interval",         f"{r['awr_interval']:,} seconds"),
                ("Categories Processed", str(r["categories_processed"])),
                ("Plot Records Created", f"{r['plots_generated']:,}"),
            ]
        ]),
        bordered=False, size="sm", className="mb-0",
    )
    error_section = []
    if r["errors"]:
        error_section = [
            html.Hr(),
            html.H6("Errors", className="text-danger"),
            html.Ul([html.Li(e) for e in r["errors"]], className="mb-0"),
        ]
    return dbc.Card([
        dbc.CardHeader(
            [html.I(className=f"{icon} me-2"), title],
            className=f"bg-{color} text-white fw-semibold",
        ),
        dbc.CardBody([table, *error_section]),
    ], className="mt-3")


def _multi_results_panel(results_list: list) -> dbc.Card:
    total_plots = sum(r["plots_generated"] for r in results_list)
    error_count = sum(len(r["errors"])     for r in results_list)
    all_ok      = error_count == 0
    header_color = "success" if all_ok else "warning"
    header_icon  = "fas fa-check-circle" if all_ok else "fas fa-exclamation-triangle"
    header_title = (
        f"All databases processed \u2014 {total_plots:,} total plot records created"
        if all_ok
        else f"Completed with {error_count} error(s) \u2014 {total_plots:,} plot records created"
    )

    def _badge(r):
        if r["success"] and not r["errors"]:
            return dbc.Badge("\u2713", color="success", pill=True)
        if r["success"] and r["errors"]:
            return dbc.Badge("!", color="warning", pill=True)
        return dbc.Badge("\u2717", color="danger", pill=True)

    return dbc.Card([
        dbc.CardHeader(
            [html.I(className=f"{header_icon} me-2"), header_title],
            className=f"bg-{header_color} text-white fw-semibold",
        ),
        dbc.CardBody(
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Database"),
                    html.Th("Plots",      className="text-end"),
                    html.Th("Categories", className="text-end"),
                    html.Th("Errors"),
                    html.Th("Status",     className="text-center"),
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(r["db_name"], className="fw-semibold"),
                        html.Td(f"{r['plots_generated']:,}", className="text-end"),
                        html.Td(str(r["categories_processed"]), className="text-end"),
                        html.Td(
                            "; ".join(r["errors"]) if r["errors"] else "\u2014",
                            className="text-danger" if r["errors"] else "",
                        ),
                        html.Td(_badge(r), className="text-center"),
                    ])
                    for r in results_list
                ]),
            ], striped=True, bordered=True, hover=True, responsive=True,
               size="sm", className="mb-0"),
        ),
    ], className="mt-3")


# ── Page layout ─────────────────────────────────────────────────────────────────

def generate_workload_analysis_page():
    return html.Div([
        html.H2("Workload Analysis"),
        html.Hr(className="mb-4"),

        # ── Step 1: select collection ─────────────────────────────────────────
        dbc.Card([
            dbc.CardHeader(
                html.Span([
                    dbc.Badge("1", color="primary", className="me-2"),
                    "Select Collection",
                ], className="fw-semibold")
            ),
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Collection", className="fw-semibold"),
                        dcc.Dropdown(
                            id="wa-collection-dd",
                            options=_collection_opts(),
                            placeholder="Select a collection…",
                            clearable=True,
                        ),
                    ], width=8),
                ], className="g-3"),
            ),
        ], className="mb-3"),

        # ── Collection status bar (appears on collection select) ───────────────
        html.Div(
            id="wa-progress-section",
            style={"display": "none"},
            children=[
                html.Div(
                    id="wa-progress-label",
                    className="text-muted fw-semibold mb-2",
                    style={"fontSize": "0.85rem"},
                ),
                dbc.Progress(
                    id="wa-progress-bar",
                    value=0,
                    max=1,
                    label="",
                    striped=False,
                    animated=False,
                    color="primary",
                    style={"height": "28px", "fontSize": "0.85rem"},
                    className="mb-4",
                ),
            ],
        ),

        # ── Step 2: select database + AWR interval ────────────────────────────
        dbc.Card([
            dbc.CardHeader(
                html.Span([
                    dbc.Badge("2", color="primary", className="me-2"),
                    "Select Database & Interval",
                ], className="fw-semibold")
            ),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Database", className="fw-semibold"),
                        dcc.Dropdown(
                            id="wa-database-dd",
                            options=[],
                            placeholder="Select a database…",
                            clearable=True,
                            disabled=True,
                        ),
                        html.Small(
                            "\u2713 = metrics already generated   |   "
                            "\u2500\u2500 All Databases \u2500\u2500 = process entire collection",
                            className="text-muted",
                        ),
                    ], width=6),
                    dbc.Col([
                        dbc.Label("AWR Interval (seconds)", className="fw-semibold"),
                        dbc.Input(
                            id="wa-awr-interval",
                            type="number",
                            value=3600,
                            min=1,
                            placeholder="3600",
                        ),
                    ], width=3),
                ], className="g-3"),
            ]),
        ], className="mb-4"),

        # ── Step 3: generate ──────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    [html.I(className="fas fa-chart-line me-2"), "Generate Metrics"],
                    id="wa-generate-btn",
                    color="primary",
                    size="lg",
                    disabled=True,
                ),
                className="text-center",
            ),
            className="mb-4",
        ),

        # Interval drives polling; starts disabled
        dcc.Interval(
            id="wa-interval",
            interval=500,
            n_intervals=0,
            disabled=True,
        ),

        # ── Results ───────────────────────────────────────────────────────────
        html.Div(id="wa-results"),
    ])


# ── Callbacks ───────────────────────────────────────────────────────────────────

def register_callbacks(app):

    # ── Collection selected: populate database dropdown + show status bar ─────
    #    This callback is the PRIMARY owner of all progress bar properties.
    @app.callback(
        Output("wa-database-dd",      "options"),
        Output("wa-database-dd",      "value"),
        Output("wa-database-dd",      "disabled"),
        Output("wa-progress-section", "style"),
        Output("wa-progress-bar",     "value"),
        Output("wa-progress-bar",     "max"),
        Output("wa-progress-bar",     "label"),
        Output("wa-progress-bar",     "color"),
        Output("wa-progress-bar",     "animated"),
        Output("wa-progress-label",   "children"),
        Input("wa-collection-dd",     "value"),
        prevent_initial_call=True,
    )
    def _update_databases(coll_id):
        if not coll_id:
            return [], None, True, {"display": "none"}, 0, 1, "", "primary", False, ""

        total, processed = _collection_status(coll_id)
        bar_label, bar_color, status_text = _bar_props(total, processed)

        return (
            _database_opts(coll_id),
            None,
            False,
            {"display": "block"},
            processed,
            max(total, 1),       # guard against division-by-zero in the bar
            bar_label,
            bar_color,
            False,
            status_text,
        )

    # ── Enable / disable the Generate button ──────────────────────────────────
    @app.callback(
        Output("wa-generate-btn", "disabled"),
        Input("wa-database-dd",   "value"),
        Input("wa-collection-dd", "value"),
    )
    def _toggle_generate_btn(db_id, coll_id):
        return not (db_id and coll_id)

    # ── Button click: animate bar, launch background thread ──────────────────
    @app.callback(
        Output("wa-progress-bar",  "animated",  allow_duplicate=True),
        Output("wa-progress-label","children",  allow_duplicate=True),
        Output("wa-interval",      "disabled"),
        Output("wa-generate-btn",  "disabled",  allow_duplicate=True),
        Output("wa-results",       "children"),
        Input("wa-generate-btn",   "n_clicks"),
        State("wa-database-dd",    "value"),
        State("wa-awr-interval",   "value"),
        State("wa-collection-dd",  "value"),
        prevent_initial_call=True,
    )
    def _start_generation(_, db_id, awr_interval, coll_id):
        if not db_id or not coll_id:
            return no_update, no_update, no_update, no_update, no_update

        interval = int(awr_interval) if awr_interval and int(awr_interval) > 0 else 3600

        if db_id == _ALL_VALUE:
            dbs = _databases_for_collection(coll_id)
        else:
            dbs = _run(
                "SELECT db_id, db_name FROM sp_database WHERE db_id = %s",
                (int(db_id),), fetch=True,
            )

        if not dbs:
            return False, "No databases found.", True, False, no_update

        total, processed = _collection_status(coll_id)
        db_word = "database" if total == 1 else "databases"
        status_text = f"Processing\u2026  {processed} of {total} {db_word} processed"

        threading.Thread(
            target=_run_in_background,
            args=(dbs, interval, coll_id),
            daemon=True,
        ).start()

        return (
            True,          # start bar animation
            status_text,   # update label above bar
            False,         # enable interval
            True,          # disable button while running
            [],            # clear previous results
        )

    # ── Interval: poll _state, update bar, render results when done ───────────
    @app.callback(
        Output("wa-progress-bar",  "value",    allow_duplicate=True),
        Output("wa-progress-bar",  "label",    allow_duplicate=True),
        Output("wa-progress-bar",  "animated", allow_duplicate=True),
        Output("wa-progress-bar",  "color",    allow_duplicate=True),
        Output("wa-progress-label","children", allow_duplicate=True),
        Output("wa-interval",      "disabled", allow_duplicate=True),
        Output("wa-results",       "children", allow_duplicate=True),
        Output("wa-database-dd",   "options",  allow_duplicate=True),
        Output("wa-generate-btn",  "disabled", allow_duplicate=True),
        Input("wa-interval",       "n_intervals"),
        State("wa-collection-dd",  "value"),
        prevent_initial_call=True,
    )
    def _poll_progress(_, coll_id):
        with _lock:
            running          = _state["running"]
            current          = _state["current"]
            total            = _state["total_in_coll"]
            initial_proc     = _state["initial_processed"]
            results          = list(_state["results"])

        now_processed = initial_proc + current
        bar_label, bar_color, status_text = _bar_props(total, now_processed, running=running)

        if running:
            return (
                now_processed, bar_label, True, "primary",
                status_text, False,
                no_update, no_update, no_update,
            )

        # ── Generation complete ───────────────────────────────────────────────
        # Re-query for accuracy (some databases may have failed)
        if coll_id:
            total, now_processed = _collection_status(coll_id)
        bar_label, bar_color, status_text = _bar_props(total, now_processed)

        panel    = (_results_panel(results[0])    if len(results) == 1
                    else _multi_results_panel(results) if results
                    else [])
        new_opts = _database_opts(coll_id) if coll_id else no_update

        return (
            now_processed,   # final bar value (from live DB count)
            bar_label,
            False,           # stop animation
            bar_color,       # green if all done, blue otherwise
            status_text,
            True,            # disable interval
            panel,
            new_opts,        # refresh dropdown ✓ labels
            False,           # re-enable button
        )
