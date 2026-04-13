"""
Assessment screen — AI-generated workload assessment and sizing recommendation.

Flow:
  1. Select a collection  →  database dropdown populated (metrics-only).
  2. Select a database    →  Generate button enabled.
  3. Click Generate       →  Fetch metric aggregates from sp_metricplot,
                             call Claude API, render narrative assessment.

The Claude prompt receives:
  - Database identity info from sp_dbidentity (db version, host, platform)
  - Per-category peak / average values from sp_metricplot
  - AWR collection date range

Claude returns a structured assessment covering:
  - Workload characterisation (OLTP / batch / mixed)
  - Resource pressure analysis (CPU, memory, I/O)
  - Sizing recommendation for a target platform
  - Risk / migration considerations
"""

import os
import anthropic

from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc

from pyespUtil import connect_postgres_db


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


def _database_opts(coll_id):
    """Only databases that have had metrics generated."""
    rows = _run("""
        SELECT db_id, db_name
          FROM sp_database
         WHERE sp_collection_coll_id = %s
           AND db_metrics_date IS NOT NULL
         ORDER BY db_name
    """, (coll_id,))
    return [{"label": r["db_name"], "value": r["db_id"]} for r in rows]


def _fetch_identity(db_id):
    """Return identity key/value pairs for the database (version, platform, etc.)."""
    return _run("""
        SELECT iden_metric, iden_metricvalue
          FROM sp_dbidentity
         WHERE sp_database_db_id = %s
         ORDER BY iden_metric
    """, (db_id,))


def _fetch_metric_aggregates(db_id):
    """
    Per-category peak and average from sp_metricplot, summed across RAC instances
    per snapshot, then aggregated.
    """
    return _run("""
        SELECT mp_metricname                              AS metric,
               mp_metricacronym                          AS acronym,
               cat_yaxis_unit                            AS unit,
               ROUND(AVG(CAST(mp_plotvalue AS NUMERIC))::NUMERIC, 3) AS avg_value,
               ROUND(MAX(CAST(mp_plotvalue AS NUMERIC))::NUMERIC, 3) AS peak_value,
               MIN(mp_plotdate)                          AS date_from,
               MAX(mp_plotdate)                          AS date_to
          FROM sp_metricplot mp
          LEFT JOIN sp_category sc
                 ON sc.cat_name    = mp.mp_metricname
                AND sc.cat_acronym = mp.mp_metricacronym
                AND sc.is_active_fg = TRUE
         WHERE mp.sp_database_db_id = %s
         GROUP BY mp_metricname, mp_metricacronym, cat_yaxis_unit
         ORDER BY mp_metricname, mp_metricacronym
    """, (db_id,))


def _fetch_db_info(db_id):
    """Return basic database record (name, host, cpu, model)."""
    rows = _run("""
        SELECT db_name, db_collection_host, db_host_cpu, db_host_model,
               db_fileread_date
          FROM sp_database
         WHERE db_id = %s
    """, (db_id,))
    return rows[0] if rows else {}


# ── Claude API call ───────────────────────────────────────────────────────────

def _build_prompt(db_info: dict, identity: list, metrics: list) -> str:
    """Compose the user message sent to Claude."""

    identity_block = "\n".join(
        f"  {r['iden_metric']}: {r['iden_metricvalue']}"
        for r in identity
    ) or "  (no identity data available)"

    metrics_block = "\n".join(
        "  {metric} / {acronym} — avg: {avg_value} {unit}, peak: {peak_value} {unit}  "
        "({date_from} → {date_to})".format(
            metric=r["metric"],
            acronym=r["acronym"],
            unit=r["unit"] or "",
            avg_value=r["avg_value"],
            peak_value=r["peak_value"],
            date_from=str(r["date_from"])[:16] if r["date_from"] else "?",
            date_to=str(r["date_to"])[:16] if r["date_to"] else "?",
        )
        for r in metrics
    ) or "  (no metric plot data available)"

    return f"""You are an Oracle database performance and sizing expert at Accenture Enkitec Group (AEG).

You have been given AWR workload data for a production Oracle database. Produce a concise but complete assessment covering the four sections below. Use plain prose — no bullet-point lists, no markdown headings. Write as if this will be pasted directly into a client-facing PDF report.

DATABASE INFORMATION
--------------------
Name            : {db_info.get('db_name', 'unknown')}
Collection host : {db_info.get('db_collection_host', 'unknown')}
Host CPU        : {db_info.get('db_host_cpu', 'unknown')}
Host model      : {db_info.get('db_host_model', 'unknown')}
Collection date : {str(db_info.get('db_fileread_date', 'unknown'))[:10]}

DATABASE IDENTITY METRICS
--------------------------
{identity_block}

WORKLOAD METRICS (avg and peak over the collection window)
-----------------------------------------------------------
{metrics_block}

REQUIRED SECTIONS IN YOUR RESPONSE
------------------------------------
1. Workload Characterisation — describe the workload type (OLTP, batch, mixed, read-heavy, write-heavy) and its dominant patterns based on the metrics above.

2. Resource Pressure Analysis — identify which resources (CPU, memory/buffer cache, physical I/O, redo/log) are under the most pressure, citing the specific avg and peak values that support your conclusions.

3. Sizing Recommendation — recommend a target platform (on-premises server class, Oracle Exadata model, or equivalent cloud shape) sized to handle the observed peak workload with headroom. State the recommended CPU count, memory, and storage I/O in concrete terms.

4. Migration Considerations — note any risks, data points that require further investigation, or collection gaps that limit the confidence of this assessment.
"""


def call_claude_assessment(db_id: int) -> tuple[str, str]:
    """
    Fetch data for db_id, call Claude, return (db_name, assessment_text).
    Raises on API or DB errors so the caller can surface them in the UI.
    """
    db_info  = _fetch_db_info(db_id)
    identity = _fetch_identity(db_id)
    metrics  = _fetch_metric_aggregates(db_id)

    prompt = _build_prompt(db_info, identity, metrics)

    client   = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY from env
    message  = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    assessment_text = message.content[0].text
    return db_info.get("db_name", str(db_id)), assessment_text


# ── Page layout ───────────────────────────────────────────────────────────────

def generate_assessment_page():
    return html.Div([
        html.H2("Assessment"),
        html.Hr(className="mb-4"),

        dbc.Card([
            dbc.CardHeader(html.Span("Select Database", className="fw-semibold")),
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Collection", className="fw-semibold"),
                        dcc.Dropdown(
                            id="as-collection-dd",
                            options=_collection_opts(),
                            placeholder="Select a collection…",
                            clearable=True,
                        ),
                    ], width=5),
                    dbc.Col([
                        dbc.Label("Database", className="fw-semibold"),
                        dcc.Dropdown(
                            id="as-database-dd",
                            options=[],
                            placeholder="Select a database…",
                            clearable=True,
                            disabled=True,
                        ),
                        html.Small(
                            "Only databases with metrics generated are available.",
                            className="text-muted",
                        ),
                    ], width=5),
                ], className="g-3"),
            ),
        ], className="mb-4"),

        dbc.Row(
            dbc.Col(
                dbc.Button(
                    [html.I(className="fas fa-brain me-2"), "Generate Assessment"],
                    id="as-generate-btn",
                    color="primary",
                    size="lg",
                    disabled=True,
                ),
                className="text-center",
            ),
            className="mb-4",
        ),

        html.Div(id="as-output"),
    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_callbacks(app):

    @app.callback(
        Output("as-database-dd", "options"),
        Output("as-database-dd", "value"),
        Output("as-database-dd", "disabled"),
        Input("as-collection-dd", "value"),
        prevent_initial_call=True,
    )
    def _on_collection(coll_id):
        if not coll_id:
            return [], None, True
        opts = _database_opts(coll_id)
        return opts, None, len(opts) == 0

    @app.callback(
        Output("as-generate-btn", "disabled"),
        Input("as-database-dd", "value"),
    )
    def _toggle_btn(db_id):
        return not db_id

    @app.callback(
        Output("as-output",       "children"),
        Output("as-generate-btn", "disabled", allow_duplicate=True),
        Input("as-generate-btn",  "n_clicks"),
        State("as-database-dd",   "value"),
        prevent_initial_call=True,
    )
    def _generate(_, db_id):
        if not db_id:
            return no_update, False

        try:
            db_name, text = call_claude_assessment(int(db_id))
        except Exception as exc:
            return (
                dbc.Alert(
                    [html.I(className="fas fa-exclamation-triangle me-2"),
                     f"Assessment failed: {exc}"],
                    color="danger",
                ),
                False,
            )

        # Split the response into the four numbered sections for display
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        return (
            dbc.Card([
                dbc.CardHeader(
                    html.Strong(f"Workload Assessment — {db_name}"),
                    className="bg-primary text-white",
                ),
                dbc.CardBody([
                    html.P(para, className="mb-3") for para in paragraphs
                ]),
            ], className="mt-2"),
            False,
        )
