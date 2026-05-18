# AstraNotes — Prioritized Backlog

**Prioritization method:** Value/Risk — stories that deliver core user value or de-risk the architecture appear first. Stories that depend on a stable core appear later.

| Priority | Story ID | Title | Requirement(s) | Rationale |
|---|---|---|---|---|
| 1 | US-05 | Persist Notes Across Sessions | FR-05, NFR-03 | Nothing else works if notes don't survive sessions. Foundation for all other stories. |
| 2 | US-01 | Create a Note | FR-01, FR-06 | Primary user action. Validates the Note model, NoteRepository interface, and ValidationLayer end-to-end. |
| 3 | US-04 | Mark a Note as Private | FR-04, SPR-01 | Highest architectural risk. PrivacyService must be verified before any save/load path is considered stable. |
| 4 | US-02 | Edit an Existing Note | FR-02 | Depends on create and persist being solid. Validates the update path through NoteRepository. |
| 5 | US-03 | Delete a Note | FR-03 | Depends on create and persist. Validates the delete path and error handling for missing notes. |
| 6 | US-07 | View Notes Sorted by Last Modified | FR-08 | Depends on create and persist. Low implementation risk; confirms sort logic on the list view. |
| 7 | US-06 | Search Notes by Keyword | FR-07, NFR-01 | Depends on a populated note collection. Performance requirement (2s for 500 notes) should be validated with real data. |
| 8 | US-08 | Tag a Note | FR-06 | Metadata enhancement. Depends on stable note model and edit flow. Lowest priority for Sprint Zero. |

---

## Backlog Notes

**US-05 before US-01:** It might seem natural to create before persisting, but the persistence layer is what validates the entire storage architecture from Submission 1. Building it first means US-01, US-02, and US-04 all test against a real storage backend rather than an in-memory stub.

**US-04 third:** The PrivacyService is the highest architectural risk in the project. It touches every save and load operation for private notes. Addressing it early prevents a situation where the full CRUD loop is built and then has to be re-threaded through an encryption layer later.

**US-06 and US-07 after CRUD:** Sort and search are read operations that require a populated note collection to be meaningful. They are deprioritized until the write path (create, edit, delete, persist) is stable.

**US-08 last:** Tags are a metadata enhancement. They add value but do not change the core architecture. They are parked at the end of this backlog and are candidates for Sprint 1 or Sprint 2 depending on progress.
