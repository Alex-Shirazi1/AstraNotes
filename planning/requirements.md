# AstraNotes — Requirements

**Source:** Week 1.2 Submission 2 — Initial Requirement Set
**Student:** Alex Shirazi
**Project:** AstraNotes
**Technical Path:** Python

---

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall allow a user to create a new text note with a title and body. |
| FR-02 | The system shall allow a user to edit an existing note and save the updated content, updating the last-modified timestamp automatically. |
| FR-03 | The system shall allow a user to delete a note from the local collection by note identifier. |
| FR-04 | The system shall allow a user to mark a note as private, which flags it for encryption handling by the privacy service. |
| FR-05 | The system shall persist all notes to local file storage and restore them on application startup so that data survives between sessions. |
| FR-06 | The system shall support note metadata including a unique identifier (UUID), created date, last modified date, and user-defined tags. |
| FR-07 | The system shall allow a user to search notes by title or body content using keyword matching and return all matching results. |
| FR-08 | The system shall display notes in a sorted list, ordered by last-modified date by default. |

---

## Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | The system shall handle a local collection of up to 500 notes without noticeable lag, completing note listing and keyword search within 2 seconds. |
| NFR-02 | The system architecture shall separate core business logic from storage and presentation concerns so that each layer can be reviewed, tested, or replaced independently. |
| NFR-03 | The application shall start and display the user's note list within 3 seconds on a machine meeting minimum development hardware specifications. |

---

## Security, Privacy, Reliability, and Governance Requirements

| ID | Requirement |
|---|---|
| SPR-01 | Private notes shall be encrypted at rest using Fernet symmetric encryption via Python's `cryptography` library so that raw note content is never stored in plaintext on disk. |
| SPR-02 | The system shall catch all storage-related failures (file not found, permission denied, corrupt data) and surface clear, non-technical error messages instead of crashing or exposing stack traces. |
| SPR-03 | All core components (repository, privacy service, validation layer) shall have at least one automated unit test verifying their primary behavior before each milestone delivery. |
| SPR-04 | Any third-party library introduced into the project shall be documented with its purpose and license; unverified or unnecessary dependencies shall be avoided. |

---

## Traceability

Each requirement maps to one or more user stories in `user-stories.md` and one or more backlog items in `backlog.md`. The traceability chain is:

**Requirements → User Stories → Acceptance Criteria → Backlog → Sprint Zero Plan**
