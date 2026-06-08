# AstraNotes

A local-first, single-user note-taking application built for CSEN 296. AstraNotes
takes a requirement set through the full software development lifecycle —
requirements, architecture, UML design, traceability, implementation, and
testing — using AI as a collaborative drafting tool with human validation at
every step.

Notes are stored as individual JSON files on the local machine. There is no
network dependency and no external service.

## Features

- **Create notes** with a title, body, and optional comma-separated tags (FR-01, FR-06)
- **View all notes** sorted by last-modified date, newest first (FR-08)
- **Search notes** by keyword across title and body, case-insensitive (FR-07)
- **Delete notes** by ID with a confirmation prompt (FR-03)
- **Persistence** across sessions — every note is a JSON file under `~/.astranotes/data/` (FR-05)
- Automatic metadata: UUID, UTC `created_at` / `modified_at` timestamps (FR-06)
- Clear, non-technical error messages for storage and validation failures (SPR-02)

> **Scope note:** Private-note encryption (FR-04 / SPR-01) and in-CLI editing
> (FR-02) are designed in the architecture and traceability artifacts but are
> deferred slices. The `PrivacyService` / `SecureNote` design and the reason for
> deferral (key-management strategy) are documented in
> `docs/traceability/` and `docs/architecture/`. `NoteService.edit()` is
> implemented and unit-tested but is not yet wired into the CLI menu.

## Architecture

AstraNotes uses a layered architecture with strict separation between business
logic, storage, and presentation (NFR-02). Each layer is one package under
`src/astranotes/`:

| Package | Responsibility |
|---|---|
| `models` | `Note` dataclass and domain exceptions |
| `validation` | `ValidationLayer` — input rules (e.g. non-empty title) |
| `repository` | `NoteRepository` interface + `JsonFileRepository` (JSON-per-note on disk) |
| `service` | `NoteService` — coordinates operations, depends on the repository *interface* |
| `cli` | Terminal menu shell (entry point) |
| `privacy` | Reserved for `PrivacyService` (Fernet encryption — deferred slice) |

`NoteService` depends on the abstract `NoteRepository`, not the concrete
`JsonFileRepository`, so the storage backend can be swapped without touching
business logic.

## Requirements

- Python 3.9 or newer
- Dependencies listed in `requirements.txt` (`cryptography` for the deferred
  privacy slice)

## Setup

```bash
# from the AstraNotes/ project root
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

To run the test suite you also need pytest:

```bash
pip install pytest
```

## Usage

Run the CLI from the `src/` directory:

```bash
cd src
python -m astranotes.cli.main
```

You will see a menu:

```
  [1] View all notes
  [2] Create a note
  [3] Search notes
  [4] Delete a note
  [q] Quit
```

Notes are written to `~/.astranotes/data/` as `{uuid}.json` and reloaded
automatically on the next launch.

## Running the tests

From the project root:

```bash
python -m pytest tests/ -v
```

All 17 tests should pass. Tests use temporary directories, so they never touch
the real `~/.astranotes/data/` store (SPR-03).

## Repository layout

```
AstraNotes/
├── README.md
├── requirements.txt
├── planning/                 # requirements, user stories, backlog, sprint-zero plan
├── docs/
│   ├── requirements/         # initial + refined requirement baselines (PDF)
│   ├── architecture/         # class, object, package, activity, deployment, use-case diagrams + ADL
│   ├── traceability/         # requirements-to-UML traceability matrix
│   └── process/              # working agreement, DoD, git workflow, test planning, env setup
├── src/astranotes/           # application source (one package per layer)
└── tests/                    # pytest unit + integration tests
```

## SDLC artifacts

This repository contains the complete final project package developed across the
quarter:

- **Requirements & planning** — `planning/*.md`, `docs/requirements/*.pdf`
- **Architecture & UML** — `docs/architecture/*.pdf`
- **Traceability & validation** — `docs/traceability/*.pdf`
- **Implementation** — `src/astranotes/`
- **Testing** — `tests/`, `docs/process/Alex_Shirazi_Test_planning.pdf`,
  `docs/process/Alex_Shirazi_Week9_Test_Improvement_Log.pdf`
- **Process / security / deployment** — `docs/process/`,
  `docs/architecture/Deployment Diagram.pdf`,
  `docs/architecture/AlexShirazi_ArchDecisionLog.pdf`

## AI-assisted development

AI was used as a drafting and cross-checking partner across the SDLC — never as
a final authority. Each AI suggestion was accepted with modification, changed,
or rejected with a documented reason. The accept / refine / reject record is in
the "How AI Helped" section of the traceability matrix
(`docs/traceability/submission_traceability_matrix_Alex_Shirazi.pdf`).
