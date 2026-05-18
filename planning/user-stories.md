# AstraNotes — User Stories and Acceptance Criteria

**Traceability:** Stories derived from FR-01 through FR-08 and SPR-01 through SPR-04 (Submission 2 Requirement Set)

---

## US-01 — Create a Note
**Requirement:** FR-01
**Story:** As a user, I want to create a new note with a title and body so that I can capture information quickly and find it later.

**Acceptance Criteria:**
- [ ] Given I am on the note list screen, when I trigger "New Note," a note entry form is presented with a title field and a body field.
- [ ] When I submit a title and body, a new Note object is created with a UUID, created_at timestamp, and modified_at timestamp set automatically.
- [ ] The new note appears in the note list immediately after creation, sorted by modified_at descending.
- [ ] If I submit with an empty title, validation rejects the entry and displays a non-technical error message.

---

## US-02 — Edit an Existing Note
**Requirement:** FR-02
**Story:** As a user, I want to edit the title or body of an existing note so that I can keep my notes accurate and up to date.

**Acceptance Criteria:**
- [ ] Given a saved note, when I open it and modify the title or body and save, the note is updated in local storage and the modified_at timestamp reflects the save time.
- [ ] The original created_at timestamp is not changed by an edit.
- [ ] If the save operation fails (e.g., disk error), a clear error message is shown and the note is not corrupted.
- [ ] The updated note appears at the top of the note list (sorted by modified_at).

---

## US-03 — Delete a Note
**Requirement:** FR-03
**Story:** As a user, I want to delete a note I no longer need so that my note collection stays organized and uncluttered.

**Acceptance Criteria:**
- [ ] Given a saved note, when I trigger delete and confirm, the note is removed from local storage and no longer appears in the note list.
- [ ] If I cancel the delete confirmation, the note is not removed.
- [ ] Deleting a note that does not exist (e.g., already removed) surfaces a clear error rather than crashing.

---

## US-04 — Mark a Note as Private
**Requirement:** FR-04, SPR-01
**Story:** As a user, I want to mark a note as private so that its content is encrypted on disk and not readable without authorization.

**Acceptance Criteria:**
- [ ] Given a note, when I toggle is_private to True and save, the body is encrypted by PrivacyService before being written to disk.
- [ ] When I retrieve a private note, the body is decrypted by PrivacyService before being displayed.
- [ ] The raw note file on disk does not contain plaintext body content for any private note.
- [ ] If encryption or decryption fails, a clear error message is shown and no partial or corrupted content is displayed.

---

## US-05 — Persist Notes Across Sessions
**Requirement:** FR-05
**Story:** As a user, I want my notes to be saved to local storage so that they are still available the next time I open the application.

**Acceptance Criteria:**
- [ ] When the application starts, all previously saved notes are loaded from local file storage and displayed in the note list.
- [ ] Notes created or edited in the current session are available in the next session without any additional user action.
- [ ] If a note file is missing or corrupt on startup, the application logs the issue and continues loading the remaining notes rather than crashing.
- [ ] Startup completes and the note list is displayed within 3 seconds on a standard development machine (NFR-03).

---

## US-06 — Search Notes by Keyword
**Requirement:** FR-07
**Story:** As a user, I want to search my notes by keyword so that I can quickly find notes relevant to a topic without scrolling through the full list.

**Acceptance Criteria:**
- [ ] Given a collection of notes, when I enter a search keyword, all notes whose title or body contains the keyword (case-insensitive) are returned.
- [ ] If no notes match, a clear empty-state message is shown rather than a blank screen.
- [ ] Search across up to 500 notes completes within 2 seconds (NFR-01).
- [ ] Clearing the search field restores the full sorted note list.

---

## US-07 — View Notes Sorted by Last Modified
**Requirement:** FR-08
**Story:** As a user, I want to see my notes listed with the most recently modified note at the top so that my most active notes are always easy to reach.

**Acceptance Criteria:**
- [ ] The note list is sorted by modified_at descending by default on every application load.
- [ ] After creating or editing a note, that note appears at the top of the list without requiring a manual refresh.
- [ ] Sort order is stable: notes with identical modified_at values are ordered consistently (e.g., by created_at descending as a tiebreaker).

---

## US-08 — Tag a Note
**Requirement:** FR-06
**Story:** As a user, I want to add tags to a note so that I can group related notes by topic and locate them more easily later.

**Acceptance Criteria:**
- [ ] Given a note, when I add one or more tags and save, the tags are persisted as part of the note metadata.
- [ ] Tags are stored as a list of strings and are preserved exactly as entered (case-sensitive).
- [ ] A note with no tags displays an empty tag list without error.
- [ ] Tags are visible when viewing a note and can be edited or removed in the same edit flow as the title and body.
