# BDD Acceptance Scenarios — AstraNotes

**Format:** Gherkin (Given / When / Then)
**Traces to:** FR-01 through FR-08, SPR-01 through SPR-03
**Derived from:** `user-stories.md` acceptance criteria, refined at Week 3.1

---

## Feature: Create a Note (US-01, FR-01, FR-06)

```gherkin
Feature: Create a Note
  As a user
  I want to create a new note with a title, body, and optional tags
  So that I can capture information quickly and find it later

  Scenario: Successfully create a note with title and body
    Given I am on the AstraNotes main page
    When I click the "New Note" button
    And I enter "Sprint Review Notes" as the title
    And I enter "Discussed team velocity and backlog grooming" as the body
    And I click "Create Note"
    Then a new note card appears at the top of the note list
    And the card displays the title "Sprint Review Notes"
    And the card shows a created_at timestamp in UTC

  Scenario: Create a note with optional tags
    Given I am on the AstraNotes main page
    When I click the "New Note" button
    And I enter "Architecture Decision" as the title
    And I enter "research, architecture" in the tags field
    And I click "Create Note"
    Then the new note card shows tags "#research" and "#architecture"

  Scenario: Reject note submission with an empty title
    Given I am on the AstraNotes main page
    When I click the "New Note" button
    And I leave the title field empty
    And I click "Create Note"
    Then an inline validation error is displayed reading "Title is required"
    And no note is added to the note list
    And the modal remains open

  Scenario: Reject note submission with a whitespace-only title
    Given I am on the AstraNotes main page
    When I click the "New Note" button
    And I enter "   " as the title
    And I click "Create Note"
    Then the system rejects the note with a validation error
    And no note is created
```

---

## Feature: Edit a Note (US-02, FR-02)

```gherkin
Feature: Edit an Existing Note
  As a user
  I want to edit the title or body of an existing note
  So that I can keep my notes accurate and up to date

  Scenario: Successfully edit a note's title and body
    Given a note exists with title "Old Title" and body "Old body"
    And I have selected that note card
    When I click the "Edit" button on the note card
    And I change the title to "New Title"
    And I change the body to "Updated body content"
    And I click "Save"
    Then the note displays "New Title" as its title
    And the note's modified_at timestamp is updated to the current time
    And the note moves to the top of the sorted list

  Scenario: created_at is not changed by an edit
    Given a note exists with a known created_at timestamp
    And I have selected that note card
    When I edit and save the note
    Then the note's created_at timestamp is unchanged
```

---

## Feature: Delete a Note (US-03, FR-03)

```gherkin
Feature: Delete a Note
  As a user
  I want to delete a note I no longer need
  So that my note collection stays organized

  Scenario: Successfully delete a note with confirmation
    Given a note exists in the list
    And I have selected that note card
    When I click the "Delete" button
    And I click "Yes, delete" in the confirmation strip
    Then the note is removed from the note list
    And a success message "Note deleted" appears briefly

  Scenario: Cancel a delete operation
    Given a note exists in the list
    And I have selected that note card
    When I click the "Delete" button
    And I click "Cancel" in the confirmation strip
    Then the note remains in the note list unchanged

  Scenario: Delete a note that no longer exists
    Given a note ID that has been removed from storage
    When a delete request is submitted for that ID
    Then the system shows a clear error message "Note not found"
    And the application does not crash
```

---

## Feature: Mark a Note as Private (US-04, FR-04, SPR-01)

```gherkin
Feature: Mark a Note as Private
  As a user
  I want to mark a note as private
  So that its content is flagged for protected handling

  Scenario: Create a private note
    Given I am on the AstraNotes main page
    When I click "New Note"
    And I enter "Private Thoughts" as the title
    And I check the "Mark as private" checkbox
    And I click "Create Note"
    Then the note card shows a lock icon
    And the note's is_private flag is true in storage

  Scenario: Private note is visually distinguished from public notes
    Given a private note and a public note exist in the list
    Then the private note card displays a lock icon
    And the public note card does not display a lock icon
```

---

## Feature: Persist Notes Across Sessions (US-05, FR-05)

```gherkin
Feature: Persist Notes Across Sessions
  As a user
  I want my notes saved to local storage
  So that they are still available the next time I open the application

  Scenario: Notes survive an application restart
    Given I have created three notes in the current session
    When I close and reopen the application
    Then all three notes are displayed in the note list

  Scenario: Corrupt note file is skipped gracefully on startup
    Given a corrupt JSON file exists in the notes data directory
    When the application starts
    Then the application loads and displays all valid notes
    And no error crashes the application
    And the corrupt file is skipped with a logged warning
```

---

## Feature: Search Notes by Keyword (US-06, FR-07)

```gherkin
Feature: Search Notes by Keyword
  As a user
  I want to search my notes by keyword
  So that I can quickly find relevant notes without scrolling the full list

  Scenario: Search returns matching notes (case-insensitive)
    Given three notes exist: "Sprint Notes", "API Design", "Meeting Summary"
    When I enter "sprint" in the search bar
    Then only "Sprint Notes" is shown in the results
    And the result count reads "1 result"

  Scenario: Search with no matches shows empty state
    Given notes exist in the collection
    When I enter "xyznonexistent" in the search bar
    Then no note cards are shown
    And the empty state message reads 'No results for "xyznonexistent"'

  Scenario: Clearing the search restores the full sorted list
    Given a search is active showing filtered results
    When I click the clear (✕) button next to the search term
    Then all notes are shown, sorted by modified_at descending

  Scenario: Empty search keyword is rejected
    Given I am on the main page
    When I submit a search with only whitespace
    Then an error message is displayed
    And the full note list is shown
```

---

## Feature: View Notes Sorted by Last Modified (US-07, FR-08)

```gherkin
Feature: View Notes Sorted by Last Modified
  As a user
  I want to see my notes with the most recently modified at the top
  So that my most active notes are always easy to reach

  Scenario: Notes are sorted newest-modified first on load
    Given notes with different modified_at timestamps exist
    When I open the application
    Then the note with the most recent modified_at is displayed first

  Scenario: Editing a note moves it to the top of the list
    Given two notes exist with Note A older than Note B
    When I edit Note A and save
    Then Note A appears at the top of the list
    And Note B appears below it
```

---

## Feature: Tag a Note (US-08, FR-06)

```gherkin
Feature: Tag a Note
  As a user
  I want to add tags to a note
  So that I can group related notes by topic

  Scenario: Tags are saved and displayed on the note card
    Given I create a note with tags "research, backend"
    Then the note card shows "#research" and "#backend"

  Scenario: Tags are case-sensitive
    Given a note is created with tag "Backend"
    Then the stored tag is exactly "Backend" (not "backend")

  Scenario: A note with no tags displays without error
    Given a note is created with no tags
    Then the note card displays no tag chips
    And the note loads without error
```
