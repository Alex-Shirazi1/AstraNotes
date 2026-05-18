# AstraNotes — Sprint Zero Plan

**Sprint Duration:** Week 2.2 through end of Week 3
**Goal:** Establish the project foundation so that Sprint 1 can begin implementation with zero ambiguity about structure, tools, workflow, or architecture.

Sprint Zero is not a feature sprint. No user stories are marked Done at the end of Sprint Zero. The sprint is complete when the working environment, architecture skeleton, and planning artifacts are in place and verified.

---

## Sprint Zero Objectives

### 1. Repository and Project Structure Setup

- Initialize a Python project repository with a clear folder structure:
  - `astranotes/` — application source (models, repository, privacy, validation, cli)
  - `tests/` — unit tests mirroring the source structure
  - `planning/` — requirements, user stories, backlog, sprint plans
  - `docs/` — architecture decision log, ai_log.md
- Add a `requirements.txt` listing only verified, licensed dependencies (SPR-04).
- Add a `.gitignore` appropriate for Python projects.
- Confirm the project runs with `python -m astranotes` without errors (even if the CLI only prints a placeholder).

**DoD check:** Repository structure matches the architecture from Submission 1. No untracked dependencies. Project runs cleanly.

---

### 2. Note Data Model Implementation

- Implement the `Note` dataclass with all fields defined in the architecture: `id` (UUID), `title` (str), `body` (str), `is_private` (bool), `created_at` (datetime), `modified_at` (datetime), `tags` (list of str).
- Write at least one unit test confirming: a Note can be instantiated with valid fields, created_at and modified_at are set automatically, and id is a valid UUID.

**DoD check:** Note model is explainable, tested, and traced to FR-01 and FR-06.

---

### 3. NoteRepository Interface and JsonFileRepository Stub

- Implement the abstract `NoteRepository` interface with method signatures: `save`, `get`, `list_all`, `update`, `delete`.
- Implement `JsonFileRepository(NoteRepository)` that reads and writes individual `.json` files per note to a local data directory.
- Write at least one unit test confirming a note can be saved to a temp directory and retrieved with matching fields.

**DoD check:** Repository interface is in place. JsonFileRepository is tested end-to-end for a basic save/load round trip. Traced to FR-05.

---

### 4. PrivacyService Skeleton

- Implement `PrivacyService` with `encrypt(body: str) -> bytes` and `decrypt(data: bytes) -> str` using Fernet symmetric encryption via the `cryptography` library.
- Write at least one unit test confirming: encrypting a string and decrypting it returns the original value, and the encrypted output is not equal to the plaintext input.

**DoD check:** PrivacyService is tested for basic round-trip. No private note content is ever stored in plaintext. Traced to SPR-01 and FR-04.

**Risk note:** Key management is deferred to Sprint 1. For Sprint Zero, a hardcoded test key is acceptable in the test suite only. Production key strategy must be resolved before US-04 is marked Done.

---

### 5. ValidationLayer Skeleton

- Implement a `ValidationLayer` with at least one rule: a note title must be a non-empty string.
- Raise a `ValidationError` (custom exception) when the rule is violated.
- Write at least one unit test confirming that an empty title raises `ValidationError` and a valid title passes.

**DoD check:** ValidationLayer is tested and traced to FR-01.

---

### 6. Workflow Readiness Check

- Confirm that `ai_log.md` and `backlog.md` are in place and reflect at least the Sprint Zero work.
- Confirm that the Architecture Decision Log (Submission 1) is accessible in the project docs folder and up to date.
- Confirm that the Working Agreement (Submission 2.1) and Definition of Done (Submission 2.1) are accessible and applied to every Sprint Zero task.
- Run all unit tests and confirm 100% pass rate before Sprint Zero is closed.

**DoD check:** All planning artifacts are in place. Test suite is green. Sprint Zero is not closed until every objective above has a passing test or a verified artifact.

---

## Sprint Zero Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Fernet key management unclear for production use | Medium | Defer to Sprint 1; use test key only in Sprint Zero. Document decision in ADL. |
| JSON file-per-note approach has edge cases (concurrent writes, corrupt files) | Low for solo project | Implement basic error handling for missing/corrupt files in Sprint Zero. Defer advanced cases. |
| Sprint Zero expands into feature work | Medium | No user story is marked Done in Sprint Zero. Any feature work discovered is added to the backlog and deferred to Sprint 1. |
| Architecture from Submission 1 needs adjustment once code is written | Low-Medium | Sprint Zero skeleton work is the test. If the architecture needs adjustment, update the ADL before Sprint 1 begins. |

---

## Sprint Zero Exit Criteria

Sprint Zero is complete when all of the following are true:

- [ ] Project repository is initialized with the folder structure above.
- [ ] `Note` dataclass is implemented and has passing unit tests.
- [ ] `NoteRepository` interface and `JsonFileRepository` are implemented with a passing save/load test.
- [ ] `PrivacyService` is implemented with a passing encrypt/decrypt test.
- [ ] `ValidationLayer` is implemented with a passing title validation test.
- [ ] `ai_log.md` and `backlog.md` are populated and current.
- [ ] All tests pass.
- [ ] No user story from the backlog is prematurely marked Done.
