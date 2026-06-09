# AstraNotes

A local-first, multi-user note-taking web application built for CSEN 296B. AstraNotes takes a requirement set through the full AI-assisted software development lifecycle — requirements, architecture, UML design, traceability, implementation, testing, and CI/CD — with human validation at every step.

Notes are stored as individual JSON files on the local machine. There is no network dependency and no external service.

## Features

- **Multi-user authentication** — register and log in; passwords hashed with PBKDF2-SHA256 via Werkzeug (FR-08)
- **Create, edit, duplicate, delete notes** with title, body, and comma-separated tags (FR-01, FR-02, FR-03, FR-06)
- **Private notes** — toggle a lock flag per note; displayed with a 🔒 icon (FR-04 / SPR-01)
- **Search** — case-insensitive match across title, body, tags, and note ID prefix (FR-07)
- **Tag filter** — click any tag chip to filter the note list; clear with ✕
- **Share notes** — deep-copy a note to another user's account; recipient gets an independent copy tagged `shared-by-{user}`
- **Live refresh** — page auto-reloads when a new shared note arrives (polls every 5 seconds)
- **Admin dashboard** — aggregate stats (note count, user count, storage used) and a live audit log of every action
- **PST/PDT timestamps** — all displayed times converted from UTC
- **Per-user data isolation** — each user's notes stored in a separate directory under `~/.astranotes/data/{user_id}/`
- **Persistence** across sessions — every note is a JSON file; no database required (FR-05)

## Architecture

AstraNotes uses a strict layered architecture (NFR-02). Each layer is one package under `src/astranotes/`:

| Package | Responsibility |
|---|---|
| `models` | `Note` and `User` dataclasses, domain exceptions |
| `validation` | `ValidationLayer` — input rules (non-empty title, min length) |
| `repository` | `NoteRepository` interface + `JsonFileRepository`; `UserRepository` |
| `service` | `NoteService` — coordinates operations, depends on the repository *interface* |
| `web` | Flask web UI — routes, Jinja2 templates, session auth |
| `cli` | Terminal menu shell |
| `privacy` | Reserved for `PrivacyService` (Fernet encryption — designed, deferred) |

`NoteService` depends on the abstract `NoteRepository`, not the concrete `JsonFileRepository`, so the storage backend can be swapped without touching business logic.

## Requirements

- Python 3.9 or newer
- Dependencies in `requirements.txt`

## Setup

```bash
# from the AstraNotes/ project root
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the web app

```bash
python3 src/astranotes/web/app.py
```

Open `http://localhost:5000` in your browser. Click **Register** to create an account and get started.

## Running the tests

```bash
python3 -m pytest tests/ -v
```

All 17 tests should pass. Tests use temporary directories and never touch the real `~/.astranotes/data/` store.

To run with coverage:

```bash
python3 -m pytest tests/ -v --cov=src/astranotes --cov-report=term-missing --cov-config=.coveragerc
```

## CI/CD

GitHub Actions runs on every push to `main` or `feature/**`:

- **Test matrix** — Python 3.9 and 3.11
- **SAST scan** — Bandit static analysis
- **Secrets scan** — grep for hardcoded credentials
- **Coverage gate** — 60% minimum on service/model/repository layers

## Repository layout

```
AstraNotes/
├── README.md
├── requirements.txt
├── .coveragerc
├── .github/workflows/ci.yml
├── planning/                 # requirements, user stories, backlog, sprint-zero plan
├── docs/
│   ├── requirements/         # initial + refined requirement baselines
│   ├── architecture/         # UML diagrams + architecture decision log
│   ├── traceability/         # requirements-to-UML traceability matrix
│   └── process/              # working agreement, DoD, git workflow, test planning
├── src/astranotes/           # application source (one package per layer)
└── tests/                    # pytest unit tests
```

## SDLC artifacts

- **Requirements & planning** — `planning/`, `docs/requirements/`
- **Architecture & UML** — `docs/architecture/`
- **Traceability** — `docs/traceability/`
- **Implementation** — `src/astranotes/`
- **Testing** — `tests/`, `docs/process/`
- **CI/CD** — `.github/workflows/ci.yml`

## AI-assisted development

AI was used as a drafting and cross-checking partner across the entire SDLC — requirements generation, BDD Gherkin scenarios, architecture documents, UML diagrams, test generation, and the web UI. Every AI output was reviewed and validated. Gaps identified during review (e.g. search not matching tags, share not preserving `is_private`) were caught and fixed by human oversight. The accept/refine/reject record is in `docs/traceability/`.

## Data storage

Notes are stored at `~/.astranotes/data/{user_id}/{note_id}.json`. Users are stored at `~/.astranotes/users/`. Nothing is written inside the project directory.
