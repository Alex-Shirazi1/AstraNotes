"""
seed_notes.py — populate demo notes for admin and student1.
Run once from the AstraNotes root:
    python3 scripts/seed_notes.py
"""
import json, uuid, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from astranotes.repository.user_repository import UserRepository

BASE_DIR  = Path.home() / ".astranotes"
USERS_DIR = BASE_DIR / "users"
DATA_ROOT = BASE_DIR / "data"

user_repo = UserRepository(USERS_DIR)

def make_note(title, body, tags=None, is_private=False, days_ago=0):
    now = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "body": body,
        "tags": tags or [],
        "is_private": is_private,
        "created_at": now.isoformat(),
        "modified_at": now.isoformat(),
    }

def seed_user(username, notes):
    user = user_repo.get_by_username(username)
    if not user:
        print(f"  ✗ user '{username}' not found — register them first then re-run")
        return
    data_dir = DATA_ROOT / user.id
    data_dir.mkdir(parents=True, exist_ok=True)
    for note in notes:
        path = data_dir / f"{note['id']}.json"
        path.write_text(json.dumps(note, indent=2))
        marker = "🔒 " if note["is_private"] else "   "
        print(f"  {marker}{note['title']}")
    print(f"  → {len(notes)} notes written for '{username}'\n")

# ── Admin: CSEN 296B Lecture Notes ───────────────────────────────────
admin_notes = [
    make_note(
        "CSEN 296B — Lecture 1: Course Overview",
        "Introduced the AI-native SDLC methodology. Key themes: human oversight, "
        "artifact traceability, and vibe coding with validation gates. Professor "
        "emphasized that AI generates, humans decide.",
        tags=["csen296b", "lecture", "sdlc"],
        days_ago=60,
    ),
    make_note(
        "CSEN 296B — Lecture 2: Requirements Engineering",
        "Covered FR vs NFR vs SPR classification. Used AstraNotes as running example. "
        "Key insight: requirements must be traceable all the way to test cases. "
        "MoSCoW prioritization discussed.",
        tags=["csen296b", "lecture", "requirements"],
        days_ago=53,
    ),
    make_note(
        "CSEN 296B — Lecture 3: Architecture & UML",
        "Layered architecture: models → repository → service → presentation. "
        "UML class diagrams, sequence diagrams for key flows. NFR-02 strict layer "
        "separation — NoteService must not depend on concrete repository.",
        tags=["csen296b", "lecture", "architecture"],
        days_ago=46,
    ),
    make_note(
        "CSEN 296B — Lecture 4: Testing & TDD",
        "Test pyramid: unit → integration → e2e. TDD red-green-refactor cycle. "
        "pytest fixtures and tmp_path for isolation. Coverage thresholds as quality gates. "
        "Week 9 lab: test improvement log.",
        tags=["csen296b", "lecture", "testing"],
        days_ago=39,
    ),
    make_note(
        "CSEN 296B — Lecture 5: Security & CI/CD",
        "SAST with Bandit, secrets scanning in CI pipeline. GitHub Actions matrix "
        "testing across Python 3.9 and 3.11. SPR-01: Fernet encryption for private notes. "
        "Never commit credentials — use environment variables.",
        tags=["csen296b", "lecture", "security", "ci-cd"],
        is_private=True,  # 🔒 private
        days_ago=32,
    ),
]

# ── Student1: CSEN 240 Lecture Notes ─────────────────────────────────
student_notes = [
    make_note(
        "CSEN 240 — Lecture 1: Intro to Computer Architecture",
        "Von Neumann architecture: CPU, memory, I/O. Fetch-decode-execute cycle. "
        "RISC vs CISC tradeoffs. Performance equation: CPU time = IC × CPI × clock period.",
        tags=["csen240", "lecture", "architecture"],
        days_ago=58,
    ),
    make_note(
        "CSEN 240 — Lecture 2: Data Representation",
        "Two's complement for signed integers. IEEE 754 floating point: sign, exponent, "
        "mantissa. Overflow and underflow cases. Bitwise operations and masks.",
        tags=["csen240", "lecture", "binary"],
        days_ago=51,
    ),
    make_note(
        "CSEN 240 — Lecture 3: Assembly Language",
        "MIPS instruction set: R-type, I-type, J-type. Registers $t0-$t9, $s0-$s7, $sp, $ra. "
        "lw/sw for memory access. Branch and jump instructions. Calling conventions.",
        tags=["csen240", "lecture", "assembly", "mips"],
        days_ago=44,
    ),
    make_note(
        "CSEN 240 — Lecture 4: Pipelining",
        "5-stage pipeline: IF, ID, EX, MEM, WB. Hazards: structural, data, control. "
        "Forwarding paths to resolve data hazards. Branch prediction strategies.",
        tags=["csen240", "lecture", "pipelining"],
        days_ago=37,
    ),
    make_note(
        "CSEN 240 — Lecture 5: Memory Hierarchy",
        "Cache levels L1/L2/L3. Direct-mapped vs set-associative vs fully-associative. "
        "LRU replacement policy. Virtual memory and page tables. TLB for fast translation.",
        tags=["csen240", "lecture", "memory"],
        is_private=True,  # 🔒 private
        days_ago=30,
    ),
]

print("\n🌱 Seeding demo notes...\n")
print("Admin (CSEN 296B notes):")
seed_user("admin", admin_notes)
print("student1 (CSEN 240 notes):")
seed_user("student1", student_notes)
print("Done. Refresh the browser to see the notes.")
