# AI Interaction Log — AstraNotes

**Project:** AstraNotes | **Course:** CSEN 296 | **Student:** Alex Shirazi

This log captures the key GitHub Copilot interactions that influenced major architectural decisions, technology choices, and tradeoffs. Routine completions and trivial autocomplete suggestions are not included. Each entry shows the prompt, the suggestion, and whether it was accepted, refined, or rejected — and why.

---

## Interaction 1 — Storage Backend: JSON files vs. SQLite

**Week 3 | Decision: FR-05 storage strategy**

**My prompt to Copilot Chat:**
> I need to persist notes locally for a single-user app. Should I use a SQLite database or individual JSON files per note? The architecture needs to be testable without external dependencies.

**Copilot suggestion:**
```
For a single-user local app with a testability requirement, individual JSON files
per note are a strong choice:
- No database driver dependency, no setup required
- Each note is independently readable/writable — no locking issues
- Straightforward to mock in tests using tmp directories
- File-per-note makes backup and inspection trivial

SQLite is better when you need relational queries, transactions across multiple
records, or a collection larger than a few thousand records. For a note-taking app
under 500 notes (your NFR-01), JSON files are more than sufficient.

Suggested interface:
class NoteRepository(ABC):
    def save(self, note: Note) -> None: ...
    def get(self, note_id: str) -> Note: ...
    def list_all(self) -> List[Note]: ...
    def update(self, note: Note) -> None: ...
    def delete(self, note_id: str) -> None: ...
```

**Decision:** Accepted with modification. Adopted the JSON-per-note approach and the abstract `NoteRepository` interface exactly as suggested. Added `StoragePersistenceError` wrapping to prevent raw OS exceptions from leaking to the CLI (SPR-02 constraint), which Copilot did not include.

**Why it mattered:** This decision locked in the storage architecture for the entire project. Using an abstract interface (NFR-02) meant the storage backend can be swapped without touching `NoteService` — a testability win confirmed during Sprint Zero.

---

## Interaction 2 — Fernet Key Management: Where does the key live?

**Week 4 | Decision: SPR-01 key storage strategy**

**My prompt to Copilot Chat:**
> For Fernet encryption of private notes, where should the key be stored? I can't hardcode it in source code and I can't put it in the notes directory. What are the options?

**Copilot suggestion:**
```
Key storage options, ranked by security:

1. OS Keychain (keyring library) — Most secure for desktop apps. Key never
   touches the filesystem as plaintext. Requires user authentication to access.
   Best choice for a local single-user app.

2. Environment variable — Simple, CI-friendly. Key is in memory only, not on
   disk. Fine for dev, but the user must manage it (risk of loss).

3. User-prompted key derivation (PBKDF2) — User enters a password on startup;
   key is derived. Never stored anywhere. Highest security, worst UX.

4. Hardcoded in source — Never acceptable. Makes encryption meaningless.

Recommendation: environment variable for Sprint Zero test keys, OS keychain
for production. Document the decision in your ADL before Sprint 1.

Example (env var approach):
import os
from cryptography.fernet import Fernet
key = os.environ.get("ASTRANOTES_KEY")
if not key:
    raise RuntimeError("ASTRANOTES_KEY environment variable is not set.")
f = Fernet(key.encode())
```

**Decision:** Accepted the framing, rejected the immediate implementation. Following Copilot's recommendation to document the decision in the ADL before committing to a mechanism. The key management strategy is recorded as a deferred Sprint 1 decision in `docs/architecture/AlexShirazi_ArchDecisionLog.pdf`. The Fernet encryption slice itself is explicitly listed as Gap 1 in the traceability matrix with the rationale documented.

**What I changed:** Copilot suggested choosing the OS keychain approach immediately. I pushed back because committing to a specific mechanism in Sprint Zero before the full usage pattern was clear would constrain Sprint 1 unnecessarily. Kept the decision open but bounded.

---

## Interaction 3 — Flask vs. a More Heavyweight Framework for the Web UI

**Week 10 | Decision: Web UI technology selection**

**My prompt to Copilot Chat:**
> I need to add a web UI to AstraNotes for the final demo. The existing code has a NoteService, ValidationLayer, and JsonFileRepository already implemented. Should I use Flask, FastAPI, or Django for a single-page demo UI?

**Copilot suggestion:**
```
Given that you have a working service layer and just need a presentation layer
for a demo, Flask is the right call:

- Zero-configuration, one dependency
- Jinja2 templates included — no separate frontend build step
- Direct instantiation of your existing NoteService (no serialization layer needed)
- SPR-04 compliance: minimal new dependency surface

FastAPI is better when you need a real API consumed by a separate frontend.
Django is better when you need ORM, auth, admin, and full CRUD scaffolding out
of the box. Neither fits a "wrap existing service layer for demo" use case.

Suggested route structure:
GET  /              → list notes (FR-08)
GET  /?q=keyword    → search (FR-07)
POST /notes         → create (FR-01)
POST /notes/<id>/edit   → edit (FR-02)
POST /notes/<id>/delete → delete (FR-03)
```

**Decision:** Accepted exactly. This matched the design already in `docs/architecture/AstraNotes_WebUI_Design.pdf`. The routes Copilot suggested were identical to the design doc, which confirmed both were reasonable.

---

## Interaction 4 — ValidationLayer: Separate Class or Inline in NoteService?

**Week 3 | Decision: Where does input validation live?**

**My prompt to Copilot Chat:**
> Should I put title validation logic directly in NoteService.create(), or in a separate ValidationLayer class? The requirement says each layer must be independently testable (NFR-02).

**Copilot suggestion:**
```
Separate ValidationLayer class. Reasons:

1. NFR-02 compliance: if validation is in NoteService, you can't test it without
   instantiating the service (which needs a repo). A standalone ValidationLayer
   is injectable and testable with zero dependencies.

2. Single Responsibility: NoteService coordinates; it shouldn't also contain
   all the business rules about what a valid note looks like.

3. Extensibility: a separate class makes it trivial to add tag validation,
   body length limits, or other rules later without changing NoteService.

class ValidationLayer:
    def validate_title(self, title: str) -> None:
        if not isinstance(title, str):
            raise ValidationError("title", "Title must be a string")
        if not title.strip():
            raise ValidationError("title", "Title must not be empty or whitespace-only")

    def validate_note(self, note: Note) -> None:
        self.validate_title(note.title)
```

**Decision:** Accepted verbatim. The `ValidationLayer` class in `src/astranotes/validation/validation_layer.py` is nearly identical to this suggestion. The `ValidationError` exception with `field_name` and `message` attributes came from this interaction.

**What I verified:** Copilot's whitespace-stripping check (`title.strip()`) directly addressed ambiguity A-01 from the Week 3.1 refined baseline — a whitespace-only title should be treated as empty. The AI suggestion and the manual ambiguity review arrived at the same conclusion independently.

---

## Interaction 5 — SearchResult Dataclass: Return List or Wrapped Object?

**Week 8 | Refactor: FR-07 search return type**

**My prompt to Copilot Chat:**
> My search() method currently returns List[Note]. Should I wrap it in a dataclass with the keyword and count? The requirement wants the result traceable to the original query.

**Copilot suggestion:**
```
Wrap it. A SearchResult dataclass gives you:
- The matched keyword stored alongside results (useful for "X results for Y" UI)
- A .count property without calling len() at every callsite
- A natural place to add pagination metadata later

@dataclass
class SearchResult:
    keyword: str
    notes: List[Note]

    @property
    def count(self) -> int:
        return len(self.notes)
```

**Decision:** Accepted verbatim. The `SearchResult` dataclass in `note_service.py` is exactly this. Implemented on branch `feature/search-improvements` (Week 8.1 refactor). This was logged as a v1.1 change in the module docstring.

---

## Interaction 6 — Null/Empty Check Safety: Explicit Guards vs. Truthy Checks

**Week 6 | Implementation detail: edge case handling**

**My prompt to Copilot Chat:**
> For the search keyword validation, is `if not keyword:` sufficient or should I also check for whitespace-only strings?

**Copilot suggestion:**
```
Both. The guard should be:
    if not keyword or not keyword.strip():
        raise ValueError("Search keyword must not be empty.")

Rationale: `not keyword` catches None and empty string. `not keyword.strip()`
catches "   " (whitespace-only). A user who submits three spaces expects an
error, not a result set of all notes.
```

**Decision:** Accepted exactly. This is the guard in `NoteService.search()`. The whitespace check was also separately noted in the edge-case review (Search section of Week 3.1 refined baseline), which confirmed the suggestion was correct.

---

*Log maintained by Alex Shirazi. Only interactions affecting architectural decisions or notable tradeoffs are included. Routine code completions are not logged.*
