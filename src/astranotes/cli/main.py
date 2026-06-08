"""
astranotes.cli.main
Entry point for the AstraNotes CLI shell.
Traces to: FR-01, FR-08 (first two slices wired up)
"""
import os
import sys
from pathlib import Path

# Ensure src/ is on the path when running directly
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from astranotes.models.note import ValidationError, StoragePersistenceError, NoteNotFoundError
from astranotes.repository.json_file_repository import JsonFileRepository
from astranotes.service.note_service import NoteService
from astranotes.validation.validation_layer import ValidationLayer

DATA_DIR = Path.home() / ".astranotes" / "data"


def build_service() -> NoteService:
    repo = JsonFileRepository(DATA_DIR)
    validator = ValidationLayer()
    return NoteService(repo=repo, validator=validator)


def print_header():
    print("\n" + "=" * 44)
    print("         AstraNotes  |  Local Notes App")
    print("=" * 44)


def print_menu():
    print("\n  [1] View all notes")
    print("  [2] Create a note")
    print("  [3] Search notes")
    print("  [4] Delete a note")
    print("  [q] Quit")
    print()


def view_notes(service: NoteService):
    notes = service.list_sorted()
    if not notes:
        print("\n  No notes yet.")
        return
    print(f"\n  {len(notes)} note(s) -- sorted by last modified:\n")
    for i, note in enumerate(notes, 1):
        tag_str = f"  [{', '.join(note.tags)}]" if note.tags else ""
        private = "  [PRIVATE]" if note.is_private else ""
        print(f"  {i}. {note.title}{private}{tag_str}")
        print(f"     Modified: {note.modified_at.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"     ID: {note.id}")
        print()


def create_note(service: NoteService):
    print("\n  -- New Note --")
    title = input("  Title: ").strip()
    body  = input("  Body:  ").strip()
    tags_raw = input("  Tags (comma-separated, or leave blank): ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []
    try:
        note = service.create(title=title, body=body, tags=tags)
        print(f"\n  Note created: '{note.title}' (ID: {note.id})")
    except ValidationError as e:
        print(f"\n  Could not create note: {e.message}")
    except StoragePersistenceError as e:
        print(f"\n  Storage error: {e.message}")


def search_notes(service: NoteService):
    keyword = input("\n  Search keyword: ").strip()
    if not keyword:
        print("  Please enter a keyword.")
        return
    try:
        result = service.search(keyword)
    except ValueError as e:
        print(f"\n  {e}")
        return
    if result.count == 0:
        print(f"\n  No notes matched '{result.keyword}'.")
    else:
        print(f"\n  {result.count} result(s) for '{result.keyword}':\n")
        for note in result.notes:
            print(f"  - {note.title} (ID: {note.id})")


def delete_note(service: NoteService):
    note_id = input("\n  Enter note ID to delete: ").strip()
    confirm = input(f"  Delete note {note_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return
    try:
        service.delete(note_id)
        print("  Note deleted.")
    except NoteNotFoundError:
        print("  Note not found.")
    except StoragePersistenceError as e:
        print(f"  Storage error: {e.message}")


def main():
    service = build_service()
    print_header()
    while True:
        print_menu()
        choice = input("  Choose an option: ").strip().lower()
        if choice == "1":
            view_notes(service)
        elif choice == "2":
            create_note(service)
        elif choice == "3":
            search_notes(service)
        elif choice == "4":
            delete_note(service)
        elif choice == "q":
            print("\n  Goodbye.\n")
            break
        else:
            print("  Invalid option. Try again.")


if __name__ == "__main__":
    main()
