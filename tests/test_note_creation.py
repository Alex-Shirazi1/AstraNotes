"""
tests/test_note_creation.py
Unit tests for Slice 1: Note creation (FR-01) and Slice 2: Sorted listing (FR-08).
Tests run without real file system -- uses a temporary directory (SPR-03).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import tempfile
import pytest
from astranotes.models.note import Note, ValidationError
from astranotes.repository.json_file_repository import JsonFileRepository
from astranotes.service.note_service import NoteService
from astranotes.validation.validation_layer import ValidationLayer


@pytest.fixture
def service(tmp_path):
    repo = JsonFileRepository(tmp_path)
    validator = ValidationLayer()
    return NoteService(repo=repo, validator=validator)


# ── Slice 1: Create Note (FR-01) ─────────────────────────────────────────────

def test_create_note_returns_note_with_correct_title(service):
    note = service.create(title="Sprint Zero", body="Set up repo")
    assert note.title == "Sprint Zero"

def test_create_note_assigns_uuid(service):
    note = service.create(title="Test", body="Body")
    assert note.id is not None
    assert len(note.id) == 36  # UUID format

def test_create_note_assigns_timestamps(service):
    note = service.create(title="Test", body="Body")
    assert note.created_at is not None
    assert note.modified_at is not None

def test_create_note_empty_title_raises_validation_error(service):
    with pytest.raises(ValidationError):
        service.create(title="", body="Some body")

def test_create_note_whitespace_title_raises_validation_error(service):
    with pytest.raises(ValidationError):
        service.create(title="   ", body="Some body")

def test_create_note_persists_to_disk(service, tmp_path):
    note = service.create(title="Persisted", body="Check disk")
    assert (tmp_path / f"{note.id}.json").exists()


# ── Slice 2: List Sorted (FR-08) ─────────────────────────────────────────────

def test_list_sorted_returns_most_recently_modified_first(service):
    n1 = service.create(title="First", body="")
    n2 = service.create(title="Second", body="")
    # edit n1 so its modified_at is newer
    service.edit(n1.id, title="First updated", body="Updated")
    sorted_notes = service.list_sorted()
    assert sorted_notes[0].id == n1.id

def test_list_sorted_empty_returns_empty_list(service):
    assert service.list_sorted() == []

def test_list_sorted_single_note(service):
    note = service.create(title="Only note", body="")
    result = service.list_sorted()
    assert len(result) == 1
    assert result[0].id == note.id
