"""
astranotes.service.note_service
Traces to: FR-01, FR-02, FR-03, FR-07, FR-08
UML evidence: NoteService class (class diagram), service:NoteService (object diagram)

Changelog:
  v1.0  Initial implementation (Week 6 Sprint Zero)
  v1.1  search() refactored on branch feature/search-improvements (Week 8.1)
        - empty keyword now raises ValueError instead of returning all notes
        - keyword stripped before matching to avoid whitespace false-negatives
        - search result wrapped in SearchResult dataclass for traceability
"""
from dataclasses import dataclass
from datetime import timezone, datetime
from typing import List

from astranotes.models.note import Note, ValidationError
from astranotes.repository.note_repository import NoteRepository
from astranotes.validation.validation_layer import ValidationLayer


@dataclass
class SearchResult:
    """
    Wraps search output with metadata.
    Added in v1.1 refactor (branch: feature/search-improvements).
    Traces to FR-07: keyword, match count, and matched notes all in one object.
    """
    keyword: str
    notes: List[Note]

    @property
    def count(self) -> int:
        return len(self.notes)


class NoteService:
    """
    Coordinates all note operations. Depends on NoteRepository interface (NFR-02).
    Composes ValidationLayer (class diagram composition relationship).
    """

    def __init__(self, repo: NoteRepository, validator: ValidationLayer) -> None:
        self._repo = repo
        self._validator = validator

    # Slice 1: Create Note (FR-01)
    def create(self, title: str, body: str, tags: List[str] = None) -> Note:
        """
        FR-01: create a new plain note.
        Validates title, assigns UUID and timestamps automatically.
        Raises ValidationError if title is empty or whitespace-only.
        """
        note = Note(title=title, body=body, tags=tags or [])
        self._validator.validate_note(note)
        self._repo.save(note)
        return note

    # Slice 2: List Sorted (FR-08)
    def list_sorted(self) -> List[Note]:
        """
        FR-08: return all notes sorted by modified_at descending.
        Stable tiebreaker: created_at descending (Week 3.1 ambiguity A-04 resolution).
        """
        notes = self._repo.list_all()
        return sorted(
            notes,
            key=lambda n: (n.modified_at, n.created_at),
            reverse=True
        )

    def edit(self, note_id: str, title: str, body: str) -> None:
        """FR-02: edit title and body; modified_at updated automatically by Note.set_body."""
        note = self._repo.get(note_id)
        self._validator.validate_title(title)
        note.title = title
        note.set_body(body)
        self._repo.update(note)

    def delete(self, note_id: str) -> None:
        """FR-03: delete note by ID."""
        self._repo.delete(note_id)

    # v1.1 refactor: search() (FR-07) -- branch feature/search-improvements
    def search(self, keyword: str) -> SearchResult:
        """
        FR-07: case-insensitive keyword search across title and body.

        v1.1 changes (PR #1, feature/search-improvements):
          - empty or whitespace-only keyword raises ValueError (was: silently returned all notes)
          - keyword stripped before comparison to avoid whitespace false-negatives
          - returns SearchResult instead of bare List[Note] for traceability
          - private notes excluded from this slice (gap documented in Week 5.2 traceability matrix)

        Raises:
            ValueError: if keyword is empty or whitespace-only.
        """
        if not keyword or not keyword.strip():
            raise ValueError("Search keyword must not be empty.")

        kw = keyword.strip().lower()
        matched = [
            n for n in self._repo.list_all()
            if kw in n.title.lower()
            or kw in n.body.lower()
            or any(kw in tag.lower() for tag in n.tags)
            or n.id.lower().startswith(kw)
        ]
        return SearchResult(keyword=keyword.strip(), notes=matched)
