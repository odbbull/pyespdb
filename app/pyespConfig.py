"""
Configuration management screens for PyESPDB.
Provides CRUD operations for Client, Project, Collection, and Category entities.
"""

from dash import html, dcc, Input, Output, State, ALL, ctx, no_update
import dash_bootstrap_components as dbc
from datetime import datetime, date
from pyespUtil import connect_postgres_db


# ── DB helper ──────────────────────────────────────────────────────────────────

def _run(sql, params=None, fetch=False):
    """Execute a query, committing on write or returning rows on fetch."""
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


# ── CLIENT ─────────────────────────────────────────────────────────────────────

def get_clients():
    return _run("""
        SELECT cl_id, cl_name, cl_shortname, cl_account_contact,
               cl_contact_email, tm_contact, tm_contact_email, is_active_fg,
               hidden_name
        FROM sp_client ORDER BY cl_name
    """, fetch=True)


def save_client(cl_id, d):
    if cl_id is None:
        _run("""
            INSERT INTO sp_client
              (cl_name, cl_shortname, cl_creation_date, is_active_fg,
               cl_account_contact, cl_contact_email, tm_contact, tm_contact_email,
               hidden_name)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (d['cl_name'], d['cl_shortname'], datetime.now(), d['is_active'],
              d.get('cl_account_contact') or None, d.get('cl_contact_email') or None,
              d.get('tm_contact') or None, d.get('tm_contact_email') or None,
              d.get('hidden_name') or None))
    else:
        _run("""
            UPDATE sp_client
               SET cl_name=%s, cl_shortname=%s, is_active_fg=%s,
                   cl_account_contact=%s, cl_contact_email=%s,
                   tm_contact=%s, tm_contact_email=%s, cl_modify_date=%s,
                   hidden_name=%s
             WHERE cl_id=%s
        """, (d['cl_name'], d['cl_shortname'], d['is_active'],
              d.get('cl_account_contact') or None, d.get('cl_contact_email') or None,
              d.get('tm_contact') or None, d.get('tm_contact_email') or None,
              datetime.now(), d.get('hidden_name') or None, cl_id))


def remove_client(cl_id):
    _run("DELETE FROM sp_client WHERE cl_id=%s", (cl_id,))


# ── PROJECT ────────────────────────────────────────────────────────────────────

def get_projects():
    return _run("""
        SELECT p.pr_id, p.pr_name, p.pr_shortname,
               p.sp_client_cl_id, c.cl_name, p.is_active_fg
        FROM sp_project p
        JOIN sp_client c ON c.cl_id = p.sp_client_cl_id
        ORDER BY p.pr_name
    """, fetch=True)


def get_client_stats():
    """Return clients with active project and collection counts."""
    return _run("""
        SELECT c.cl_id, c.cl_name,
               COUNT(DISTINCT p.pr_id)  FILTER (WHERE p.is_active_fg  = TRUE) AS active_projects,
               COUNT(DISTINCT co.coll_id) FILTER (WHERE co.is_active_fg = TRUE) AS active_collections
          FROM sp_client c
          LEFT JOIN sp_project    p  ON p.sp_client_cl_id  = c.cl_id
          LEFT JOIN sp_collection co ON co.sp_project_pr_id = p.pr_id
         GROUP BY c.cl_id, c.cl_name
         ORDER BY c.cl_name
    """, fetch=True)


def save_project(pr_id, d):
    if pr_id is None:
        _run("""
            INSERT INTO sp_project
              (pr_name, pr_shortname, pr_creation_date, is_active_fg, sp_client_cl_id)
            VALUES (%s,%s,%s,%s,%s)
        """, (d['pr_name'], d['pr_shortname'], datetime.now(),
              d['is_active'], d['sp_client_cl_id']))
    else:
        _run("""
            UPDATE sp_project
               SET pr_name=%s, pr_shortname=%s, is_active_fg=%s,
                   sp_client_cl_id=%s, pr_modify_date=%s
             WHERE pr_id=%s
        """, (d['pr_name'], d['pr_shortname'], d['is_active'],
              d['sp_client_cl_id'], datetime.now(), pr_id))


def remove_project(pr_id):
    _run("DELETE FROM sp_project WHERE pr_id=%s", (pr_id,))


# ── COLLECTION ─────────────────────────────────────────────────────────────────

def get_collections():
    return _run("""
        SELECT co.coll_id, co.coll_name, co.coll_shortname, co.coll_date,
               co.sp_project_pr_id, p.pr_name, p.sp_client_cl_id, c.cl_name,
               co.is_active_fg, co.coll_dir_location,
               co.coll_collected_by, co.coll_collector_email, co.coll_objective
        FROM sp_collection co
        JOIN sp_project p ON p.pr_id = co.sp_project_pr_id
        JOIN sp_client c ON c.cl_id = p.sp_client_cl_id
        ORDER BY co.coll_name
    """, fetch=True)


def save_collection(coll_id, d):
    coll_date = d.get('coll_date') or datetime.now()
    if coll_id is None:
        _run("""
            INSERT INTO sp_collection
              (coll_name, coll_shortname, coll_date, is_active_fg,
               coll_dir_location, coll_collected_by, coll_collector_email,
               coll_objective, sp_project_pr_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (d['coll_name'], d['coll_shortname'], coll_date, d['is_active'],
              d.get('coll_dir_location') or None, d.get('coll_collected_by') or None,
              d.get('coll_collector_email') or None, d.get('coll_objective') or None,
              d['sp_project_pr_id']))
    else:
        _run("""
            UPDATE sp_collection
               SET coll_name=%s, coll_shortname=%s, coll_date=%s, is_active_fg=%s,
                   coll_dir_location=%s, coll_collected_by=%s,
                   coll_collector_email=%s, coll_objective=%s, sp_project_pr_id=%s
             WHERE coll_id=%s
        """, (d['coll_name'], d['coll_shortname'], coll_date, d['is_active'],
              d.get('coll_dir_location') or None, d.get('coll_collected_by') or None,
              d.get('coll_collector_email') or None, d.get('coll_objective') or None,
              d['sp_project_pr_id'], coll_id))


def remove_collection(coll_id):
    _run("DELETE FROM sp_collection WHERE coll_id=%s", (coll_id,))


# ── CATEGORY ───────────────────────────────────────────────────────────────────

def get_categories():
    return _run("""
        SELECT cat_id, cat_name, cat_acronym, cat_yaxis_unit,
               cat_yaxis_divisor, is_static_fg, is_active_fg, add_interval_fg
        FROM sp_category ORDER BY cat_name
    """, fetch=True)


def save_category(cat_id, d):
    if cat_id is None:
        _run("""
            INSERT INTO sp_category
              (cat_name, cat_acronym, is_static_fg, is_active_fg,
               cat_yaxis_unit, cat_yaxis_divisor, add_interval_fg)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (d['cat_name'], d['cat_acronym'],
              d.get('is_static'), d.get('is_active'),
              d.get('cat_yaxis_unit') or None, d.get('cat_yaxis_divisor'),
              d.get('add_interval')))
    else:
        _run("""
            UPDATE sp_category
               SET cat_name=%s, cat_acronym=%s, is_static_fg=%s, is_active_fg=%s,
                   cat_yaxis_unit=%s, cat_yaxis_divisor=%s, add_interval_fg=%s
             WHERE cat_id=%s
        """, (d['cat_name'], d['cat_acronym'],
              d.get('is_static'), d.get('is_active'),
              d.get('cat_yaxis_unit') or None, d.get('cat_yaxis_divisor'),
              d.get('add_interval'), cat_id))


def remove_category(cat_id):
    _run("DELETE FROM sp_category WHERE cat_id=%s", (cat_id,))


# ── TABLE ROW BUILDERS ─────────────────────────────────────────────────────────

def _badge(flag):
    return dbc.Badge("Active", color="success", pill=True) if flag \
        else dbc.Badge("Inactive", color="secondary", pill=True)


def _actions(entity, row_id, view_href=None):
    buttons = []
    if view_href:
        buttons.append(
            dbc.Button(html.I(className="fas fa-search"),
                       href=view_href, external_link=False,
                       color="outline-primary", size="sm", className="me-1")
        )
    buttons += [
        dbc.Button(html.I(className="fas fa-pencil-alt"),
                   id={"type": f"{entity}-edit", "index": row_id},
                   color="outline-secondary", size="sm", className="me-1", n_clicks=0),
        dbc.Button(html.I(className="fas fa-trash-alt"),
                   id={"type": f"{entity}-delete", "index": row_id},
                   color="outline-danger", size="sm", n_clicks=0),
    ]
    return html.Td(buttons, className="text-nowrap")


def _client_rows(data):
    if not data:
        return [html.Tr(html.Td("No clients defined.", colSpan=6,
                                className="text-center text-muted fst-italic py-3"))]
    return [html.Tr([
        html.Td(r['cl_name']), html.Td(r['cl_shortname']),
        html.Td(r['cl_account_contact'] or "—"), html.Td(r['cl_contact_email'] or "—"),
        html.Td(_badge(r['is_active_fg'])), _actions("client", r['cl_id']),
    ]) for r in data]


def _project_rows(data, client_filter=None):
    if client_filter and client_filter != "all":
        data = [r for r in data if r['sp_client_cl_id'] == client_filter]
    if not data:
        return [html.Tr(html.Td("No projects defined.", colSpan=5,
                                className="text-center text-muted fst-italic py-3"))]
    return [html.Tr([
        html.Td(r['pr_name']), html.Td(r['pr_shortname']),
        html.Td(r['cl_name']), html.Td(_badge(r['is_active_fg'])),
        _actions("project", r['pr_id']),
    ]) for r in data]


def _collection_rows(data):
    if not data:
        return [html.Tr(html.Td("No collections defined.", colSpan=6,
                                className="text-center text-muted fst-italic py-3"))]
    return [html.Tr([
        html.Td(r['coll_name']), html.Td(r['coll_shortname']),
        html.Td(f"{r['pr_name']} / {r['cl_name']}"),
        html.Td(str(r['coll_date'])[:10] if r['coll_date'] else "—"),
        html.Td(_badge(r['is_active_fg'])),
        _actions("collection", r['coll_id'], view_href="/lineGraph"),
    ]) for r in data]


def _category_rows(data):
    if not data:
        return [html.Tr(html.Td("No categories defined.", colSpan=6,
                                className="text-center text-muted fst-italic py-3"))]
    return [html.Tr([
        html.Td(r['cat_name']), html.Td(r['cat_acronym']),
        html.Td(r['cat_yaxis_unit'] or "—"),
        html.Td(str(r['cat_yaxis_divisor']) if r['cat_yaxis_divisor'] is not None else "—"),
        html.Td(_badge(r['is_active_fg'])), _actions("category", r['cat_id']),
    ]) for r in data]


# ── PROJECT CLIENT SELECTOR ───────────────────────────────────────────────────

def _client_stats_table(stats, selected="all"):
    """Proper table with one selectable row per client showing project/collection counts."""
    font = "0.8rem"

    def _row(cl_id, name, proj_n, coll_n):
        is_sel = str(cl_id) == str(selected)
        sel_icon = html.I(className="fas fa-circle-dot", style={"color": "#0d6efd"}) \
                   if is_sel else \
                   html.I(className="far fa-circle", style={"color": "#adb5bd"})
        proj_cell = dbc.Badge(str(proj_n), color="primary", pill=True) \
                    if isinstance(proj_n, int) else \
                    html.Span("—", style={"color": "#adb5bd"})
        coll_cell = dbc.Badge(str(coll_n), color="success", pill=True) \
                    if isinstance(coll_n, int) else \
                    html.Span("—", style={"color": "#adb5bd"})
        return html.Tr([
            html.Td(
                dbc.Button(sel_icon,
                           id={"type": "mp-client-select", "index": cl_id},
                           color="link", size="sm", n_clicks=0,
                           style={"padding": "0 4px", "border": "none"}),
                style={"width": "36px", "textAlign": "center", "verticalAlign": "middle"},
            ),
            html.Td(html.Strong(name, style={"fontSize": font}) if is_sel
                    else html.Span(name, style={"fontSize": font}),
                    style={"verticalAlign": "middle"}),
            html.Td(proj_cell, className="text-center",
                    style={"width": "130px", "fontSize": font, "verticalAlign": "middle"}),
            html.Td(coll_cell, className="text-center",
                    style={"width": "140px", "fontSize": font, "verticalAlign": "middle"}),
        ], className="table-primary" if is_sel else "")

    rows = [_row("all", "All Clients", None, None)] + [
        _row(r["cl_id"], r["cl_name"], r["active_projects"], r["active_collections"])
        for r in stats
    ]

    thead = html.Thead(html.Tr([
        html.Th("",                 style={"width": "36px"}),
        html.Th("Client",           style={"fontSize": "0.75rem", "color": "#6c757d"}),
        html.Th("Active Projects",  className="text-center",
                style={"width": "130px", "fontSize": "0.75rem", "color": "#6c757d"}),
        html.Th("Active Collections", className="text-center",
                style={"width": "140px", "fontSize": "0.75rem", "color": "#6c757d"}),
    ]))

    return dbc.Table(
        [thead, html.Tbody(rows)],
        size="sm", hover=True, striped=False, bordered=False,
        style={"marginBottom": 0, "width": "auto", "minWidth": "350px"},
    )


# ── MODAL DEFINITIONS ──────────────────────────────────────────────────────────

def _client_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="client-modal-title")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([dbc.Label("Client ID"),
                         dbc.Input(id="client-id-display", disabled=True,
                                   placeholder="—")], width=4),
                dbc.Col([dbc.Label("Client Name *"),
                         dbc.Input(id="client-name", placeholder="Full client name")], width=5),
                dbc.Col([dbc.Label("Short Name *"),
                         dbc.Input(id="client-shortname", placeholder="Max 15 chars", maxLength=15)], width=3),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Account Contact"),
                         dbc.Input(id="client-account-contact", placeholder="Contact name")], width=6),
                dbc.Col([dbc.Label("Contact Email"),
                         dbc.Input(id="client-contact-email", type="email", placeholder="contact@example.com")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Hidden Name"),
                         dbc.Input(id="client-hidden-name", placeholder="Alternate / hidden name",
                                   maxLength=50)], width=12),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Contact"),
                         dbc.Input(id="client-dl-contact", placeholder="Contact name")], width=6),
                dbc.Col([dbc.Label("Email"),
                         dbc.Input(id="client-dl-email", type="email", placeholder="email@example.com")], width=6),
            ], className="mb-3"),
            dbc.Checklist(id="client-is-active",
                          options=[{"label": "Active", "value": 1}],
                          value=[1], switch=True),
        ]),
        dbc.ModalFooter([
            dbc.Button("Save", id="client-save-btn", color="primary", className="me-2"),
            dbc.Button("Cancel", id="client-cancel-btn", color="secondary"),
        ]),
    ], id="client-modal", is_open=False)


def _project_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="project-modal-title")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([dbc.Label("Project Name *"),
                         dbc.Input(id="project-name", placeholder="Project name")], width=8),
                dbc.Col([dbc.Label("Short Name *"),
                         dbc.Input(id="project-shortname", placeholder="Max 15 chars", maxLength=15)], width=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Client *"),
                         dcc.Dropdown(id="project-client-dd", placeholder="Select a client…",
                                      clearable=False)], width=12),
            ], className="mb-3"),
            dbc.Checklist(id="project-is-active",
                          options=[{"label": "Active", "value": 1}],
                          value=[1], switch=True),
        ]),
        dbc.ModalFooter([
            dbc.Button("Save", id="project-save-btn", color="primary", className="me-2"),
            dbc.Button("Cancel", id="project-cancel-btn", color="secondary"),
        ]),
    ], id="project-modal", is_open=False)


def _collection_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="collection-modal-title")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([dbc.Label("Collection Name *"),
                         dbc.Input(id="collection-name", placeholder="Collection name")], width=8),
                dbc.Col([dbc.Label("Short Name *"),
                         dbc.Input(id="collection-shortname", placeholder="Max 15 chars", maxLength=15)], width=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Project *"),
                         dcc.Dropdown(id="collection-project-dd",
                                      placeholder="Select a project…", clearable=False)], width=8),
                dbc.Col([dbc.Label("Collection Date *"),
                         dbc.Input(id="collection-date", type="date")], width=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Directory Location"),
                         dbc.Input(id="collection-dir-location", placeholder="/path/to/collection")], width=12),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Collected By"),
                         dbc.Input(id="collection-collected-by", placeholder="Collector name")], width=6),
                dbc.Col([dbc.Label("Collector Email"),
                         dbc.Input(id="collection-collector-email", type="email",
                                   placeholder="collector@example.com")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Objective"),
                         dbc.Textarea(id="collection-objective",
                                      placeholder="Collection objective…", rows=2)], width=12),
            ], className="mb-3"),
            dbc.Checklist(id="collection-is-active",
                          options=[{"label": "Active", "value": 1}],
                          value=[1], switch=True),
        ]),
        dbc.ModalFooter([
            dbc.Button("Save", id="collection-save-btn", color="primary", className="me-2"),
            dbc.Button("Cancel", id="collection-cancel-btn", color="secondary"),
        ]),
    ], id="collection-modal", is_open=False, size="lg")


def _category_modal():
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(id="category-modal-title")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([dbc.Label("Category Name *"),
                         dbc.Input(id="category-name", placeholder="Category name")], width=8),
                dbc.Col([dbc.Label("Acronym *"),
                         dbc.Input(id="category-acronym", placeholder="Max 15 chars", maxLength=15)], width=4),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Y-Axis Unit"),
                         dbc.Input(id="category-yaxis-unit", placeholder="e.g. MB/s, seconds")], width=6),
                dbc.Col([dbc.Label("Y-Axis Divisor"),
                         dbc.Input(id="category-yaxis-divisor", type="number",
                                   placeholder="e.g. 1024")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Checklist(id="category-is-static",
                                  options=[{"label": "Static", "value": 1}],
                                  value=[], switch=True, className="mb-2"),
                    dbc.Checklist(id="category-is-active",
                                  options=[{"label": "Active", "value": 1}],
                                  value=[1], switch=True, className="mb-2"),
                    dbc.Checklist(id="category-add-interval",
                                  options=[{"label": "Add Interval", "value": 1}],
                                  value=[], switch=True),
                ]),
            ]),
        ]),
        dbc.ModalFooter([
            dbc.Button("Save", id="category-save-btn", color="primary", className="me-2"),
            dbc.Button("Cancel", id="category-cancel-btn", color="secondary"),
        ]),
    ], id="category-modal", is_open=False)


# ── PAGE LAYOUTS ───────────────────────────────────────────────────────────────

def _page_wrapper(title, add_btn_id, thead_cells, tbody_id, data_rows, stores, modal):
    return html.Div([
        dbc.Row([
            dbc.Col(html.H2(title, className="mb-0"), width="auto"),
            dbc.Col(
                dbc.Button([html.I(className="fas fa-plus me-1"), "Add New"],
                           id=add_btn_id, color="primary", size="sm"),
                className="d-flex align-items-center justify-content-end"
            ),
        ], className="mb-3 align-items-center"),
        dbc.Table([
            html.Thead(html.Tr([html.Th(c) for c in thead_cells])),
            html.Tbody(id=tbody_id, children=data_rows),
        ], striped=True, bordered=True, hover=True, responsive=True, size="sm"),
        *stores,
        modal,
    ])


def generate_client_page():
    return _page_wrapper(
        "Manage Clients", "client-add-btn",
        ["Name", "Short Name", "Account Contact", "Contact Email", "Status", "Actions"],
        "client-table-body", _client_rows(get_clients()),
        [dcc.Store(id="client-edit-id")], _client_modal()
    )


def generate_project_page():
    stats = get_client_stats()
    return html.Div([
        dbc.Row([
            dbc.Col(html.H2("Manage Projects", className="mb-0"), width="auto"),
            dbc.Col(
                dbc.Button([html.I(className="fas fa-plus me-1"), "Add New"],
                           id="project-add-btn", color="primary", size="sm"),
                className="d-flex align-items-center justify-content-end",
            ),
        ], className="mb-3 align-items-center"),
        dbc.Card([
            dbc.CardHeader(html.Span("Filter by Client", className="fw-semibold")),
            dbc.CardBody(
                html.Div(_client_stats_table(stats, "all"), id="mp-client-table"),
                style={"padding": "8px 12px"},
            ),
        ], className="mb-4", style={"maxWidth": "50%"}),
        dbc.Table([
            html.Thead(html.Tr([html.Th(c) for c in
                                ["Name", "Short Name", "Client", "Status", "Actions"]])),
            html.Tbody(id="project-table-body", children=_project_rows(get_projects())),
        ], striped=True, bordered=True, hover=True, responsive=True, size="sm"),
        dcc.Store(id="project-edit-id"),
        dcc.Store(id="mp-client-filter", data="all"),
        _project_modal(),
    ])


def generate_collection_page():
    return _page_wrapper(
        "Manage Collections", "collection-add-btn",
        ["Name", "Short Name", "Project / Client", "Date", "Status", "Actions"],
        "collection-table-body", _collection_rows(get_collections()),
        [dcc.Store(id="collection-edit-id")], _collection_modal()
    )


def generate_category_page():
    return _page_wrapper(
        "Manage Categories", "category-add-btn",
        ["Name", "Acronym", "Y-Axis Unit", "Divisor", "Status", "Actions"],
        "category-table-body", _category_rows(get_categories()),
        [dcc.Store(id="category-edit-id")], _category_modal()
    )


# ── CALLBACKS ──────────────────────────────────────────────────────────────────

def register_callbacks(app):

    # ── CLIENT ──────────────────────────────────────────────────────────────

    @app.callback(
        Output("client-modal",          "is_open"),
        Output("client-edit-id",        "data"),
        Output("client-modal-title",    "children"),
        Output("client-id-display",     "value"),
        Output("client-name",           "value"),
        Output("client-shortname",      "value"),
        Output("client-account-contact","value"),
        Output("client-contact-email",  "value"),
        Output("client-hidden-name",    "value"),
        Output("client-dl-contact",     "value"),
        Output("client-dl-email",       "value"),
        Output("client-is-active",      "value"),
        Input("client-add-btn", "n_clicks"),
        Input({"type": "client-edit", "index": ALL}, "n_clicks"),
        Input("client-cancel-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def _client_modal_ctrl(add_n, edit_ns, cancel_n):
        t = ctx.triggered_id
        _no = (no_update,) * 11
        if t == "client-cancel-btn":
            return (False,) + _no
        if t == "client-add-btn":
            return True, None, "Add Client", "", "", "", "", "", "", "", "", [1]
        if isinstance(t, dict) and t.get("type") == "client-edit":
            if not any(edit_ns):
                return (False,) + _no
            row = next((r for r in get_clients() if r['cl_id'] == t["index"]), None)
            if not row:
                return (False,) + _no
            return (True, row['cl_id'], "Edit Client",
                    str(row['cl_id']),
                    row['cl_name'], row['cl_shortname'],
                    row['cl_account_contact'] or "", row['cl_contact_email'] or "",
                    row['hidden_name'] or "",
                    row['tm_contact'] or "", row['tm_contact_email'] or "",
                    [1] if row['is_active_fg'] else [])
        return (False,) + _no

    @app.callback(
        Output("client-table-body", "children"),
        Output("client-modal", "is_open", allow_duplicate=True),
        Input("client-save-btn", "n_clicks"),
        State("client-edit-id", "data"),
        State("client-name", "value"),
        State("client-shortname", "value"),
        State("client-account-contact", "value"),
        State("client-contact-email", "value"),
        State("client-hidden-name", "value"),
        State("client-dl-contact", "value"),
        State("client-dl-email", "value"),
        State("client-is-active", "value"),
        prevent_initial_call=True,
    )
    def _client_save(_, edit_id, name, shortname, acct, email, hidden_name, dl, dl_email, active):
        save_client(edit_id, {
            'cl_name': name, 'cl_shortname': shortname,
            'cl_account_contact': acct, 'cl_contact_email': email,
            'hidden_name': hidden_name,
            'tm_contact': dl, 'tm_contact_email': dl_email,
            'is_active': bool(active),
        })
        return _client_rows(get_clients()), False

    @app.callback(
        Output("client-table-body", "children", allow_duplicate=True),
        Input({"type": "client-delete", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def _client_delete(ns):
        if not any(ns):
            return no_update
        remove_client(ctx.triggered_id["index"])
        return _client_rows(get_clients())

    # ── PROJECT ─────────────────────────────────────────────────────────────

    @app.callback(
        Output("project-modal", "is_open"),
        Output("project-edit-id", "data"),
        Output("project-modal-title", "children"),
        Output("project-name", "value"),
        Output("project-shortname", "value"),
        Output("project-client-dd", "options"),
        Output("project-client-dd", "value"),
        Output("project-is-active", "value"),
        Input("project-add-btn", "n_clicks"),
        Input({"type": "project-edit", "index": ALL}, "n_clicks"),
        Input("project-cancel-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def _project_modal_ctrl(add_n, edit_ns, cancel_n):
        t = ctx.triggered_id
        opts = [{"label": c['cl_name'], "value": c['cl_id']} for c in get_clients()]
        _no = (no_update,) * 7
        if t == "project-cancel-btn":
            return (False,) + _no
        if t == "project-add-btn":
            return True, None, "Add Project", "", "", opts, None, [1]
        if isinstance(t, dict) and t.get("type") == "project-edit":
            if not any(edit_ns):
                return (False,) + _no
            row = next((r for r in get_projects() if r['pr_id'] == t["index"]), None)
            if not row:
                return (False,) + _no
            return (True, row['pr_id'], "Edit Project",
                    row['pr_name'], row['pr_shortname'],
                    opts, row['sp_client_cl_id'],
                    [1] if row['is_active_fg'] else [])
        return (False,) + _no

    @app.callback(
        Output("project-table-body", "children"),
        Input("mp-client-filter", "data"),
        prevent_initial_call=True,
    )
    def _project_filter(client_filter):
        return _project_rows(get_projects(), client_filter)

    @app.callback(
        Output("mp-client-filter", "data"),
        Output("mp-client-table",  "children"),
        Input({"type": "mp-client-select", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def _mp_client_select(ns):
        if not any(ns):
            return no_update, no_update
        selected = ctx.triggered_id["index"]
        return selected, _client_stats_table(get_client_stats(), selected)

    @app.callback(
        Output("project-table-body", "children", allow_duplicate=True),
        Output("project-modal", "is_open", allow_duplicate=True),
        Input("project-save-btn", "n_clicks"),
        State("project-edit-id", "data"),
        State("project-name", "value"),
        State("project-shortname", "value"),
        State("project-client-dd", "value"),
        State("project-is-active", "value"),
        State("mp-client-filter", "data"),
        prevent_initial_call=True,
    )
    def _project_save(_, edit_id, name, shortname, client_id, active, client_filter):
        save_project(edit_id, {
            'pr_name': name, 'pr_shortname': shortname,
            'sp_client_cl_id': client_id, 'is_active': bool(active),
        })
        return _project_rows(get_projects(), client_filter), False

    @app.callback(
        Output("project-table-body", "children", allow_duplicate=True),
        Input({"type": "project-delete", "index": ALL}, "n_clicks"),
        State("mp-client-filter", "data"),
        prevent_initial_call=True,
    )
    def _project_delete(ns, client_filter):
        if not any(ns):
            return no_update
        remove_project(ctx.triggered_id["index"])
        return _project_rows(get_projects(), client_filter)

    # ── COLLECTION ──────────────────────────────────────────────────────────

    @app.callback(
        Output("collection-modal", "is_open"),
        Output("collection-edit-id", "data"),
        Output("collection-modal-title", "children"),
        Output("collection-name", "value"),
        Output("collection-shortname", "value"),
        Output("collection-project-dd", "options"),
        Output("collection-project-dd", "value"),
        Output("collection-date", "value"),
        Output("collection-dir-location", "value"),
        Output("collection-collected-by", "value"),
        Output("collection-collector-email", "value"),
        Output("collection-objective", "value"),
        Output("collection-is-active", "value"),
        Input("collection-add-btn", "n_clicks"),
        Input({"type": "collection-edit", "index": ALL}, "n_clicks"),
        Input("collection-cancel-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def _collection_modal_ctrl(add_n, edit_ns, cancel_n):
        t = ctx.triggered_id
        proj_opts = [
            {"label": f"{p['pr_name']}  ({p['cl_name']})", "value": p['pr_id']}
            for p in get_projects()
        ]
        _no = (no_update,) * 12
        if t == "collection-cancel-btn":
            return (False,) + _no
        if t == "collection-add-btn":
            return (True, None, "Add Collection",
                    "", "", proj_opts, None,
                    str(date.today()), "", "", "", "", [1])
        if isinstance(t, dict) and t.get("type") == "collection-edit":
            if not any(edit_ns):
                return (False,) + _no
            row = next((r for r in get_collections() if r['coll_id'] == t["index"]), None)
            if not row:
                return (False,) + _no
            coll_date = str(row['coll_date'])[:10] if row['coll_date'] else str(date.today())
            return (True, row['coll_id'], "Edit Collection",
                    row['coll_name'], row['coll_shortname'],
                    proj_opts, row['sp_project_pr_id'],
                    coll_date,
                    row['coll_dir_location'] or "",
                    row['coll_collected_by'] or "",
                    row['coll_collector_email'] or "",
                    row['coll_objective'] or "",
                    [1] if row['is_active_fg'] else [])
        return (False,) + _no

    @app.callback(
        Output("collection-table-body", "children"),
        Output("collection-modal", "is_open", allow_duplicate=True),
        Input("collection-save-btn", "n_clicks"),
        State("collection-edit-id", "data"),
        State("collection-name", "value"),
        State("collection-shortname", "value"),
        State("collection-project-dd", "value"),
        State("collection-date", "value"),
        State("collection-dir-location", "value"),
        State("collection-collected-by", "value"),
        State("collection-collector-email", "value"),
        State("collection-objective", "value"),
        State("collection-is-active", "value"),
        prevent_initial_call=True,
    )
    def _collection_save(_, edit_id, name, shortname, proj_id, coll_date,
                         dir_loc, collected_by, collector_email, objective, active):
        save_collection(edit_id, {
            'coll_name': name, 'coll_shortname': shortname,
            'sp_project_pr_id': proj_id, 'coll_date': coll_date,
            'coll_dir_location': dir_loc, 'coll_collected_by': collected_by,
            'coll_collector_email': collector_email,
            'coll_objective': objective, 'is_active': bool(active),
        })
        return _collection_rows(get_collections()), False

    @app.callback(
        Output("collection-table-body", "children", allow_duplicate=True),
        Input({"type": "collection-delete", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def _collection_delete(ns):
        if not any(ns):
            return no_update
        remove_collection(ctx.triggered_id["index"])
        return _collection_rows(get_collections())

    # ── CATEGORY ────────────────────────────────────────────────────────────

    @app.callback(
        Output("category-modal", "is_open"),
        Output("category-edit-id", "data"),
        Output("category-modal-title", "children"),
        Output("category-name", "value"),
        Output("category-acronym", "value"),
        Output("category-yaxis-unit", "value"),
        Output("category-yaxis-divisor", "value"),
        Output("category-is-static", "value"),
        Output("category-is-active", "value"),
        Output("category-add-interval", "value"),
        Input("category-add-btn", "n_clicks"),
        Input({"type": "category-edit", "index": ALL}, "n_clicks"),
        Input("category-cancel-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def _category_modal_ctrl(add_n, edit_ns, cancel_n):
        t = ctx.triggered_id
        _no = (no_update,) * 9
        if t == "category-cancel-btn":
            return (False,) + _no
        if t == "category-add-btn":
            return True, None, "Add Category", "", "", "", None, [], [1], []
        if isinstance(t, dict) and t.get("type") == "category-edit":
            if not any(edit_ns):
                return (False,) + _no
            row = next((r for r in get_categories() if r['cat_id'] == t["index"]), None)
            if not row:
                return (False,) + _no
            return (True, row['cat_id'], "Edit Category",
                    row['cat_name'], row['cat_acronym'],
                    row['cat_yaxis_unit'] or "", row['cat_yaxis_divisor'],
                    [1] if row['is_static_fg'] else [],
                    [1] if row['is_active_fg'] else [],
                    [1] if row['add_interval_fg'] else [])
        return (False,) + _no

    @app.callback(
        Output("category-table-body", "children"),
        Output("category-modal", "is_open", allow_duplicate=True),
        Input("category-save-btn", "n_clicks"),
        State("category-edit-id", "data"),
        State("category-name", "value"),
        State("category-acronym", "value"),
        State("category-yaxis-unit", "value"),
        State("category-yaxis-divisor", "value"),
        State("category-is-static", "value"),
        State("category-is-active", "value"),
        State("category-add-interval", "value"),
        prevent_initial_call=True,
    )
    def _category_save(_, edit_id, name, acronym, yaxis_unit, yaxis_divisor,
                       is_static, is_active, add_interval):
        save_category(edit_id, {
            'cat_name': name, 'cat_acronym': acronym,
            'cat_yaxis_unit': yaxis_unit or None,
            'cat_yaxis_divisor': yaxis_divisor,
            'is_static': bool(is_static),
            'is_active': bool(is_active),
            'add_interval': bool(add_interval),
        })
        return _category_rows(get_categories()), False

    @app.callback(
        Output("category-table-body", "children", allow_duplicate=True),
        Input({"type": "category-delete", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def _category_delete(ns):
        if not any(ns):
            return no_update
        remove_category(ctx.triggered_id["index"])
        return _category_rows(get_categories())
