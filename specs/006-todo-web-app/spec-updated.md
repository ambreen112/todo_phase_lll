# Feature Specification: Phase 2 Todo Web Application (Complete Feature Parity)

**Feature Branch**: `006-todo-web-app`
**Created**: 2026-01-02
**Updated**: 2026-01-08 (Full Phase 1 feature parity)
**Status**: Draft
**Input**: Migrate all Phase 1 CLI features to Phase 2 web application

## Overview

This specification defines Phase 2 of the Evolution of Todo application, transitioning from a console-based CLI tool to a full-stack web application with multi-user support and authentication. Phase 2 maintains **complete feature parity** with Phase 1 while adding multi-user capabilities, persistent storage, and a modern web interface.

### Project Context

Phase 1 delivered a console-based todo application with comprehensive task management features:
- Priority levels (HIGH/MEDIUM/LOW) with visual indicators
- Tags/categories for flexible organization
- Due dates with overdue and due-today alerts
- Recurring tasks (daily/weekly/monthly)
- Soft-delete with deletion reasons and restore capability
- Advanced filtering, search, and sorting
- Task completion tracking

Phase 2 extends this feature set into a web-accessible, multi-user system where each user manages their own private task list with the same rich functionality.

### Assumptions

- Users access the application via a modern web browser (Chrome, Firefox, Safari, Edge - current and previous two versions)
- Single-tenant deployment with shared infrastructure but logical data isolation per user
- JWT tokens expire after 7 days for reasonable security without excessive re-authentication
- All Phase 1 features are preserved with equivalent web UI implementations
- Task IDs transition from auto-increment integers to UUIDs for multi-user scalability
- ISO 8601 datetime format used for all date/time fields

---

## User Scenarios & Testing

### User Story 1 - Account Creation and Authentication (Priority: P1) 🎯

As a new user, I want to create an account so that I can access my tasks from any device.

**Why this priority**: Authentication is the foundation of the multi-user system. Without it, no other features can function.

**Independent Test**: A user can complete signup, log in with new credentials, and see an empty task dashboard.

**Acceptance Scenarios**:

1. **Given** a user visits the signup page, **When** they provide valid email and password (minimum 8 characters), **Then** the system creates their account and redirects to login.

2. **Given** a user attempts signup with an email already in use, **When** they submit the form, **Then** the system displays an error message and does not create a duplicate account.

3. **Given** a user with an account visits the login page, **When** they enter correct credentials, **Then** the system authenticates them and grants access to their task dashboard.

4. **Given** an authenticated user, **When** their session expires or they clear browser data and revisit the app, **Then** the system prompts them to log in again.

---

### User Story 2 - Task Creation with Full Metadata (Priority: P1) 🎯

As a user, I want to create tasks with title, description, priority, tags, due date, and recurrence so that I can fully capture my task requirements.

**Why this priority**: Task creation is the primary value proposition. All metadata fields from Phase 1 must be available.

**Independent Test**: User can create a task with all optional fields and see it appear in their list with all metadata intact.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the dashboard, **When** they click "Add Task" and provide only a title, **Then** the task is saved with default priority (MEDIUM), no tags, no due date, and no recurrence.

2. **Given** an authenticated user creating a task, **When** they provide title, description, priority HIGH, tags "work, urgent", due date "2026-01-15", **Then** all fields are stored and displayed correctly.

3. **Given** an authenticated user, **When** they attempt to create a task without a title, **Then** the system shows a validation error and does not save the task.

4. **Given** an authenticated user creating a task, **When** they set recurrence to "weekly" and due date to "2026-01-15", **Then** the task is marked as recurring and will auto-generate next instance upon completion.

---

### User Story 3 - Priority Management (Priority: P1) 🎯

As a user, I want to assign priority levels (HIGH, MEDIUM, LOW) to tasks so that I can focus on important items first.

**Why this priority**: Priority is a core organizational dimension from Phase 1. Essential for task triage and focus.

**Independent Test**: User can set priority on creation, update it later, filter by priority, and sort by priority.

**Acceptance Scenarios**:

1. **Given** an authenticated user creating a task, **When** they select priority HIGH, **Then** the task displays with HIGH priority indicator (red badge or icon).

2. **Given** an authenticated user viewing their task list, **When** they filter by priority HIGH, **Then** only HIGH priority tasks are shown.

3. **Given** an authenticated user with mixed-priority tasks, **When** they sort by priority, **Then** tasks are ordered HIGH → MEDIUM → LOW.

4. **Given** an authenticated user editing a task, **When** they change priority from MEDIUM to HIGH, **Then** the change persists and is immediately visible.

---

### User Story 4 - Tags and Categorization (Priority: P1) 🎯

As a user, I want to assign multiple tags to tasks so that I can organize them by context, project, or category.

**Why this priority**: Tags provide flexible, cross-cutting organization independent of status or priority. Core Phase 1 feature.

**Independent Test**: User can add multiple tags to a task, filter by tag, and search by tag.

**Acceptance Scenarios**:

1. **Given** an authenticated user creating a task, **When** they add tags "work, urgent, meeting", **Then** all three tags are stored and displayed with the task.

2. **Given** an authenticated user viewing their task list, **When** they filter by tag "work", **Then** all tasks with "work" tag are shown.

3. **Given** an authenticated user, **When** they search for "urgent", **Then** tasks with "urgent" in title, description, OR tags are returned.

4. **Given** an authenticated user editing a task, **When** they add a new tag "blocked", **Then** the tag is added to existing tags without replacing them.

---

### User Story 5 - Due Dates and Reminders (Priority: P1) 🎯

As a user, I want to set due dates on tasks and receive alerts for overdue or due-today tasks so that I don't miss deadlines.

**Why this priority**: Time-based task management is critical. Phase 1 had overdue/today detection and startup alerts.

**Independent Test**: User sets a due date, sees visual indicators for overdue/today, and receives alerts.

**Acceptance Scenarios**:

1. **Given** an authenticated user creating a task, **When** they set due date to "2026-01-15", **Then** the due date is stored and displayed with the task.

2. **Given** an authenticated user with a task due yesterday, **When** they view their dashboard, **Then** the task shows an "overdue" indicator (⚠ badge or red highlight).

3. **Given** an authenticated user with tasks due today, **When** they log in, **Then** a notification banner displays "X tasks due today".

4. **Given** an authenticated user viewing their list, **When** they filter by "overdue", **Then** only tasks with due dates in the past are shown.

5. **Given** an authenticated user viewing their list, **When** they filter by "due today", **Then** only tasks with due dates today are shown.

---

### User Story 6 - Recurring Tasks (Priority: P2)

As a user, I want to create recurring tasks (daily/weekly/monthly) so that repeated tasks are automatically managed.

**Why this priority**: Automating repeated tasks reduces manual overhead. Phase 1 had full recurrence support.

**Independent Test**: User creates a weekly recurring task, completes it, and a new instance is auto-generated with the next due date.

**Acceptance Scenarios**:

1. **Given** an authenticated user creating a task, **When** they set recurrence to "weekly" and due date to "2026-01-15", **Then** the task is marked as recurring with a 🔄 indicator.

2. **Given** an authenticated user with a recurring task, **When** they mark it complete, **Then** a new instance is created with the next due date (7 days later for weekly), linked via `parent_id`.

3. **Given** an authenticated user with a recurring task, **When** they stop recurrence, **Then** future instances are no longer generated upon completion.

4. **Given** an authenticated user, **When** they delete a recurring task instance, **Then** only that instance is deleted, not the entire series (unless they choose "delete all").

---

### User Story 7 - Soft Delete with Reasons (Priority: P2)

As a user, I want to delete tasks with a reason and be able to restore them later so that I have an audit trail and can undo mistakes.

**Why this priority**: Soft delete prevents accidental data loss and provides accountability. Phase 1 required deletion reasons.

**Independent Test**: User deletes a task with a reason, views deleted tasks list, and restores a task.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing a task, **When** they click delete and provide reason "no longer needed", **Then** the task is soft-deleted with reason and timestamp.

2. **Given** an authenticated user, **When** they attempt to delete without providing a reason, **Then** the system shows an error and does not delete the task.

3. **Given** an authenticated user, **When** they view "Deleted Tasks", **Then** all soft-deleted tasks are shown with their deletion reasons and timestamps.

4. **Given** an authenticated user viewing deleted tasks, **When** they click restore on a task, **Then** the task returns to active status with deletion metadata cleared.

5. **Given** an authenticated user viewing the main task list, **When** deleted tasks exist, **Then** they are not shown in the active list (filtered out by default).

---

### User Story 8 - Advanced Filtering and Search (Priority: P2)

As a user, I want to filter tasks by multiple criteria and search across all fields so that I can quickly find relevant tasks.

**Why this priority**: With rich metadata, powerful filtering and search are essential for usability. Phase 1 had comprehensive filtering.

**Independent Test**: User applies multiple filters simultaneously and searches across title, description, and tags.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they apply filter "priority: HIGH AND tag: work", **Then** only HIGH priority tasks with "work" tag are shown.

2. **Given** an authenticated user, **When** they search for "meeting", **Then** tasks with "meeting" in title, description, or tags are returned.

3. **Given** an authenticated user, **When** they filter by "status: incomplete AND due: overdue", **Then** only incomplete tasks with past due dates are shown.

4. **Given** an authenticated user with active filters, **When** they clear filters, **Then** the full task list is restored.

---

### User Story 9 - Sorting and List Management (Priority: P2)

As a user, I want to sort my task list by different fields so that I can view tasks in my preferred order.

**Why this priority**: Sorting provides control over list presentation. Phase 1 supported ID, priority, title, and status sorting.

**Independent Test**: User sorts list by priority, then by title, and sees correct ordering.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing their task list, **When** they sort by priority, **Then** tasks are ordered HIGH → MEDIUM → LOW.

2. **Given** an authenticated user viewing their task list, **When** they sort by title, **Then** tasks are ordered alphabetically (case-insensitive).

3. **Given** an authenticated user viewing their task list, **When** they sort by status, **Then** incomplete tasks appear before completed tasks.

4. **Given** an authenticated user viewing their task list, **When** they sort by due date, **Then** tasks with earlier due dates appear first, followed by tasks with no due date.

---

### User Story 10 - Task List Viewing (Priority: P1) 🎯

As a user, I want to view all my tasks with visual indicators for status, priority, and due date so that I can quickly assess my workload.

**Why this priority**: Task visibility is fundamental. Users must see their tasks with clear visual cues.

**Independent Test**: An authenticated user sees their complete task list with priority colors, status indicators, and due date alerts.

**Acceptance Scenarios**:

1. **Given** an authenticated user with tasks, **When** they access the dashboard, **Then** all their active tasks are displayed with priority badges, completion status, and due date indicators.

2. **Given** an authenticated user with no tasks, **When** they access the dashboard, **Then** they see a prompt to create their first task.

3. **Given** an authenticated user viewing their task list, **When** tasks exist, **Then** they can distinguish between incomplete, completed, recurring, overdue, and due-today tasks visually.

4. **Given** an authenticated user, **When** they create or modify a task, **Then** the task list reflects the change immediately without page reload.

---

### User Story 11 - Task Completion Toggle (Priority: P1) 🎯

As a user, I want to mark tasks as complete or incomplete so that I can track my progress. For recurring tasks, completing should generate the next instance.

**Why this priority**: Completion tracking is core to task management. Recurring task logic depends on completion.

**Independent Test**: User toggles completion status, and for recurring tasks, a new instance is auto-generated.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing an incomplete task, **When** they click the completion checkbox, **Then** the task is marked complete and visually updated (strikethrough, checkmark).

2. **Given** an authenticated user viewing a completed task, **When** they click to toggle it, **Then** the task is marked incomplete.

3. **Given** an authenticated user with a recurring task, **When** they mark it complete, **Then** a new instance is created with the next due date and linked via `parent_id`.

4. **Given** an authenticated user, **When** they mark a task complete, **Then** the change persists across sessions.

---

### User Story 12 - Task Editing (Priority: P1) 🎯

As a user, I want to edit all task fields including priority, tags, due date, and recurrence so that I can update task details as needed.

**Why this priority**: Tasks often need refinement. Full edit capability for all fields is essential.

**Independent Test**: User modifies task title, priority, tags, due date, and recurrence, with changes persisting.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing a task, **When** they select edit and modify the title and priority, **Then** both changes are saved.

2. **Given** an authenticated user editing a task, **When** they add a new tag to existing tags, **Then** all tags are preserved and the new one is added.

3. **Given** an authenticated user, **When** they attempt to edit a task to have no title, **Then** the system shows a validation error.

4. **Given** an authenticated user editing a recurring task, **When** they change recurrence from weekly to daily, **Then** future instances will be generated daily upon completion.

5. **Given** an authenticated user editing a task, **When** they cancel the edit, **Then** the original values are preserved.

---

### User Story 13 - Task Deletion (Priority: P1) 🎯

As a user, I want to delete tasks with a required reason so that I have an audit trail and can restore if needed.

**Why this priority**: Soft delete with reasons prevents data loss and provides accountability.

**Independent Test**: User deletes a task with reason, and it moves to "Deleted" view. User can restore it.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing a task, **When** they click delete, **Then** a modal appears requiring a deletion reason.

2. **Given** an authenticated user in the delete modal, **When** they provide reason "no longer relevant" and confirm, **Then** the task is soft-deleted with reason and timestamp.

3. **Given** an authenticated user, **When** they attempt to delete without a reason, **Then** the system prevents deletion and shows an error.

4. **Given** an authenticated user with multiple tasks, **When** they delete one, **Then** other tasks remain unaffected.

---

### Edge Cases

- **Duplicate task titles**: The system allows multiple tasks with the same title (no uniqueness constraint).
- **Empty task list**: New users see helpful onboarding content, not an error.
- **Session timeout during action**: Users attempting actions with expired tokens are redirected to login.
- **Simultaneous tab access**: Changes in one tab are reflected when switching to another tab (via React Query refetch).
- **Very long text inputs**: Title (256 chars), description (2000 chars), tags (50 chars each), deletion reason (500 chars).
- **Invalid due dates**: System validates date format and rejects invalid dates.
- **Recurring task completion edge cases**: If a recurring task is completed multiple times rapidly, each completion generates a new instance.
- **Restoring deleted tasks**: Restored tasks return to active list with original metadata intact except deletion_metadata is cleared.
- **Tag input**: Tag names are case-insensitive for filtering/search but preserve original case for display.

---

## Requirements

### Functional Requirements

**Authentication**:
- **FR-001**: System MUST allow users to create accounts with email and password.
- **FR-002**: System MUST require passwords of at least 8 characters.
- **FR-003**: System MUST validate email format during signup.
- **FR-004**: System MUST prevent duplicate email registration.
- **FR-005**: System MUST authenticate users via email and password combination.
- **FR-006**: System MUST issue JWT tokens upon successful authentication.
- **FR-007**: System MUST require JWT authentication for all task operations.
- **FR-016**: System MUST provide a logout function that invalidates the session.
- **FR-017**: System MUST display appropriate error messages for authentication failures.

**Task Creation & Editing**:
- **FR-008**: System MUST allow users to create tasks with a required title (max 256 characters).
- **FR-009**: System MUST allow optional task descriptions (max 2000 characters).
- **FR-018**: System MUST validate that task titles are not empty.
- **FR-019**: System MUST allow users to set task priority (HIGH, MEDIUM, LOW), defaulting to MEDIUM.
- **FR-020**: System MUST allow users to add multiple tags to a task (max 50 chars per tag).
- **FR-021**: System MUST allow users to set a due date as an ISO 8601 datetime.
- **FR-022**: System MUST allow users to set recurrence (NONE, DAILY, WEEKLY, MONTHLY), defaulting to NONE.
- **FR-012**: System MUST allow users to update all task fields (title, description, priority, tags, due_date, recurrence).

**Task Viewing & Filtering**:
- **FR-010**: System MUST return all active (non-deleted) tasks belonging to the authenticated user.
- **FR-011**: System MUST allow users to view a single task by ID.
- **FR-023**: System MUST allow filtering by priority (HIGH, MEDIUM, LOW).
- **FR-024**: System MUST allow filtering by tags (exact tag match).
- **FR-025**: System MUST allow filtering by completion status (complete, incomplete).
- **FR-026**: System MUST allow filtering by due date (overdue, due today, future).
- **FR-027**: System MUST allow sorting by ID, priority, title, status, due date.
- **FR-028**: System MUST allow search across title, description, and tags (case-insensitive).

**Task Completion & Recurrence**:
- **FR-014**: System MUST allow users to toggle task completion status.
- **FR-029**: System MUST auto-generate next instance when a recurring task is marked complete.
- **FR-030**: System MUST link recurring instances via `parent_id` field.
- **FR-031**: System MUST calculate next due date based on recurrence frequency (daily +1d, weekly +7d, monthly +30d).
- **FR-032**: System MUST allow users to stop recurrence for a task (set to NONE).

**Soft Delete & Restore**:
- **FR-013**: System MUST allow users to soft-delete their own tasks with a required reason (max 500 chars).
- **FR-033**: System MUST record deletion timestamp in ISO 8601 format.
- **FR-034**: System MUST exclude soft-deleted tasks from default list view.
- **FR-035**: System MUST provide a "Deleted Tasks" view showing all soft-deleted tasks with reasons.
- **FR-036**: System MUST allow users to restore soft-deleted tasks, clearing deletion metadata.

**Due Date Alerts**:
- **FR-037**: System MUST identify tasks with due dates in the past as "overdue".
- **FR-038**: System MUST identify tasks with due dates today as "due today".
- **FR-039**: System MUST display a notification banner on login if overdue or due-today tasks exist.

**Ownership & Security**:
- **FR-015**: System MUST enforce task ownership - users can only access their own tasks.
- **FR-040**: System MUST prevent users from viewing, editing, or deleting other users' tasks.

---

### Key Entities

**User**: Represents an authenticated user account. Attributes include unique identifier (UUID from JWT), email address, and password hash. Users own zero or more tasks.

**Task**: Represents a user task item. Attributes include:
- `id` (UUID): Unique identifier
- `title` (string, required, max 256 chars)
- `description` (string, optional, max 2000 chars)
- `completed` (boolean, defaults to false)
- `priority` (enum: HIGH/MEDIUM/LOW, defaults to MEDIUM)
- `tags` (array of strings, max 50 chars each)
- `due_date` (ISO 8601 datetime, optional)
- `recurrence` (enum: NONE/DAILY/WEEKLY/MONTHLY, defaults to NONE)
- `parent_id` (UUID, optional, references parent task for recurring instances)
- `deleted_at` (ISO 8601 datetime, optional, set when soft-deleted)
- `deletion_reason` (string, max 500 chars, required for soft delete)
- `owner_id` (UUID, foreign key to users)
- `created_at` (ISO 8601 datetime)
- `updated_at` (ISO 8601 datetime)

**User-Task Relationship**: One-to-many. A user creates, reads, updates, and deletes their own tasks. Tasks cannot be shared between users or transferred.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: New users can complete account creation in under 2 minutes.
- **SC-002**: Authenticated users can create a task with full metadata and see it appear in their list within 2 seconds.
- **SC-003**: Task completion toggle responds within 1 second of user interaction.
- **SC-004**: 95% of API requests complete successfully under normal load.
- **SC-005**: Users can reliably access their tasks across multiple devices after authentication.
- **SC-006**: Users can identify task priority, status, and due date urgency within 3 seconds of viewing the dashboard.
- **SC-007**: Zero unauthorized access - users can only view and modify their own tasks.
- **SC-008**: Users understand authentication errors and know how to resolve them (measured via user testing).
- **SC-009**: Users can successfully filter by priority and tags to find specific tasks within 5 seconds.
- **SC-010**: Recurring tasks auto-generate next instances 100% of the time upon completion.
- **SC-011**: Users can restore deleted tasks with 100% data integrity (all metadata preserved).
- **SC-012**: Overdue and due-today alerts are displayed within 1 second of dashboard load.

---

## Implementation Phases

### Phase 2A: Foundation + Core P1 Features (MVP)
- Authentication (US1)
- Task creation with all metadata (US2)
- Priority management (US3)
- Tags and categorization (US4)
- Due dates and reminders (US5)
- Task viewing with indicators (US10)
- Task completion toggle (US11)
- Task editing (US12)
- Task deletion with reasons (US13, soft delete)

### Phase 2B: Advanced P2 Features
- Recurring tasks (US6)
- Restore deleted tasks (US7)
- Advanced filtering and search (US8)
- Sorting and list management (US9)

### Phase 2C: Polish & Optimization
- Performance optimization
- Enhanced UI/UX
- Comprehensive testing
- Documentation

---

## Out of Scope (Future Phases)

- Task sharing between users
- Team/collaborative task lists
- Task comments or activity log
- File attachments
- Email notifications
- Mobile applications
- Calendar integration
- Subtasks or task hierarchy beyond recurring parent-child
- Custom recurrence patterns (e.g., every 2 weeks, specific days of week)
- Bulk operations (delete/complete multiple tasks at once)
