"""
This app creates a simple sidebar layout using inline style arguments and the
dbc.Nav component.

dcc.Location is used to track the current location, and a callback uses the
current location to render the appropriate page content. The active prop of
each NavLink is set automatically according to the current pathname. To use
this feature you must install dash-bootstrap-components >= 0.11.0.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plotly.com/urls
"""

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from pyespHome import generateHomePage, register_callbacks as register_home_callbacks
from pyespCollBubble import generate_collection_bubble_page
from pyespConfig import (
    generate_client_page, generate_project_page,
    generate_collection_page, generate_category_page,
    register_callbacks as register_config_callbacks,
)
from pyespLoadFile import (
    generate_load_file_page,
    register_callbacks as register_loadfile_callbacks,
)
from pyespWorkload import (
    generate_workload_analysis_page,
    register_callbacks as register_workload_callbacks,
)
from pyespLineGraph import (
    generate_line_graph_page,
    register_callbacks as register_linegraph_callbacks,
)
from pyespAssessment import (
    generate_assessment_page,
    register_callbacks as register_assessment_callbacks,
)
from pyespCollSummary import (
    generate_collection_summary_page,
    register_callbacks as register_collsummary_callbacks,
)
from pyespDbGraph import (
    generate_db_graph_page,
    register_callbacks as register_dbgraph_callbacks,
)
import os
from contextlib import contextmanager

app = dash.Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    ],
    suppress_callback_exceptions=True,
)

# Custom CSS to reduce font sizes
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-size: 0.875rem;
            }
            .nav-link {
                font-size: 0.875rem;
            }
            .nav-link:hover {
                background-color: transparent !important;
            }
            .nav-link.active {
                background-color: transparent !important;
                color: #0d6efd !important;
            }
            .accordion-button {
                font-size: 0.75rem;
                padding: 0.5rem 0.75rem;
                background-color: transparent !important;
                box-shadow: none !important;
            }
            .accordion-button::after {
                width: 0.6rem;
                height: 0.6rem;
                background-size: 0.6rem;
            }
            .accordion-button:hover {
                background-color: transparent !important;
            }
            .accordion-button:focus {
                border-color: transparent;
                box-shadow: none;
            }
            .accordion-button:not(.collapsed) {
                background-color: transparent !important;
                color: inherit;
            }
            .accordion-item {
                border: none;
                background-color: transparent;
            }
            .accordion-body {
                padding: 0.25rem 0;
            }
            h1 { font-size: 1.75rem; }
            h2 { font-size: 1.5rem; }
            h3 { font-size: 1.25rem; }
            h4 { font-size: 1.125rem; }
            p, .lead {
                font-size: 0.875rem;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "1.5rem 0.75rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "13.5rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Accenture", style={'textAlign': 'center'}),
        html.H4("Enkitec Group", style={'textAlign': 'center'}),
        html.Hr(),
        html.P("AEG eSP Workload Analysis Tool", className="lead", style={'textAlign': 'center'}),
        dbc.Nav(
            [
                dbc.NavLink([html.I(className="fas fa-home me-2"), "Home"], href="/", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Hr(),
        # Tree-structured menu with collapsible sections
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dbc.Nav(
                            [
                                dbc.NavLink("Collection Summary", href="/collSummary", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                                dbc.NavLink("Workload Analysis", href="/workloadAnalysis", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                                dbc.NavLink("Line Graph", href="/lineGraph", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                                dbc.NavLink("Assessment", href="/assessment", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                            ],
                            vertical=True,
                            pills=True,
                        ),
                    ],
                    title="Analyze",
                ),
                dbc.AccordionItem(
                    [
                        dbc.Nav(
                            [
                                dbc.NavLink("Clients", href="/manageClient", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                                dbc.NavLink("Projects", href="/manageProject", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                                dbc.NavLink("Collections", href="/manageCollection", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                                dbc.NavLink("Categories", href="/manageCategory", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                                html.Hr(style={"margin": "0.25rem 0"}),
                                dbc.NavLink("specInt Rating", href="/specIntRating", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                                dbc.NavLink("Load File", href="/loadFile", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                            ],
                            vertical=True,
                            pills=True,
                        ),
                    ],
                    title="Configuration",
                ),
                dbc.AccordionItem(
                    [
                        dbc.Nav(
                            [
                                dbc.NavLink("User Preferences", href="/userPrefs", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                                dbc.NavLink("System Settings", href="/sysSettings", active="exact", style={"padding-left": "1rem", "font-size": "0.75rem", "padding-top": "0.25rem", "padding-bottom": "0.25rem"}),
                            ],
                            vertical=True,
                            pills=True,
                        ),
                    ],
                    title="Settings",
                ),
            ],
            start_collapsed=True,
            always_open=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

myClient = ''
myProject = ''

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url", refresh=False), sidebar, content])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/" or pathname == "" or pathname == None:
        return generateHomePage(myClient, myProject)
    # Analyze section routes
    elif pathname and pathname.startswith("/collectionBubble/"):
        coll_id = pathname.split("/")[-1]
        return generate_collection_bubble_page(coll_id)
    elif pathname == "/collSummary":
        return generate_collection_summary_page()
    elif pathname and pathname.startswith("/dbGraph/"):
        parts       = [p for p in pathname.split("/") if p]
        # parts: ["dbGraph", coll_id, db_id?, cat_name?, cat_acronym?]
        coll_id     = parts[1] if len(parts) > 1 else None
        db_id       = parts[2] if len(parts) > 2 else None
        cat_name    = parts[3] if len(parts) > 3 else None
        cat_acronym = parts[4] if len(parts) > 4 else None
        return generate_db_graph_page(coll_id, db_id, cat_name, cat_acronym)
    elif pathname == "/workloadAnalysis":
        return generate_workload_analysis_page()
    elif pathname == "/lineGraph":
        return generate_line_graph_page()
    elif pathname == "/assessment":
        return generate_assessment_page()
    # Configuration — data management
    elif pathname == "/manageClient":
        return generate_client_page()
    elif pathname == "/manageProject":
        return generate_project_page()
    elif pathname == "/manageCollection":
        return generate_collection_page()
    elif pathname == "/manageCategory":
        return generate_category_page()
    # Configuration section routes
    elif pathname == "/specIntRating":
        return html.Div([
            html.H2("specInt Rating"),
            html.P("Configure specInt ratings here.")
        ])
    elif pathname == "/loadFile":
        return generate_load_file_page()
    # Settings section routes
    elif pathname == "/userPrefs":
        return html.Div([
            html.H2("User Preferences"),
            html.P("Customize your user preferences here.")
        ])
    elif pathname == "/sysSettings":
        return html.Div([
            html.H2("System Settings"),
            html.P("Configure system-wide settings here.")
        ])
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


register_config_callbacks(app)
register_loadfile_callbacks(app)
register_workload_callbacks(app)
register_linegraph_callbacks(app)
register_assessment_callbacks(app)
register_collsummary_callbacks(app)
register_dbgraph_callbacks(app)
register_home_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, port=8051)
