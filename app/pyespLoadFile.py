"""
Load File screen — upload an ESCP ZIP, associate it with a collection,
and ingest its contents into the PostgreSQL database via the AcmeESP pipeline.
"""
import os
import sys
import base64
import logging

# Make AcmeESP modules importable (app/AcmeESP/)
_ESP_DIR = os.path.join(os.path.dirname(__file__), "AcmeESP")
if _ESP_DIR not in sys.path:
    sys.path.insert(0, _ESP_DIR)

from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc

from pyespUtil import connect_postgres_db
from config import CONFIG
from database import DatabaseConnection, DatabaseOperations, DatabaseError
from file_processor import (
    FileProcessor, CPUDetailsParser, ESCPParser, FileProcessingError,
)

logger = logging.getLogger(__name__)

_NAV_STYLE = {"padding-left": "1rem", "font-size": "0.75rem",
               "padding-top": "0.25rem", "padding-bottom": "0.25rem"}


# ── DB helpers ─────────────────────────────────────────────────────────────────

def _run(sql, params=None, fetch=False):
    conn = connect_postgres_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if fetch:
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        conn.commit()
    finally:
        conn.close()


def _client_opts():
    rows = _run(
        "SELECT cl_id, cl_name FROM sp_client ORDER BY cl_name",
        fetch=True,
    )
    return [{"label": r["cl_name"], "value": r["cl_id"]} for r in rows]


def _project_opts(cl_id):
    rows = _run(
        """SELECT pr_id, pr_name FROM sp_project
            WHERE sp_client_cl_id = %s ORDER BY pr_name""",
        (cl_id,), fetch=True,
    )
    return [{"label": r["pr_name"], "value": r["pr_id"]} for r in rows]


def _collection_opts(pr_id):
    rows = _run(
        """SELECT coll_id, coll_name FROM sp_collection
            WHERE sp_project_pr_id = %s ORDER BY coll_name""",
        (pr_id,), fetch=True,
    )
    return [{"label": r["coll_name"], "value": r["coll_id"]} for r in rows]


# ── ESP processing ─────────────────────────────────────────────────────────────

def _process_file(content_b64: str, filename: str, collection_id: int) -> dict:
    """
    Decode the uploaded ZIP, run the full AcmeESP pipeline for a single file,
    and return a results dict.
    """
    # Strip the data-URI prefix that dcc.Upload prepends
    if "," in content_b64:
        content_b64 = content_b64.split(",", 1)[1]
    file_bytes = base64.b64decode(content_b64)

    # Write to a staging area inside the ESP temp directory
    upload_dir = os.path.join(CONFIG.TEMP_DIR, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as fh:
        fh.write(file_bytes)

    results = {
        "filename": filename,
        "collection_id": collection_id,
        "db_record_id": None,
        "cpu_type": "",
        "server_model": "",
        "identity_records": 0,
        "metric_records": 0,
        "skipped_lines": 0,
        "error_lines": 0,
        "errors": [],
        "success": False,
    }

    db_conn = DatabaseConnection()
    try:
        db_ops = DatabaseOperations(db_conn)
        fp = FileProcessor()

        # 1. Insert sp_database record (uses filename to derive host/db name)
        database_id = db_ops.insert_database_record(str(collection_id), filename)
        results["db_record_id"] = database_id

        # 2. Extract ZIP contents to temp directory
        extracted = fp.extract_zip_file(file_path)
        logger.info("Extracted %d files from %s", len(extracted), filename)

        # 3. Parse CPU info file if present
        cpu_files = fp.find_files_by_pattern(CONFIG.TEMP_DIR, CONFIG.CPU_FILE_PATTERN)
        if cpu_files:
            cpu_type, server_model = CPUDetailsParser.parse_cpu_file(cpu_files[0])
            results["cpu_type"] = cpu_type
            results["server_model"] = server_model
            if cpu_type or server_model:
                db_ops.update_cpu_details(database_id, cpu_type, server_model)
        else:
            logger.warning("No CPU info file found in archive")

        # 4. Locate and parse ESCP CSV
        escp_files = fp.find_files_by_pattern(CONFIG.TEMP_DIR, CONFIG.ESCP_FILE_PATTERN)
        if not escp_files:
            raise FileProcessingError("No ESCP CSV file found inside the ZIP archive")

        identity_batch, metric_batch, stats = ESCPParser.parse_escp_file(
            escp_files[0], database_id
        )

        # 5. Batch-insert identity records
        for i in range(0, len(identity_batch), CONFIG.BATCH_SIZE):
            db_ops.insert_identity_batch(identity_batch[i : i + CONFIG.BATCH_SIZE])

        # 6. Batch-insert metric records
        for i in range(0, len(metric_batch), CONFIG.BATCH_SIZE):
            db_ops.insert_metric_batch(metric_batch[i : i + CONFIG.BATCH_SIZE])

        results.update({
            "identity_records": stats["identity_records"],
            "metric_records":   stats["metric_records"],
            "skipped_lines":    stats["skipped_lines"],
            "error_lines":      stats["error_lines"],
            "success":          True,
        })

    except (DatabaseError, FileProcessingError, ValueError, Exception) as exc:
        results["errors"].append(str(exc))
        logger.error("ESP processing error: %s", exc, exc_info=True)
    finally:
        fp.clear_temp_directory()
        if db_conn._pool:
            db_conn._pool.closeall()

    return results


# ── Results panel ──────────────────────────────────────────────────────────────

def _results_panel(r: dict) -> dbc.Card:
    color = "success" if r["success"] else "danger"
    icon  = "fas fa-check-circle" if r["success"] else "fas fa-times-circle"
    title = "File processed successfully" if r["success"] else "Processing failed"

    rows = [("File", r["filename"]),
            ("Collection ID", str(r["collection_id"]))]
    if r["db_record_id"] is not None:
        rows.append(("Database Record ID", str(r["db_record_id"])))
    if r["cpu_type"]:
        rows.append(("CPU Type", r["cpu_type"]))
    if r["server_model"]:
        rows.append(("Server Model", r["server_model"]))
    if r["success"]:
        rows += [
            ("Identity Records Loaded", f"{r['identity_records']:,}"),
            ("Metric Records Loaded",   f"{r['metric_records']:,}"),
            ("Lines Skipped",           f"{r['skipped_lines']:,}"),
            ("Parse Errors",            f"{r['error_lines']:,}"),
        ]

    table = dbc.Table(
        html.Tbody([html.Tr([html.Th(k, style={"width": "45%"}), html.Td(v)])
                    for k, v in rows]),
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


# ── Page layout ────────────────────────────────────────────────────────────────

def generate_load_file_page():
    return html.Div([
        html.H2("Load ESP Collection File"),
        html.Hr(className="mb-4"),

        # ── Step 1: file upload ───────────────────────────────────────────────
        dbc.Card([
            dbc.CardHeader(
                html.Span([
                    dbc.Badge("1", color="primary", className="me-2"),
                    "Select ZIP File",
                ], className="fw-semibold")
            ),
            dbc.CardBody([
                dcc.Upload(
                    id="lf-upload",
                    children=html.Div([
                        html.I(className="fas fa-file-archive fa-3x text-muted mb-2 d-block"),
                        html.Span("Drag and drop an ESCP ZIP file here, or "),
                        html.A("click to browse", style={"cursor": "pointer",
                                                         "textDecoration": "underline"}),
                    ], className="text-center py-4"),
                    style={
                        "borderWidth": "2px",
                        "borderStyle": "dashed",
                        "borderRadius": "8px",
                        "borderColor": "#ced4da",
                        "backgroundColor": "#f8f9fa",
                        "cursor": "pointer",
                    },
                    accept=".zip",
                    multiple=False,
                ),
                html.Div(id="lf-upload-status", className="mt-2"),
                # Hidden stores
                dcc.Store(id="lf-file-store"),
            ]),
        ], className="mb-3"),

        # ── Step 2: associate with a collection ───────────────────────────────
        dbc.Card([
            dbc.CardHeader(
                html.Span([
                    dbc.Badge("2", color="primary", className="me-2"),
                    "Associate with Collection",
                ], className="fw-semibold")
            ),
            dbc.CardBody(
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Client", className="fw-semibold"),
                        dcc.Dropdown(
                            id="lf-client-dd",
                            options=_client_opts(),
                            placeholder="Select a client…",
                            clearable=True,
                        ),
                    ], width=4),
                    dbc.Col([
                        dbc.Label("Project", className="fw-semibold"),
                        dcc.Dropdown(
                            id="lf-project-dd",
                            options=[],
                            placeholder="Select a project…",
                            clearable=True,
                            disabled=True,
                        ),
                    ], width=4),
                    dbc.Col([
                        dbc.Label("Collection", className="fw-semibold"),
                        dcc.Dropdown(
                            id="lf-collection-dd",
                            options=[],
                            placeholder="Select a collection…",
                            clearable=True,
                            disabled=True,
                        ),
                    ], width=4),
                ], className="g-3"),
            ),
        ], className="mb-4"),

        # ── Step 3: process ───────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    [html.I(className="fas fa-cogs me-2"), "Process File"],
                    id="lf-process-btn",
                    color="primary",
                    size="lg",
                    disabled=True,
                ),
                className="text-center",
            ),
            className="mb-3",
        ),

        # ── Results (wrapped in Loading spinner) ──────────────────────────────
        dcc.Loading(
            html.Div(id="lf-results"),
            type="circle",
            color="#0d6efd",
        ),
    ])


# ── Callbacks ──────────────────────────────────────────────────────────────────

def register_callbacks(app):

    @app.callback(
        Output("lf-upload-status", "children"),
        Output("lf-file-store", "data"),
        Input("lf-upload", "contents"),
        State("lf-upload", "filename"),
        prevent_initial_call=True,
    )
    def _handle_upload(contents, filename):
        if not contents:
            return no_update, no_update
        if not filename.lower().endswith(".zip"):
            return (
                dbc.Alert("Only .zip files are accepted.", color="warning",
                          dismissable=True, className="mb-0 py-2"),
                no_update,
            )
        status = dbc.Alert(
            [html.I(className="fas fa-check-circle me-2"), f"Ready to load: {filename}"],
            color="success", className="mb-0 py-2",
        )
        return status, {"filename": filename, "content": contents}

    @app.callback(
        Output("lf-project-dd", "options"),
        Output("lf-project-dd", "value"),
        Output("lf-project-dd", "disabled"),
        Input("lf-client-dd", "value"),
        prevent_initial_call=True,
    )
    def _update_projects(client_id):
        if not client_id:
            return [], None, True
        return _project_opts(client_id), None, False

    @app.callback(
        Output("lf-collection-dd", "options"),
        Output("lf-collection-dd", "value"),
        Output("lf-collection-dd", "disabled"),
        Input("lf-project-dd", "value"),
        prevent_initial_call=True,
    )
    def _update_collections(project_id):
        if not project_id:
            return [], None, True
        return _collection_opts(project_id), None, False

    @app.callback(
        Output("lf-process-btn", "disabled"),
        Input("lf-file-store", "data"),
        Input("lf-collection-dd", "value"),
    )
    def _toggle_button(file_data, collection_id):
        return not (file_data and collection_id)

    @app.callback(
        Output("lf-results", "children"),
        Input("lf-process-btn", "n_clicks"),
        State("lf-file-store", "data"),
        State("lf-collection-dd", "value"),
        prevent_initial_call=True,
    )
    def _run_processing(_, file_data, collection_id):
        if not file_data or not collection_id:
            return no_update
        results = _process_file(
            file_data["content"],
            file_data["filename"],
            collection_id,
        )
        return _results_panel(results)
