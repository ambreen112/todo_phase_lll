# Feature Specification: Soft Delete with Reason Tracking

**Feature Branch**: `001-soft-delete-reason`
**Created**: 2025-12-29
**Status**: Draft
**Input**: User description: "Specify a feature to add a delete reason to the delete command using soft delete in the existing Todo CLI app."

## User Scenarios & Testing

### User Story 1 - Soft Delete with Reason (Priority: P1)

User wants to delete a todo item and provide a reason for why it was deleted. The system should mark the item as deleted rather than removing it permanently, storing both the deletion status and the reason provided by the user.

**Why this priority**: This is the core functionality requested. Soft delete provides auditability and recovery capabilities, while the reason field captures important context about why tasks were removed.

**Independent Test**: Can be fully tested by creating a todo, deleting it with a reason, then listing deleted items and verifying both the deletion status and reason are stored correctly.

**Acceptance Scenarios**:

1. **Given** an active todo item exists, **When** user executes `delete <id> <reason>`, **Then** the todo is marked as deleted and the reason is stored
2. **Given** a deleted todo exists with reason, **When** user lists all todos, **Then** deleted items are not shown in the default list
3. **Given** a deleted todo exists with reason, **When** user queries deleted items, **Then** the todo ID, task, status, and deletion reason are displayed

---

### User Story 2 - View Deleted Items (Priority: P2)

User wants to see a list of deleted todo items along with their deletion reasons for auditing and potential recovery purposes.

**Why this priority**: Secondary to the core delete functionality but essential for the soft delete feature to provide value. Users need visibility into what was deleted and why.

**Independent Test**: Can be fully tested by deleting multiple todos with different reasons, then executing the list-deleted command and verifying all deleted items appear with their reasons.

**Acceptance Scenarios**:

1. **Given** multiple deleted todos exist, **When** user executes the list-deleted command, **Then** all deleted items are displayed in a table format
2. **Given** deleted todos with long reasons exist, **When** user views the deleted list, **Then** long reasons are truncated for display while full text is preserved

---

### User Story 3 - Restore Deleted Items (Priority: P3)

User wants to restore a previously deleted todo back to active status, clearing its deletion status while preserving the original task content.

**Why this priority**: Restore capability is a natural extension of soft delete but not strictly required for the core soft delete with reason feature. Provides recovery mechanism for users who deleted items accidentally.

**Independent Test**: Can be fully tested by deleting a todo, then restoring it and verifying it reappears in the active todo list.

**Acceptance Scenarios**:

1. **Given** a deleted todo exists, **When** user executes `restore <id>`, **Then** the todo becomes active again and appears in the main list
2. **Given** a deleted todo with reason exists, **When** user restores it, **Then** the deletion reason is cleared or archived (not shown in active list)

---

### Edge Cases

- What happens when user tries to delete without providing a reason?
- What happens when user tries to restore an already active todo?
- What happens when deletion reason is extremely long (e.g., 500+ characters)?
- What happens when user tries to delete a non-existent todo ID?
- What happens when user provides an empty reason string (just whitespace)?
- How does system handle special characters or emojis in deletion reason?

## Requirements

### Functional Requirements

- **FR-001**: System MUST support soft delete operation that marks todos as deleted instead of removing them permanently
- **FR-002**: System MUST require a deletion reason when executing the delete command
- **FR-003**: System MUST store deletion reason with each deleted todo item
- **FR-004**: System MUST exclude deleted todos from the default list command output
- **FR-005**: System MUST provide a command to view all deleted todos including their deletion reasons
- **FR-006**: System MUST allow users to restore deleted todos back to active status
- **FR-007**: System MUST validate that todo ID exists before attempting delete operation
- **FR-008**: System MUST provide clear error message when delete command is executed without a reason
- **FR-009**: System MUST preserve original task content when soft deleting (only add deletion metadata)
- **FR-010**: System MUST handle deletion reasons of reasonable length (up to 200 characters minimum)

### Key Entities

- **Todo**: Represents a task with ID, description, completion status, deletion status, and deletion reason (if deleted)
  - Active todos: visible in default list, no deletion metadata
  - Deleted todos: hidden from default list, marked with deletion timestamp and reason
- **Deletion Record**: Metadata attached to deleted todos including reason and timestamp

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can successfully soft delete a todo with reason in under 5 seconds
- **SC-002**: Deleted todos with reasons are retrievable via dedicated command showing ID, task, and reason
- **SC-003**: System maintains 100% of deleted todo data (no information loss on soft delete)
- **SC-004**: Users can restore deleted items successfully, returning them to active state
- **SC-005**: All deletion operations include required reason field (validation prevents empty reasons)
