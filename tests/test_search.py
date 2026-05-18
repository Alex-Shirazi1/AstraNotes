"""
tests/test_search.py
Tests for the refactored search() method (FR-07, US-06).
Added on branch feature/search-improvements (Week 8.1).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from astranotes.repository.json_file_repository import JsonFileRepository
from astranotes.service.note_service import NoteService, SearchResult
from astranotes.validation.validation_layer import ValidationLayer


@pytest.fixture
def service(tmp_path):
    return NoteService(JsonFileRepository(tmp_path), ValidationLayer())


@pytest.fixture
def populated_service(service):
    service.create(title="Sprint Zero Notes", body="Set up repo and stubs")
    service.create(title="API Key",           body="Store in environment variable")
    service.create(title="Meeting Notes",     body="Sprint review on Friday")
    return service


# FR-07: basic search
def test_search_returns_search_result_type(populated_service):
    result = populated_service.search("sprint")
    assert isinstance(result, SearchResult)

def test_search_matches_title_case_insensitive(populated_service):
    result = populated_service.search("SPRINT")
    assert result.count >= 1

def test_search_matches_body_case_insensitive(populated_service):
    result = populated_service.search("ENVIRONMENT")
    assert result.count == 1

def test_search_no_match_returns_empty_result(populated_service):
    result = populated_service.search("nonexistent")
    assert result.count == 0
    assert result.notes == []

def test_search_result_contains_keyword(populated_service):
    result = populated_service.search("  sprint  ")
    assert result.keyword == "sprint"  # stripped

# v1.1 edge cases
def test_search_empty_keyword_raises_value_error(populated_service):
    with pytest.raises(ValueError):
        populated_service.search("")

def test_search_whitespace_keyword_raises_value_error(populated_service):
    with pytest.raises(ValueError):
        populated_service.search("   ")

def test_search_keyword_stripped_before_match(populated_service):
    # "  sprint  " should match same as "sprint"
    result_padded = populated_service.search("  sprint  ")
    result_clean  = populated_service.search("sprint")
    assert result_padded.count == result_clean.count
