"""
astranotes.web.app
Flask web UI layer for AstraNotes — multi-user edition.
Traces to: FR-01, FR-02, FR-03, FR-04, FR-06, FR-07, FR-08
Design doc: docs/architecture/AstraNotes_WebUI_Design.pdf

Architecture:
  View   — Jinja2 templates (index.html, login.html, register.html, admin.html)
  Controller — Flask routes (this file)
  Model  — NoteService + JsonFileRepository + UserRepository (existing packages, unchanged)

Each user gets an isolated notes directory:
  ~/.astranotes/data/{user_id}/
"""
import logging
import os
import sys
from datetime import timezone, timedelta
from functools import wraps
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from flask import (Flask, flash, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from astranotes.models.note import (Note, NoteNotFoundError,
                                     StoragePersistenceError, ValidationError)
from astranotes.models.user import User, UserAlreadyExistsError
from astranotes.repository.json_file_repository import JsonFileRepository
from astranotes.repository.user_repository import UserRepository
from astranotes.service.note_service import NoteService
from astranotes.validation.validation_layer import ValidationLayer

# ── Paths ──────────────────────────────────────────────────────────
BASE_DIR   = Path.home() / ".astranotes"
USERS_DIR  = BASE_DIR / "users"
DATA_ROOT  = BASE_DIR / "data"
_LOG_PATH  = BASE_DIR / "astranotes_actions.log"
BASE_DIR.mkdir(parents=True, exist_ok=True)

# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(_LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("astranotes.web")

# ── Template filters ───────────────────────────────────────────────
_PST = timezone(timedelta(hours=-8))
_PDT = timezone(timedelta(hours=-7))

def _to_pst(dt):
    """Convert a UTC datetime to PST/PDT string for display."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    month = dt.month
    tz = _PDT if 3 < month < 11 else _PST
    label = "PDT" if tz is _PDT else "PST"
    local = dt.astimezone(tz)
    return local.strftime(f"%Y-%m-%d %H:%M {label}")

# ── Flask app ──────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "astranotes-dev-secret-change-in-prod"
app.jinja_env.filters["pst"] = _to_pst

user_repo = UserRepository(USERS_DIR)


# ── Seed admin singleton ───────────────────────────────────────────
def _seed_admin() -> None:
    """Ensure exactly one admin account exists on every startup.

    Credentials come from env vars so nothing sensitive lives in source.
    If the account already exists it is left untouched (true singleton).

    Defaults (fine for demo / local dev):
        username: admin
        password: admin

    Override for a real deployment:
        ASTRANOTES_ADMIN_USER=alex ASTRANOTES_ADMIN_PASS=s3cure flask run
    """
    admin_user = os.environ.get("ASTRANOTES_ADMIN_USER", "admin")
    admin_pass = os.environ.get("ASTRANOTES_ADMIN_PASS", "admin")
    if not user_repo.username_exists(admin_user):
        user = User(
            username=admin_user,
            password_hash=generate_password_hash(admin_pass, method="pbkdf2:sha256"),
            role="admin",
        )
        user_repo.save(user)
        logger.info("SEED_ADMIN created singleton admin user=%r", admin_user)
    else:
        logger.debug("SEED_ADMIN admin user=%r already exists, skipping", admin_user)


_seed_admin()


# ── Helpers ────────────────────────────────────────────────────────

def _note_service() -> tuple[NoteService, JsonFileRepository]:
    """Build NoteService scoped to the current user's data directory."""
    user_id = session["user_id"]
    data_dir = DATA_ROOT / user_id
    repo = JsonFileRepository(data_dir)
    return NoteService(repo=repo, validator=ValidationLayer()), repo


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated




# ── Auth routes ────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = user_repo.get_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"]   = user.id
            session["username"]  = user.username
            session["role"]      = user.role
            logger.info("LOGIN user=%r role=%s", username, user.role)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("index"))
        logger.warning("LOGIN_FAILED user=%r", username)
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")
        if not username or len(username) < 2:
            flash("Username must be at least 2 characters.", "error")
        elif not password or len(password) < 4:
            flash("Password must be at least 4 characters.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif user_repo.username_exists(username):
            flash("That username is already taken.", "error")
        else:
            user = User(
                username=username,
                password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
            )
            user_repo.save(user)
            session.clear()
            session["user_id"]  = user.id
            session["username"] = user.username
            session["role"]     = user.role
            logger.info("REGISTER user=%r id=%s role=%s", username, user.id, user.role)
            flash(f"Account created. Welcome, {username}!", "success")
            return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    username = session.get("username", "?")
    session.clear()
    logger.info("LOGOUT user=%r", username)
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


# ── Note routes (all login-required) ──────────────────────────────

@app.route("/", methods=["GET"])
@login_required
def index():
    service, _ = _note_service()
    q          = request.args.get("q", "").strip()
    active_tag = request.args.get("tag", "").strip()
    if q:
        try:
            result = service.search(q)
            notes  = result.notes
            logger.info("SEARCH user=%r keyword=%r hits=%d",
                        session["username"], q, len(notes))
        except ValueError as exc:
            flash(str(exc), "error")
            logger.warning("SEARCH_REJECTED user=%r keyword=%r reason=%s",
                           session["username"], q, exc)
            notes = service.list_sorted()
    elif active_tag:
        all_notes = service.list_sorted()
        notes = [n for n in all_notes if active_tag.lower() in [t.lower() for t in n.tags]]
        logger.info("TAG_FILTER user=%r tag=%r hits=%d",
                    session["username"], active_tag, len(notes))
    else:
        notes = service.list_sorted()
        logger.info("VIEW_LIST user=%r count=%d", session["username"], len(notes))
    other_users = [u.username for u in user_repo.list_all()
                   if u.username != session["username"]]
    return render_template("index.html", notes=notes, query=q,
                           active_tag=active_tag,
                           username=session["username"],
                           other_users=other_users)


@app.route("/notes", methods=["POST"])
@login_required
def create_note():
    _, repo = _note_service()
    title      = request.form.get("title", "").strip()
    body       = request.form.get("body", "").strip()
    tags_raw   = request.form.get("tags", "").strip()
    is_private = request.form.get("is_private") == "on"
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
    try:
        note = Note(title=title, body=body, tags=tags, is_private=is_private)
        ValidationLayer().validate_note(note)
        repo.save(note)
        logger.info("CREATE user=%r id=%s title=%r", session["username"], note.id, title)
        flash(f'Note "{note.title}" created.', "success")
    except ValidationError as exc:
        logger.warning("CREATE_REJECTED user=%r field=%s reason=%s",
                       session["username"], exc.field_name, exc.message)
        flash(f"Could not create note: {exc.message}", "error")
    except StoragePersistenceError as exc:
        flash(f"Storage error: {exc.message}", "error")
    return redirect(url_for("index"))


@app.route("/notes/<note_id>/edit", methods=["POST"])
@login_required
def edit_note(note_id: str):
    service, repo = _note_service()
    title      = request.form.get("title", "").strip()
    body       = request.form.get("body", "").strip()
    is_private = request.form.get("is_private") == "on"
    try:
        service.edit(note_id, title, body)
        # update is_private separately (not part of NoteService.edit signature)
        note = repo.get(note_id)
        note.is_private = is_private
        repo.update(note)
        logger.info("EDIT user=%r id=%s title=%r private=%s",
                    session["username"], note_id, title, is_private)
        flash("Note updated.", "success")
    except ValidationError as exc:
        flash(f"Validation error: {exc.message}", "error")
    except NoteNotFoundError:
        flash("Note not found.", "error")
    except StoragePersistenceError as exc:
        flash(f"Storage error: {exc.message}", "error")
    return redirect(url_for("index"))


@app.route("/notes/<note_id>/delete", methods=["POST"])
@login_required
def delete_note(note_id: str):
    service, _ = _note_service()
    try:
        service.delete(note_id)
        logger.info("DELETE user=%r id=%s", session["username"], note_id)
        flash("Note deleted.", "success")
    except NoteNotFoundError:
        flash("Note not found.", "error")
    except StoragePersistenceError as exc:
        flash(f"Storage error: {exc.message}", "error")
    return redirect(url_for("index"))


@app.route("/notes/<note_id>/duplicate", methods=["POST"])
@login_required
def duplicate_note(note_id: str):
    _, repo = _note_service()
    try:
        original = repo.get(note_id)
        copy = Note(
            title=f"Copy of {original.title}",
            body=original.body,
            tags=list(original.tags),
            is_private=original.is_private,
        )
        ValidationLayer().validate_note(copy)
        repo.save(copy)
        logger.info("DUPLICATE user=%r source=%s new=%s",
                    session["username"], note_id, copy.id)
        flash(f'Duplicated as "{copy.title}".', "success")
    except NoteNotFoundError:
        flash("Note not found.", "error")
    except StoragePersistenceError as exc:
        flash(f"Storage error: {exc.message}", "error")
    return redirect(url_for("index"))


@app.route("/notes/<note_id>/share", methods=["POST"])
@login_required
def share_note(note_id: str):
    _, repo = _note_service()
    target_username = request.form.get("target_username", "").strip()
    if not target_username:
        flash("Please select a user to share with.", "error")
        return redirect(url_for("index"))
    if target_username == session["username"]:
        flash("You can't share a note with yourself.", "error")
        return redirect(url_for("index"))
    target_user = user_repo.get_by_username(target_username)
    if not target_user:
        flash(f"User '{target_username}' not found.", "error")
        return redirect(url_for("index"))
    try:
        original = repo.get(note_id)
        shared_tag = f"shared-by-{session['username']}"
        copy = Note(
            title=original.title,
            body=original.body,
            tags=list(original.tags) + [shared_tag],
            is_private=original.is_private,
        )
        target_repo = JsonFileRepository(DATA_ROOT / target_user.id)
        ValidationLayer().validate_note(copy)
        target_repo.save(copy)
        logger.info("SHARE user=%r -> target=%r note_id=%s",
                    session["username"], target_username, note_id)
        flash(f'Note shared with {target_username}.', "success")
    except NoteNotFoundError:
        flash("Note not found.", "error")
    except StoragePersistenceError as exc:
        flash(f"Storage error: {exc.message}", "error")
    return redirect(url_for("index"))


# ── Live poll endpoint ─────────────────────────────────────────────
@app.route("/api/note-count")
@login_required
def note_count():
    from flask import jsonify
    _, repo = _note_service()
    return jsonify({"count": len(repo.list_all())})


# ── Admin dashboard ────────────────────────────────────────────────

@app.route("/admin", methods=["GET"])
@login_required
def admin():
    # Aggregate stats across ALL users
    all_users  = user_repo.list_all()
    total_users = len(all_users)
    total_notes = 0
    storage_bytes = 0

    for user in all_users:
        user_dir = DATA_ROOT / user.id
        if user_dir.exists():
            for p in user_dir.glob("*.json"):
                total_notes   += 1
                storage_bytes += p.stat().st_size

    # Current user's notes for avg body length
    _, repo = _note_service()
    my_notes = repo.list_all()
    avg_body = round(
        sum(len(n.body) for n in my_notes) / len(my_notes), 1
    ) if my_notes else 0.0

    storage_ok = DATA_ROOT.exists()

    recent_logs: list = []
    if _LOG_PATH.exists():
        lines = _LOG_PATH.read_text(encoding="utf-8").splitlines()
        recent_logs = lines[-25:][::-1]

    logger.info("ADMIN_VIEW user=%r total_users=%d total_notes=%d",
                session["username"], total_users, total_notes)
    return render_template(
        "admin.html",
        total_users=total_users,
        total_notes=total_notes,
        storage_bytes=storage_bytes,
        storage_kb=round(storage_bytes / 1024, 2),
        avg_body=avg_body,
        storage_ok=storage_ok,
        storage_path=str(DATA_ROOT),
        recent_logs=recent_logs,
        username=session["username"],
        users=all_users,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
