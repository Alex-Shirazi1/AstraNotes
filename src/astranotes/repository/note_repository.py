"""
astranotes.repository.note_repository
Traces to: FR-05
UML evidence: NoteRepository interface (class diagram)
"""
from abc import ABC, abstractmethod
from typing import List
from astranotes.models.note import Note


class NoteRepository(ABC):
    """
    Abstract interface for note persistence. Traces to FR-05.
    Concrete implementations (e.g. JsonFileRepository) swap in without
    changing NoteService -- satisfying NFR-02 layer separation.
    """

    @abstractmethod
    def save(self, note: Note) -> None: ...

    @abstractmethod
    def get(self, note_id: str) -> Note: ...

    @abstractmethod
    def list_all(self) -> List[Note]: ...

    @abstractmethod
    def update(self, note: Note) -> None: ...

    @abstractmethod
    def delete(self, note_id: str) -> None: ...
