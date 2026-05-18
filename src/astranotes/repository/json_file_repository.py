"""
astranotes.repository.json_file_repository
Traces to: FR-05, SPR-02
UML evidence: JsonFileRepository class (class diagram), repo:JsonFileRepository (object diagram)
"""
import json
import os
from pathlib import Path
from typing import List

from astranotes.models.note import Note, NoteNotFoundError, StoragePersistenceError
from astranotes.repository.note_repository import NoteRepository


class JsonFileRepository(NoteRepository):
    """
    Persists each note as an individual JSON file under data_dir.
    File naming: {note_id}.json
    Traces to FR-05. Error handling traces to SPR-02.
    """

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        # Create the data directory if it does not exist (Sprint Zero objective 2)
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            raise StoragePersistenceError(
                "Could not create the notes data directory. Check your permissions."
            )

    def _path(self, note_id: str) -> Path:
        return self.data_dir / f"{note_id}.json"

    def save(self, note: Note) -> None:
        """FR-05: persist note to disk as JSON."""
        try:
            with open(self._path(note.id), "w", encoding="utf-8") as f:
                json.dump(note.to_dict(), f, indent=2)
        except OSError:
            raise StoragePersistenceError(
                "Could not save the note. Check available disk space and permissions."
            )

    def get(self, note_id: str) -> Note:
        """FR-05: load a single note by ID."""
        path = self._path(note_id)
        if not path.exists():
            raise NoteNotFoundError(note_id)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return Note.from_dict(json.load(f))
        except (json.JSONDecodeError, KeyError, ValueError):
            raise StoragePersistenceError(
                "A note file could not be read. The file may be corrupt."
            )

    def list_all(self) -> List[Note]:
        """
        FR-05: load all notes from data_dir.
        Corrupt or missing files are skipped with an error printed (Week 3.1 edge case).
        """
        notes = []
        for path in self.data_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    notes.append(Note.from_dict(json.load(f)))
            except (json.JSONDecodeError, KeyError, ValueError, OSError):
                # Skip corrupt file, continue loading remaining notes (FR-05 refined)
                print(f"Warning: skipped unreadable note file ({path.name})")
        return notes

    def update(self, note: Note) -> None:
        """FR-02: overwrite existing note file after edit."""
        if not self._path(note.id).exists():
            raise NoteNotFoundError(note.id)
        self.save(note)

    def delete(self, note_id: str) -> None:
        """FR-03: remove note file. Raises NoteNotFoundError if ID does not exist."""
        path = self._path(note_id)
        if not path.exists():
            raise NoteNotFoundError(note_id)
        try:
            os.remove(path)
        except OSError:
            raise StoragePersistenceError(
                "Could not delete the note. Check your permissions."
            )
