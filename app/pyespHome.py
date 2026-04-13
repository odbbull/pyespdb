import dash
from dash import html, dcc, Input, Output, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from pyespUtil import getCollectionSummary, getSplashStats


# Icon and color config for each stat
STAT_CONFIG = {
    "Clients":     {"icon": "fas fa-building",     "color": "#4e73df"},
    "Projects":    {"icon": "fas fa-project-diagram","color": "#1cc88a"},
    "Collections": {"icon": "fas fa-layer-group",   "color": "#36b9cc"},
    "Hosts":       {"icon": "fas fa-server",        "color": "#f6c23e"},
    "Databases":   {"icon": "fas fa-database",      "color": "#e74a3b"},
}


def _stat_card(label, value, icon, color):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.Div([
                        html.Div(label, style={
                            "fontSize": "0.7rem", "fontWeight": "700",
                            "textTransform": "uppercase", "color": color,
                            "letterSpacing": "0.05em", "marginBottom": "0.25rem",
                        }),
                        html.Div(f"{value:,}", style={
                            "fontSize": "2rem", "fontWeight": "800",
                            "color": "#2d3748", "lineHeight": "1",
                        }),
                    ], style={"flex": "1"}),
                    html.Div(
                        html.I(className=f"{icon} fa-2x", style={"color": color, "opacity": "0.25"}),
                        style={"alignSelf": "center"},
                    ),
                ], style={"display": "flex", "justifyContent": "space-between"}),
            ]),
            style={
                "borderLeft": f"4px solid {color}",
                "borderRadius": "0.5rem",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
            },
        ),
        xs=12, sm=6, md=4, lg=True,
        className="mb-4",
    )


def _bar_chart(stats):
    labels = list(stats.keys())
    values = list(stats.values())
    colors = [STAT_CONFIG[k]["color"] for k in labels]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=values,
        textposition="outside",
        hovertemplate="%{x}: %{y}<extra></extra>",
    ))
    fig.update_layout(
        title=None,
        xaxis=dict(title=None, tickfont=dict(size=12)),
        yaxis=dict(title="Count", showgrid=True, gridcolor="#f0f0f0"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=20, b=20, l=40, r=20),
        height=300,
    )
    return fig


def _donut_chart(stats):
    labels = list(stats.keys())
    values = list(stats.values())
    colors = [STAT_CONFIG[k]["color"] for k in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker_colors=colors,
        textinfo="label+percent",
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=300,
        paper_bgcolor="white",
    )
    return fig


def generateHomePage(pClient, pProject):
    """Splash screen home page with summary stats and charts."""

    stats = getSplashStats()
    pRows, _ = getCollectionSummary()

    if pRows:
        pClient  = pRows[0][2]
        pProject = pRows[0][3]

    stat_cards = dbc.Row(
        [_stat_card(k, v, STAT_CONFIG[k]["icon"], STAT_CONFIG[k]["color"])
         for k, v in stats.items()],
        className="g-3",
    )

    charts_row = dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.Strong("Repository Overview — Counts by Entity")),
                dbc.CardBody(dcc.Graph(figure=_bar_chart(stats), config={"displayModeBar": False})),
            ], style={"borderRadius": "0.5rem", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"}),
            md=7, className="mb-4",
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.Strong("Proportional Distribution")),
                dbc.CardBody(dcc.Graph(figure=_donut_chart(stats), config={"displayModeBar": False})),
            ], style={"borderRadius": "0.5rem", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"}),
            md=5, className="mb-4",
        ),
    ])

    collections_chart = None
    if pRows:
        collections_chart = dbc.Card([
            dbc.CardHeader(html.Strong("Databases per Collection")),
            dbc.CardBody([
                dcc.Graph(
                    id="home-coll-chart",
                    figure=go.Figure(
                        data=[go.Bar(
                            x=[row[1] for row in pRows],
                            y=[row[4] for row in pRows],
                            customdata=[row[0] for row in pRows],
                            marker=dict(color="#4e73df", line=dict(color="#2e53bf", width=1)),
                            text=[row[4] for row in pRows],
                            textposition="outside",
                            hovertemplate="<b>%{x}</b><br>%{y} databases<br><i>Click to view bubble plot</i><extra></extra>",
                        )],
                        layout=go.Layout(
                            xaxis=dict(title="Collection", tickfont=dict(size=11)),
                            yaxis=dict(title="Databases", showgrid=True, gridcolor="#f0f0f0"),
                            plot_bgcolor="white",
                            paper_bgcolor="white",
                            margin=dict(t=10, b=40, l=40, r=20),
                            height=300,
                            clickmode="event",
                        ),
                    ),
                    config={"displayModeBar": False},
                    style={"cursor": "pointer"},
                ),
                html.Small(
                    [html.I(className="fas fa-hand-pointer me-1"), "Click a bar to view the collection bubble plot"],
                    className="text-muted",
                    style={"fontSize": "0.75rem"},
                ),
            ]),
        ], style={"borderRadius": "0.5rem", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"}, className="mb-4")

    return html.Div(id="home-page-content", children=[
        # Header banner
        html.Div([
            html.Div([
                html.I(className="fas fa-database me-3", style={"fontSize": "2rem", "color": "#4e73df"}),
                html.Div([
                    html.H2("AEG eSP Workload Analysis Tool",
                            style={"margin": 0, "fontWeight": "800", "color": "#2d3748"}),
                    html.P(f"Client: {pClient}  |  Project: {pProject}",
                           style={"margin": 0, "color": "#718096", "fontSize": "0.85rem"}),
                ]),
            ], style={"display": "flex", "alignItems": "center"}),
        ], style={
            "background": "linear-gradient(135deg, #f7faff 0%, #eef2ff 100%)",
            "borderRadius": "0.75rem",
            "padding": "1.25rem 1.5rem",
            "marginBottom": "1.5rem",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
        }),

        stat_cards,
        charts_row,
        collections_chart or html.Div(),
    ])


def register_callbacks(app):
    @app.callback(
        Output("url", "pathname"),
        Input("home-coll-chart", "clickData"),
        prevent_initial_call=True,
    )
    def _navigate_to_collection(click_data):
        if not click_data:
            return no_update
        point = click_data["points"][0]
        coll_id = point.get("customdata")
        if coll_id is None:
            return no_update
        return f"/collectionBubble/{coll_id}"
