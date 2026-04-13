"""
Collection Bubble Plot — shows all databases in a collection plotted as bubbles.

  X axis : Total MBPS (sum of max read + write + redo MBPS)
  Y axis : Total Database Size in GB (sum of max DISK values across LOG/PERM/TEMP/UNDO)
  Bubble : sized by max CPU sessions

Navigate here from the home-page "Databases per Collection" bar chart by
clicking on any collection bar.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from pyespUtil import connect_postgres_db


# ── DB helpers ───────────────────────────────────────────────────────────────

def _get_collection_info(coll_id):
    """Return (coll_name, cl_name, pr_name) or None."""
    conn = connect_postgres_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT co.coll_name, c.cl_name, p.pr_name
          FROM sp_collection co
          JOIN sp_project p ON p.pr_id = co.sp_project_pr_id
          JOIN sp_client  c ON c.cl_id = p.sp_client_cl_id
         WHERE co.coll_id = %s
    """, (coll_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def _get_bubble_data(coll_id):
    """
    For every database in the collection return:
      db_name, total_disk_gb, total_mbps, max_cpu
    Only databases that have metrics generated (db_metrics_date IS NOT NULL)
    are included; databases with no metric rows are still returned with 0 values.
    """
    conn = connect_postgres_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            db.db_id,
            db.db_name,
            COALESCE((
                SELECT SUM(max_val)
                  FROM (
                      SELECT MAX(CAST(mp_plotvalue AS NUMERIC)) AS max_val
                        FROM sp_metricplot
                       WHERE sp_database_db_id = db.db_id
                         AND mp_metricname = 'DISK'
                       GROUP BY mp_metricacronym
                  ) disk_sub
            ), 0) AS total_disk_gb,
            COALESCE((
                SELECT SUM(max_val)
                  FROM (
                      SELECT MAX(CAST(mp_plotvalue AS NUMERIC)) AS max_val
                        FROM sp_metricplot
                       WHERE sp_database_db_id = db.db_id
                         AND mp_metricname = 'MBPS'
                       GROUP BY mp_metricacronym
                  ) mbps_sub
            ), 0) AS total_mbps,
            COALESCE((
                SELECT MAX(CAST(mp_plotvalue AS NUMERIC))
                  FROM sp_metricplot
                 WHERE sp_database_db_id = db.db_id
                   AND mp_metricname = 'CPU'
                   AND mp_metricacronym = 'CPU'
            ), 0) AS max_cpu
          FROM sp_database db
         WHERE db.sp_collection_coll_id = %s
         ORDER BY db.db_name
    """, (coll_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "db_id":        int(r[0]),
            "db_name":      r[1],
            "total_disk_gb": float(r[2] or 0),
            "total_mbps":   float(r[3] or 0),
            "max_cpu":      float(r[4] or 0),
        }
        for r in rows
    ]


# ── Page builder ─────────────────────────────────────────────────────────────

def generate_collection_bubble_page(coll_id):
    try:
        coll_id = int(coll_id)
    except (TypeError, ValueError):
        return html.Div([
            html.H2("Invalid collection"),
            html.P(f"Collection ID '{coll_id}' is not valid."),
        ])

    info = _get_collection_info(coll_id)
    if not info:
        return html.Div([
            html.H2("Collection not found"),
            html.P(f"No collection with ID {coll_id} was found."),
        ])

    coll_name, cl_name, pr_name = info
    data = _get_bubble_data(coll_id)

    has_data = data and any(d["total_disk_gb"] > 0 or d["total_mbps"] > 0 for d in data)

    if has_data:
        x_vals    = [d["total_mbps"]     for d in data]
        y_vals    = [d["total_disk_gb"]  for d in data]
        cpu_vals  = [d["max_cpu"]        for d in data]
        names     = [d["db_name"]        for d in data]

        # Scale bubbles: 12px minimum, 60px maximum
        max_cpu = max(cpu_vals) if max(cpu_vals) > 0 else 1
        scaled  = [max(12, int(60 * c / max_cpu)) if max_cpu > 0 else 20 for c in cpu_vals]

        fig = go.Figure(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="markers+text",
            text=names,
            textposition="top center",
            marker=dict(
                size=scaled,
                color="#4e73df",
                opacity=0.75,
                line=dict(color="#2e53bf", width=1.5),
                sizemode="diameter",
            ),
            customdata=cpu_vals,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "MBPS: %{x:.2f}<br>"
                "Size (GB): %{y:.2f}<br>"
                "Max CPU Sessions: %{customdata:.1f}"
                "<extra></extra>"
            ),
        ))
        fig.update_layout(
            xaxis=dict(
                title="Total MBPS (Read + Write + Redo)",
                showgrid=True,
                gridcolor="#f0f0f0",
                zeroline=True,
                zerolinecolor="#e0e0e0",
            ),
            yaxis=dict(
                title="Total Database Size (GB)",
                showgrid=True,
                gridcolor="#f0f0f0",
                zeroline=True,
                zerolinecolor="#e0e0e0",
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(t=30, b=60, l=70, r=30),
            height=560,
        )
        chart_content = dcc.Graph(figure=fig, config={"displayModeBar": False})
        footnote = html.P(
            "Bubble size represents maximum CPU sessions.  "
            "Hover over a bubble for details.",
            className="text-muted mt-2",
            style={"fontSize": "0.8rem"},
        )
    else:
        chart_content = dbc.Alert(
            [
                html.I(className="fas fa-exclamation-triangle me-2"),
                "No metric data found for this collection.  "
                "Run Workload Analysis first to generate metrics.",
            ],
            color="warning",
        )
        footnote = html.Div()

    db_count = len(data)
    db_word  = "database" if db_count == 1 else "databases"

    return html.Div([
        # Back link
        html.Div(
            dcc.Link(
                [html.I(className="fas fa-arrow-left me-2"), "Back to Home"],
                href="/",
                style={"textDecoration": "none", "color": "#4e73df", "fontSize": "0.875rem"},
            ),
            className="mb-3",
        ),

        # Header banner
        html.Div([
            html.Div([
                html.I(className="fas fa-chart-scatter me-3",
                       style={"fontSize": "2rem", "color": "#4e73df"}),
                html.Div([
                    html.H2(
                        f"Collection: {coll_name}",
                        style={"margin": 0, "fontWeight": "800", "color": "#2d3748"},
                    ),
                    html.P(
                        f"Client: {cl_name}  |  Project: {pr_name}  |  {db_count} {db_word}",
                        style={"margin": 0, "color": "#718096", "fontSize": "0.85rem"},
                    ),
                ]),
            ], style={"display": "flex", "alignItems": "center"}),
        ], style={
            "background": "linear-gradient(135deg, #f7faff 0%, #eef2ff 100%)",
            "borderRadius": "0.75rem",
            "padding": "1.25rem 1.5rem",
            "marginBottom": "1.5rem",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
        }),

        # Bubble chart card
        dbc.Card([
            dbc.CardHeader(
                html.Strong("Database Workload Profile — Size vs. Throughput"),
            ),
            dbc.CardBody(chart_content),
        ], style={"borderRadius": "0.5rem", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"}),

        footnote,
    ])
