# Feature Specification: Due Dates and Time Reminders

**Feature Branch**: `004-due-dates-reminders`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: Set deadlines with date/time pickers; browser notifications for reminders

## Overview
Add due date and time fields to todos with reminder functionality to alert users before deadlines.

## Agentic Structure
- **Main Agent**: Parse `--due` flag for date/time input
- **Add/Update Subagent**: Handle setting/modifying due dates
- **List/Search Subagent**: Display due dates; filter by overdue/due today
- **Notification Skill** (NEW): Check due dates and display alerts
- **Formatter Skill**: Update display to show due date column with urgency indicators

## Functional Requirements
- Todo model MUST have `due_date` field (ISO 8601 datetime string or None)
- Add command MUST accept `--due <date>` flag (formats: YYYY-MM-DD, YYYY-MM-DD HH:MM)
- Update command MUST support `--due <date>` flag
- List command MUST show due date column
- Overdue todos highlighted in red or with ⚠ symbol
- Due today highlighted in yellow or with ⏰ symbol
- Filter by due: `list --due today` (tasks due today)
- Filter by overdue: `list --due overdue` (overdue tasks)
- `remind` command to check and show upcoming reminders
- Auto-reminder when app starts: show overdue and due today tasks

## Non-Functional
- Date format MUST be YYYY-MM-DD or YYYY-MM-DD HH:MM
- Due date is optional (None if not set)
- Time defaults to 00:00 if only date provided
- Comparisons must use UTC timezone
- Reminder alert when task is overdue or due today
- Browser notifications not required (in-app alerts only for MVP)

## Acceptance Criteria
- Add todo with due date, verify it's stored and displayed
- Update todo due date, verify change persists
- List todos, see due date column with urgency indicators
- Filter by overdue shows only past-due tasks
- Filter by due today shows today's tasks
- Remind command shows upcoming/due tasks
- App startup shows overdue and due today alerts

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Todo with Due Date (Priority: P1)

As a user, I want to set due dates for tasks so that I can track deadlines and manage time-sensitive work.

**Why this priority**: Due dates are essential for time management; tasks without deadlines often get delayed.

**Independent Test**: Add todo with due date, list and verify due date appears with correct formatting.

**Acceptance Scenarios**:
1. **Given** I have started app, **When** I type "add Project report --due 2025-01-15", **Then** todo has due_date="2025-01-15T00:00:00"
2. **Given** I type "add Meeting --due 2025-01-15 14:00", **Then** todo has due_date="2025-01-15T14:00:00"

---

### User Story 2 - Filter Overdue and Due Today Tasks (Priority: P2)

As a user, I want to see overdue and due today tasks so that I can prioritize urgent work.

**Why this priority**: Users need to quickly identify tasks that are late or due immediately for effective prioritization.

**Independent Test**: Add tasks with past, today, and future due dates, filter by overdue/due today, verify results.

**Acceptance Scenarios**:
1. **Given** I have tasks due yesterday, today, and tomorrow, **When** I type "list --due overdue", **Then** only yesterday's task appears marked with ⚠
2. **Given** I have tasks due today and tomorrow, **When** I type "list --due today", **Then** only today's tasks appear marked with ⏰

---

### User Story 3 - Remind for Upcoming Tasks (Priority: P3)

As a user, I want to see reminders for overdue and due today tasks so that I don't miss deadlines.

**Why this priority**: Proactive reminders prevent missed deadlines; users shouldn't have to remember to check due dates manually.

**Independent Test**: Create overdue and due today tasks, run remind command, verify alerts are shown.

**Acceptance Scenarios**:
1. **Given** I have 2 overdue tasks, **When** I type "remind" or start app, **Then** system shows "You have 2 overdue tasks:" with task details
2. **Given** I have tasks due today, **When** I type "remind", **Then** system shows "Tasks due today:" with task details

---

### User Story 4 - Update Due Date (Priority: P4)

As a user, I want to change due dates of existing tasks so that I can adjust deadlines as priorities change.

**Why this priority**: Deadlines change due to project delays or reprioritization; users need to update without recreating tasks.

**Independent Test**: Create todo with due date, update it to new date, verify change persists.

**Acceptance Scenarios**:
1. **Given** I have a todo with due date "2025-01-15", **When** I type "update 1 --due 2025-01-20", **Then** todo due_date changes to "2025-01-20"
2. **Given** I want to remove due date, **When** I type "update 1 --due none", **Then** todo due_date becomes None

---

### Edge Cases

- What happens when user provides invalid date format?
- How to handle timezone differences?
- What happens when task is exactly at current time?
- How to display relative time (e.g., "2 days left", "overdue by 3 days")?
- What if user provides only time without date?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-DD-001**: Todo model MUST include `due_date` field (ISO 8601 datetime string or None)
- **FR-DD-002**: Add command MUST accept `--due <date>` flag
- **FR-DD-003**: Add command MUST accept `--due <date> <time>` flag (format: YYYY-MM-DD HH:MM)
- **FR-DD-004**: Update command MUST support `--due <date>` flag
- **FR-DD-005**: Update command MUST support `--due none` to remove due date
- **FR-DD-006**: List command MUST display due date column
- **FR-DD-007**: Overdue tasks MUST be marked with ⚠ symbol or red color
- **FR-DD-008**: Due today tasks MUST be marked with ⏰ symbol or yellow color
- **FR-DD-009**: List command MUST support `--due overdue` filter
- **FR-DD-010**: List command MUST support `--due today` filter
- **FR-DD-011**: System MUST provide `remind` command
- **FR-DD-012**: App MUST show overdue and due today alerts on startup
- **FR-DD-013**: System MUST validate date format and show error for invalid input
- **FR-DD-014**: Time MUST default to 00:00 if only date is provided

### Key Entities *(include if feature involves data)*

- **Due Date**: ISO 8601 datetime string (YYYY-MM-DDTHH:MM:SS) or None; represents task deadline
- **Reminder Alert**: Notification shown for overdue/due today tasks with task details and urgency level

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-DD-001**: Users can add todos with due dates successfully
- **SC-DD-002**: Users can update todo due dates successfully
- **SC-DD-003**: List display shows due date column correctly formatted
- **SC-DD-004**: Overdue tasks are clearly marked (⚠ symbol)
- **SC-DD-005**: Due today tasks are clearly marked (⏰ symbol)
- **SC-DD-006**: Filter by overdue returns only past-due tasks
- **SC-DD-007**: Filter by due today returns only today's tasks
- **SC-DD-008**: Remind command shows upcoming/due tasks
- **SC-DD-009**: App startup shows overdue and due today alerts
- **SC-DD-010**: Invalid date formats show clear error messages
