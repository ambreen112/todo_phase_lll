# Feature Specification: Recurring Tasks

**Feature Branch**: `005-recurring-tasks`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: Auto-reschedule repeating tasks (e.g., "weekly meeting")

## Overview
Support recurring tasks that automatically create new instances after completion based on frequency (daily, weekly, monthly).

## Agentic Structure
- **Main Agent**: Parse `--recur <frequency>` flag
- **Add/Update Subagent**: Handle setting/moving recurrence
- **List/Search Subagent**: Display recurrence indicators
- **Recurring Skill** (NEW): Handle auto-rescheduling on completion
- **Storage Skill**: Update to track recurring tasks and instances
- **Formatter Skill**: Show recurrence symbol (🔄) in list

## Functional Requirements
- Todo model MUST have `recurrence` field (enum: none, daily, weekly, monthly, default: none)
- Todo model MUST have `parent_id` field (int or None) to link recurring instances
- Add command MUST accept `--recur <daily|weekly|monthly>` flag
- Update command MUST support `--recur <daily|weekly|monthly>` flag
- Update command MUST support `--recur none` to stop recurrence
- When recurring task is marked complete, auto-create new instance for next period
- New instance preserves title, description, priority, tags from parent
- New instance's due date calculated based on frequency and previous instance
- List MUST show 🔄 symbol for recurring tasks
- Stop recurrence flag: `stop-recur <id>` (marks instance as non-recurring)

## Non-Functional
- Recurrence defaults to 'none' if not specified
- Parent task is not deleted when completing; instances are created
- First instance is the "template" for future instances
- Weekly recurrence adds 7 days to due date
- Monthly recurrence adds 30 days to due date
- Daily recurrence adds 1 day to due date
- If no due date, recurrence creates task with updated date only

## Acceptance Criteria
- Add recurring task, verify recurrence field and 🔄 symbol
- Complete recurring task, verify new instance created for next period
- Stop recurrence on task, verify no more instances created
- List shows 🔄 for recurring tasks
- Update recurrence frequency, verify new instances use new frequency

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Recurring Task (Priority: P1)

As a user, I want to create recurring tasks so that I don't have to manually recreate periodic tasks like weekly meetings.

**Why this priority**: Recurring tasks are common in real life (weekly reports, monthly bills, daily standups); auto-rescheduling saves time.

**Independent Test**: Add daily recurring task, complete it, verify new instance appears for next day.

**Acceptance Scenarios**:
1. **Given** I have started app, **When** I type "add Daily standup --recur daily --tag work", **Then** todo has recurrence="daily" and shows 🔄 in list
2. **Given** I add "Weekly team meeting --due 2025-01-08 --recur weekly", **Then** todo has due date and recurrence set

---

### User Story 2 - Auto-reschedule on Completion (Priority: P2)

As a user, I want recurring tasks to automatically create new instances when completed so that I don't forget to recreate them.

**Why this priority**: Manual recreation is error-prone; auto-rescheduling ensures consistency.

**Independent Test**: Create weekly recurring task with due date, complete it, verify new instance appears with due date +7 days.

**Acceptance Scenarios**:
1. **Given** I have a weekly recurring task due on "2025-01-08", **When** I mark it complete, **Then** new instance created with due date "2025-01-15"
2. **Given** I have a daily recurring task, **When** I complete it, **Then** new instance appears for next day

---

### User Story 3 - Stop Recurrence (Priority: P3)

As a user, I want to stop a task from recurring so that I can end repeating tasks that are no longer needed.

**Why this priority**: Not all recurring tasks are permanent; users need to end them without deleting history.

**Independent Test**: Create recurring task, complete multiple times, then stop recurrence, verify no new instances created.

**Acceptance Scenarios**:
1. **Given** I have a recurring task, **When** I type "update 1 --recur none" or "stop-recur 1", **Then** task recurrence changes to "none" and no more instances created
2. **Given** I complete a non-recurring task instance, **When** I list todos, **Then** no new instance appears

---

### User Story 4 - Update Recurrence Frequency (Priority: P4)

As a user, I want to change recurrence frequency of a task so that I can adjust periodicity as needs change.

**Why this priority**: Task frequency can change (e.g., weekly meeting becomes bi-weekly); update without recreate needed.

**Independent Test**: Create weekly recurring task, update to daily, verify new instances created daily instead of weekly.

**Acceptance Scenarios**:
1. **Given** I have a weekly recurring task, **When** I type "update 1 --recur daily", **Then** task recurrence changes to "daily" and future instances follow new frequency
2. **Given** I change recurrence, **When** I complete current instance, **Then** next instance uses new frequency

---

### Edge Cases

- What happens when recurring task has no due date (how to calculate next instance)?
- How to handle recurrence when task is deleted?
- What happens if user completes recurring task multiple times quickly?
- How to handle time zones in due date calculations?
- What happens if recurrence frequency is changed while instances already exist?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-RT-001**: Todo model MUST include `recurrence` field (enum: none, daily, weekly, monthly)
- **FR-RT-002**: Todo model MUST include `parent_id` field (int or None) for linking instances
- **FR-RT-003**: Add command MUST accept `--recur <daily|weekly|monthly>` flag
- **FR-RT-004**: Update command MUST support `--recur <daily|weekly|monthly|none>` flag
- **FR-RT-005**: System MUST provide `stop-recur <id>` command
- **FR-RT-006**: When recurring task is marked complete, system MUST auto-create new instance
- **FR-RT-007**: New instance MUST preserve title, description, priority, tags from parent
- **FR-RT-008**: New instance's due date MUST be calculated based on frequency
- **FR-RT-009**: Daily recurrence MUST add 1 day to due date
- **FR-RT-010**: Weekly recurrence MUST add 7 days to due date
- **FR-RT-011**: Monthly recurrence MUST add 30 days to due date
- **FR-RT-012**: List display MUST show 🔄 symbol for recurring tasks
- **FR-RT-013**: Recurrence MUST default to 'none' if not specified
- **FR-RT-014**: System MUST validate recurrence values and show error for invalid input

### Key Entities *(include if feature involves data)*

- **Recurrence**: Enum with values NONE, DAILY, WEEKLY, MONTHLY; determines auto-reschedule frequency
- **Parent Task**: Original recurring task that serves as template for instances
- **Instance**: Auto-created task copy with calculated due date and parent_id reference

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-RT-001**: Users can add tasks with recurrence successfully
- **SC-RT-002**: Users can update task recurrence successfully
- **SC-RT-003**: List display shows 🔄 symbol for recurring tasks
- **SC-RT-004**: Completing recurring task creates new instance with correct due date
- **SC-RT-005**: New instance preserves title, description, priority, tags from parent
- **SC-RT-006**: Stopping recurrence prevents new instances from being created
- **SC-RT-007**: Updating recurrence frequency changes future instance schedule
- **SC-RT-008**: Daily/weekly/monthly recurrence calculates next due date correctly
