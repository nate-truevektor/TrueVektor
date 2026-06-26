"""
TrueVektor local web server.

Serves the browser UI and handles reading/writing inspection.yaml.

Start with:
    python -m truevektor
or:
    python -m truevektor.server
"""

from __future__ import annotations

from pathlib import Path

import yaml
from flask import Flask, jsonify, request, send_from_directory

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent
STATIC_DIR = _HERE / "static"
SETTINGS_PATH = Path.home() / ".truevektor" / "settings.yaml"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")

# The currently open inspection folder (set by POST /api/open)
_current_folder: Path | None = None


# ---------------------------------------------------------------------------
# Helpers — inspection.yaml
# ---------------------------------------------------------------------------

def _yaml_path() -> Path:
    if _current_folder is None:
        raise RuntimeError("No inspection folder open")
    return _current_folder / "inspection.yaml"


def _read_yaml() -> dict:
    with _yaml_path().open() as f:
        return yaml.safe_load(f) or {}


def _write_yaml(data: dict) -> None:
    """Atomically write inspection.yaml."""
    path = _yaml_path()
    tmp = path.with_suffix(".yaml.tmp")
    with tmp.open("w") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    tmp.replace(path)


def _folder_listing(path: Path) -> list[dict]:
    """Return sorted list of subdirectories with inspection.yaml flag."""
    entries = []
    try:
        for entry in sorted(path.iterdir(), key=lambda e: e.name.lower()):
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                has_yaml = (entry / "inspection.yaml").exists()
                entries.append({
                    "name": entry.name,
                    "path": str(entry),
                    "is_inspection": has_yaml,
                })
    except PermissionError:
        pass
    return entries


# ---------------------------------------------------------------------------
# Helpers — settings.yaml
# ---------------------------------------------------------------------------

_DEFAULT_SETTINGS: dict = {
    "company_name": "",
    "logo_path": "",
    "technician": {
        "name": "",
        "certification": "",
        "email": "",
        "phone": "",
    },
    "default_narrative": "",
    "equipment_presets": [],   # list of {name, detector, temperature_range}
    "anomaly_presets": [],     # list of {name, observation}
    "page2_sections":  [],     # list of {heading, body}
    "polygon_stroke_color": "#ff6400",
    "polygon_stroke_width": 2,
}


def _read_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return dict(_DEFAULT_SETTINGS)
    with SETTINGS_PATH.open() as f:
        data = yaml.safe_load(f) or {}
    merged = dict(_DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def _write_settings(data: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = SETTINGS_PATH.with_suffix(".yaml.tmp")
    with tmp.open("w") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    tmp.replace(SETTINGS_PATH)


def _new_inspection_scaffold(settings: dict) -> dict:
    """Build a blank inspection.yaml pre-filled from settings."""
    tech = settings.get("technician") or {}
    presets = settings.get("equipment_presets") or []

    equipment_list = [
        {
            "name": p.get("name") or "",
            "detector": p.get("detector") or "",
            "temperature_range": p.get("temperature_range") or "",
        }
        for p in presets
    ] or [{"name": "", "detector": "", "temperature_range": ""}]

    return {
        "client": {"name": ""},
        "property": {"name": "", "address": ""},
        "inspection": {
            "date": "",
            "report_date": "",
            "time_context": "",
            "ambient_f": 0,
            "rh_pct": 0,
            "wind_mph": 0,
            "narrative": settings.get("default_narrative") or "",
        },
        "technician": {
            "name": tech.get("name") or "",
            "certification": tech.get("certification") or "",
            "email": tech.get("email") or "",
            "phone": tech.get("phone") or "",
        },
        "equipment": equipment_list,
        "images": {
            "aerial_visual": "images/aerial-visual.png",
            "orthomosaic": None,
            "thermal_images_folder": None,
        },
        "anomalies": [],
    }


# ---------------------------------------------------------------------------
# Routes — UI
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")


# ---------------------------------------------------------------------------
# Routes — File browser (images)
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp"}


@app.route("/api/image")
def serve_image():
    """Serve an image file from an absolute local path (for canvas display)."""
    from flask import send_file
    raw = request.args.get("path", "")
    if not raw:
        return "No path", 400
    p = Path(raw).resolve()
    if p.suffix.lower() not in IMAGE_EXTENSIONS:
        return "Not an image file", 403
    if not p.is_file():
        return "Not found", 404
    return send_file(str(p))


@app.route("/api/list-files")
def list_files():
    """
    List image files and subdirectories in a given path.
    Query param: ?path=/abs/path   (defaults to inspection folder)
    Returns breadcrumb, subdirs, and image files.
    """
    raw = request.args.get("path", "")
    if raw:
        folder = Path(raw).expanduser().resolve()
    elif _current_folder:
        folder = _current_folder
    else:
        folder = Path.home()

    if not folder.exists() or not folder.is_dir():
        return jsonify({"error": f"Not a directory: {folder}"}), 400

    # Breadcrumb
    try:
        parts = folder.relative_to(Path.home()).parts
        breadcrumb = [{"name": "~", "path": str(Path.home())}]
        running = Path.home()
        for part in parts:
            running = running / part
            breadcrumb.append({"name": part, "path": str(running)})
    except ValueError:
        breadcrumb = [{"name": str(folder), "path": str(folder)}]

    subdirs = []
    files = []
    try:
        for entry in sorted(folder.iterdir(), key=lambda e: e.name.lower()):
            if entry.name.startswith("."):
                continue
            if entry.is_dir():
                subdirs.append({"name": entry.name, "path": str(entry)})
            elif entry.is_file() and entry.suffix.lower() in IMAGE_EXTENSIONS:
                files.append({"name": entry.name, "path": str(entry)})
    except PermissionError:
        pass

    return jsonify({
        "current": str(folder),
        "breadcrumb": breadcrumb,
        "parent": str(folder.parent) if folder != folder.parent else None,
        "subdirs": subdirs,
        "files": files,
    })


# ---------------------------------------------------------------------------
# Routes — Settings
# ---------------------------------------------------------------------------

@app.route("/api/settings")
def get_settings():
    return jsonify(_read_settings())


@app.route("/api/settings", methods=["POST"])
def save_settings():
    data = request.get_json(force=True)
    try:
        _write_settings(data)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Routes — Folder browser
# ---------------------------------------------------------------------------

@app.route("/api/browse")
def browse():
    """List directories. Query param: ?path=/some/dir (defaults to home)."""
    raw = request.args.get("path", "")
    folder = Path(raw).expanduser().resolve() if raw else Path.home()

    if not folder.exists() or not folder.is_dir():
        return jsonify({"error": f"Not a directory: {folder}"}), 400

    try:
        parts = folder.relative_to(Path.home()).parts
        breadcrumb = [{"name": "~", "path": str(Path.home())}]
        running = Path.home()
        for part in parts:
            running = running / part
            breadcrumb.append({"name": part, "path": str(running)})
    except ValueError:
        breadcrumb = [{"name": str(folder), "path": str(folder)}]

    return jsonify({
        "current": str(folder),
        "breadcrumb": breadcrumb,
        "entries": _folder_listing(folder),
        "parent": str(folder.parent) if folder != folder.parent else None,
    })


# ---------------------------------------------------------------------------
# Routes — Open / close inspection
# ---------------------------------------------------------------------------

@app.route("/api/open", methods=["POST"])
def open_inspection():
    """Open an inspection folder. Body: {"path": "/abs/path/to/folder"}"""
    global _current_folder

    data = request.get_json(force=True)
    folder = Path(data.get("path", "")).expanduser().resolve()

    if not folder.is_dir():
        return jsonify({"error": f"Not a directory: {folder}"}), 400

    yaml_file = folder / "inspection.yaml"
    _current_folder = folder

    if not yaml_file.exists():
        settings = _read_settings()
        scaffold = _new_inspection_scaffold(settings)
        _write_yaml(scaffold)
        return jsonify({"created": True, "path": str(folder)})

    return jsonify({"created": False, "path": str(folder)})


@app.route("/api/close", methods=["POST"])
def close_inspection():
    global _current_folder
    _current_folder = None
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Routes — Inspection data
# ---------------------------------------------------------------------------

@app.route("/api/inspection")
def get_inspection():
    if _current_folder is None:
        return jsonify({"error": "No inspection open"}), 400
    try:
        data = _read_yaml()
        return jsonify({"path": str(_current_folder), "data": data})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/inspection", methods=["POST"])
def save_inspection():
    if _current_folder is None:
        return jsonify({"error": "No inspection open"}), 400
    try:
        incoming = request.get_json(force=True)
        _write_yaml(incoming)
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Routes — Validation
# ---------------------------------------------------------------------------

@app.route("/api/validate")
def run_validate():
    if _current_folder is None:
        return jsonify({"error": "No inspection open"}), 400
    try:
        from truevektor.validator import validate
        result = validate(_current_folder)
        return jsonify({
            "ok": result.ok,
            "errors": result.errors,
            "warnings": result.warnings,
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Routes — Report generation
# ---------------------------------------------------------------------------

@app.route("/api/generate-report", methods=["POST"])
def generate_report():
    if _current_folder is None:
        return jsonify({"error": "No inspection open"}), 400
    try:
        from truevektor.report import generate_report as _gen
        settings = _read_settings()
        out_path = _gen(_current_folder, settings)
        return jsonify({"ok": True, "path": str(out_path)})
    except Exception as exc:
        import traceback
        return jsonify({"error": str(exc), "detail": traceback.format_exc()}), 500


@app.route("/api/download")
def download_file():
    """Serve a generated file by absolute path for browser download."""
    from flask import send_file
    raw = request.args.get("path", "")
    if not raw:
        return "No path", 400
    p = Path(raw).resolve()
    # Only allow files inside the current inspection folder
    if _current_folder is None or not str(p).startswith(str(_current_folder)):
        return "Forbidden", 403
    if not p.is_file():
        return "Not found", 404
    return send_file(
        str(p),
        as_attachment=True,
        download_name=p.name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run(host: str = "127.0.0.1", port: int = 5000, debug: bool = False) -> None:
    import webbrowser
    import threading
    url = f"http://{host}:{port}"
    if not debug:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"\n  TrueVektor running at {url}\n  Press Ctrl+C to quit.\n")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run(debug=True)
