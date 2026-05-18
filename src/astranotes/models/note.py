"""
astranotes.models.note
Traces to: FR-01, FR-02, FR-03, FR-05, FR-06, FR-08
UML evidence: Note class (class diagram), note1:Note (object diagram)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
import uuid


class ValidationError(Exception):
    """Raised when note input fails validation. Traces to: FR-01, SPR-02."""
    def __init__(self, field_name: str, message: str) -> None:
        self.field_name = field_name
        self.message = message
        super().__init__(f"{field_name}: {message}")


class NoteNotFoundError(Exception):
    """Raised when a note ID does not exist in the repository. Traces to: FR-03."""
    def __init__(self, note_id: str) -> None:
        self.note_id = note_id
        super().__init__(f"Note not found: {note_id}")


class StoragePersistenceError(Exception):
    """Raised when a storage read or write operation fails. Traces to: SPR-02."""
    def __init__(self, message: str) -> None:
        # message must never include raw file paths or stack traces (SPR-02)
        self.message = message
        super().__init__(message)


@dataclass
class Note:
    """
    Core note entity. Traces to FR-01, FR-02, FR-05, FR-06, FR-08.
    All timestamps stored in UTC (FR-06 refined requirement).
    """
    title: str
    body: str
    is_private: bool = False
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_title(self) -> str:
        return self.title

    def get_body(self) -> str:
        return self.body

    def set_body(self, new_body: str) -> None:
        self.body = new_body
        self.modified_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "is_private": self.is_private,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            id=data["id"],
            title=data["title"],
            body=data["body"],
            is_private=data.get("is_private", False),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
        )
