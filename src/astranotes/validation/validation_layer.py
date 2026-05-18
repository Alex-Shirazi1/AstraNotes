"""
astranotes.validation.validation_layer
Traces to: FR-01, SPR-02
UML evidence: ValidationLayer class (class diagram)
"""
from typing import List
from astranotes.models.note import Note, ValidationError


class ValidationLayer:
    """
    Stateless validator for Note inputs.
    All rules enforce constraints from the Week 3.1 refined requirement baseline.
    """

    def validate_title(self, title: str) -> None:
        """
        FR-01: title must be a non-empty string after stripping whitespace.
        Whitespace-only title ('   ') is treated as empty per edge-case review (Week 3.1, A-01).
        """
        if not isinstance(title, str):
            raise ValidationError("title", "Title must be a string")
        if not title.strip():
            raise ValidationError("title", "Title must not be empty or whitespace-only")

    def validate_note(self, note: Note) -> None:
        """Run all validation rules against a Note instance."""
        self.validate_title(note.title)
