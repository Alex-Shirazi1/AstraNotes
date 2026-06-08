"""
astranotes.web.app
Flask web UI layer for AstraNotes.
Traces to: FR-01, FR-02, FR-03, FR-04, FR-06, FR-07, FR-08
Design doc: docs/architecture/AstraNotes_WebUI_Design.pdf

New presentation layer only — wires directly to existing NoteService and
JsonFileRepository without modifying any core business logic (NFR-02).
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from flask import Flask, flash, redirect, render_template, request, url_for

from astranotes.models.note import (
    Note,
    NoteNotFoundError,
    StoragePersistenceError,
    ValidationError,
)
from astranotes.repository.json_file_repository import JsonFileRepository
from astranotes.service.note_service import NoteService
from astranotes.validation.validation_layer import ValidationLayer

DATA_DIR = Path.home() / ".astranotes" / "data"
_LOG_PATH = Path.home() / ".astranotes" / "astranotes_actions.log"
_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(_LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("astranotes.web")

app = Flask(__name__)
app.secret_key = "astranotes-dev-secret"  # required for flash messages only


def _build_components() -> tuple[NoteService, JsonFileRepository, ValidationLayer]:
    repo = JsonFileRepository(DATA_DIR)
    validator = ValidationLayer()
    service = NoteService(repo=repo, validator=validator)
    return service, repo, validator


# GET / — FR-08: list all notes sorted by modified_at desc
# GET /?q= — FR-07: keyword search
@app.route("/", methods=["GET"])
def index():
    service, _, _ = _build_components()
    q = request.args.get("q", "").strip()
    if q:
        try:
            result = service.search(q)
            notes = result.notes
            logger.info("SEARCH keyword=%r hits=%d", q, len(notes))
        except ValueError as exc:
            flash(str(exc), "error")
            logger.warning("SEARCH_REJECTED keyword=%r reason=%s", q, exc)
            notes = service.list_sorted()
    else:
        notes = service.list_sorted()
        logger.info("VIEW_LIST count=%d", len(notes))
    return render_template("index.html", notes=notes, query=q)


# POST /notes — FR-01, FR-04, FR-06: create note with title, body, tags, is_private
@app.route("/notes", methods=["POST"])
def create_note():
    _, repo, validator = _build_components()
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    tags_raw = request.form.get("tags", "").strip()
    is_private = request.form.get("is_private") == "on"
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
    try:
        note = Note(title=title, body=body, tags=tags, is_private=is_private)
        validator.validate_note(note)
        repo.save(note)
        logger.info("CREATE id=%s title=%r tags=%r private=%s", note.id, title, tags, is_private)
        flash(f"Note \"{note.title}\" created.", "success")
    except ValidationError as exc:
        logger.warning("CREATE_REJECTED title=%r field=%s reason=%s", title, exc.field_name, exc.message)
        flash(f"Could not create note: {exc.message}", "error")
    except StoragePersistenceError as exc:
        logger.error("CREATE_STORAGE_ERROR title=%r error=%s", title, exc.message)
        flash(f"Storage error: {exc.message}", "error")
    return redirect(url_for("index"))


# POST /notes/<id>/edit — FR-02: edit title and body
@app.route("/notes/<note_id>/edit", methods=["POST"])
def edit_note(note_id: str):
    service, _, _ = _build_components()
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    try:
        service.edit(note_id, title, body)
        logger.info("EDIT id=%s title=%r", note_id, title)
        flash("Note updated.", "success")
    except ValidationError as exc:
        logger.warning("EDIT_REJECTED id=%s field=%s reason=%s", note_id, exc.field_name, exc.message)
        flash(f"Validation error: {exc.message}", "error")
    except NoteNotFoundError:
        logger.warning("EDIT_NOT_FOUND id=%s", note_id)
        flash("Note not found.", "error")
    except StoragePersistenceError as exc:
        logger.error("EDIT_STORAGE_ERROR id=%s error=%s", note_id, exc.message)
        flash(f"Storage error: {exc.message}", "error")
    return redirect(url_for("index"))


# POST /notes/<id>/delete — FR-03: delete note by ID
@app.route("/notes/<note_id>/delete", methods=["POST"])
def delete_note(note_id: str):
    service, _, _ = _build_components()
    try:
        service.delete(note_id)
        logger.info("DELETE id=%s", note_id)
        flash("Note deleted.", "success")
    except NoteNotFoundError:
        logger.warning("DELETE_NOT_FOUND id=%s", note_id)
        flash("Note not found.", "error")
    except StoragePersistenceError as exc:
        logger.error("DELETE_STORAGE_ERROR id=%s error=%s", note_id, exc.message)
        flash(f"Storage error: {exc.message}", "error")
    return redirect(url_for("index"))


# POST /notes/<id>/duplicate — duplicate a note
@app.route("/notes/<note_id>/duplicate", methods=["POST"])
def duplicate_note(note_id: str):
    _, repo, validator = _build_components()
    try:
        original = repo.get(note_id)
        copy = Note(
            title=f"Copy of {original.title}",
            body=original.body,
            tags=list(original.tags),
            is_private=original.is_private,
        )
        validator.validate_note(copy)
        repo.save(copy)
        logger.info("DUPLICATE source=%s new=%s title=%r", note_id, copy.id, copy.title)
        flash(f"Duplicated as \"{copy.title}\".", "success")
    except NoteNotFoundError:
        logger.warning("DUPLICATE_NOT_FOUND id=%s", note_id)
        flash("Note not found.", "error")
    except StoragePersistenceError as exc:
        logger.error("DUPLICATE_STORAGE_ERROR id=%s error=%s", note_id, exc.message)
        flash(f"Storage error: {exc.message}", "error")
    return redirect(url_for("index"))


# GET /admin — operational health dashboard
@app.route("/admin", methods=["GET"])
def admin():
    repo = JsonFileRepository(DATA_DIR)
    notes = repo.list_all()
    total_notes = len(notes)

    storage_bytes = 0
    for note in notes:
        p = DATA_DIR / f"{note.id}.json"
        if p.exists():
            storage_bytes += p.stat().st_size

    avg_body = round(sum(len(n.body) for n in notes) / total_notes, 1) if total_notes else 0.0
    storage_ok = DATA_DIR.exists() and DATA_DIR.is_dir()

    recent_logs: list[str] = []
    if _LOG_PATH.exists():
        lines = _LOG_PATH.read_text(encoding="utf-8").splitlines()
        recent_logs = lines[-25:][::-1]  # last 25, newest first

    logger.info("ADMIN_VIEW notes=%d storage_bytes=%d", total_notes, storage_bytes)
    return render_template(
        "admin.html",
        total_notes=total_notes,
        storage_bytes=storage_bytes,
        storage_kb=round(storage_bytes / 1024, 2),
        avg_body=avg_body,
        storage_ok=storage_ok,
        storage_path=str(DATA_DIR),
        recent_logs=recent_logs,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
