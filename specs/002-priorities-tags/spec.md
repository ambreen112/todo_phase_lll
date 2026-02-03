# Feature Specification: Priorities and Tags/Categories

**Feature Branch**: `002-priorities-tags`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: Add priority levels (high/medium/low) and tags/categories (work/home) to todos

## Overview
Extend todo app to support priority levels (high, medium, low) and tags/categories for better task organization and management.

## Agentic Structure
- **Main Agent**: Update command parsing to handle priority and tag arguments
- **Add/Update Subagent**: Handle setting priority and tags when creating/updating todos
- **List/Search Subagent**: Support filtering and displaying by priority/tags
- **Storage Skill**: No changes needed (Todo model extends)
- **Formatter Skill**: Update display to show priority and tags columns

## Functional Requirements
- Todo model MUST have `priority` field (enum: high, medium, low, default: medium)
- Todo model MUST have `tags` field (list of strings, e.g., ["work", "project"])
- Add command MUST accept `--priority <high|medium|low>` flag
- Add command MUST accept `--tag <tag1,tag2,...>` flag
- Update command MUST support changing priority
- Update command MUST support adding/removing tags
- List command MUST show priority column with color coding or symbols
- Filter todos by priority: `list --priority high`
- Filter todos by tag: `list --tag work`

## Non-Functional
- Priority MUST default to 'medium' if not specified
- Tags MUST be case-insensitive for filtering
- Multiple tags MUST be supported per todo
- Backward compatible with existing todos (priority defaults to medium, tags empty)

## Acceptance Criteria
- Add todo with priority and tags, verify they are stored and displayed correctly
- Update todo priority and tags, verify changes persist
- List todos, see priority and tags columns
- Filter by priority `list --priority high`, only show high priority tasks
- Filter by tag `list --tag work`, only show work-tagged tasks
- Existing todos without priority/tags still work (defaults applied)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Todo with Priority (Priority: P1)

As a user, I want to assign priority levels to tasks so that I can focus on the most important work first.

**Why this priority**: Priority is fundamental for task management - allows users to distinguish urgent tasks from less critical ones.

**Independent Test**: Add todo with high priority, add another with low priority, list and verify priorities are shown.

**Acceptance Scenarios**:
1. **Given** I have started the app, **When** I type "add Urgent meeting --priority high --tag work", **Then** todo has priority="high" and tags=["work"]
2. **Given** I add a todo without specifying priority, **When** I list todos, **Then** todo shows priority="medium" (default)

---

### User Story 2 - Add Todo with Multiple Tags (Priority: P2)

As a user, I want to assign multiple tags/categories to tasks so that I can organize them by context (work, home, project, etc.).

**Why this priority**: Tags provide flexible categorization beyond simple priority levels, enabling context-based task management.

**Independent Test**: Add todo with tags "work,urgent", filter by tag, verify it appears.

**Acceptance Scenarios**:
1. **Given** I type "add Weekly report --tag work,project", **When** I list todos, **Then** todo shows tags="work, project"
2. **Given** I have multiple todos with different tags, **When** I type "list --tag work", **Then** only work-tagged todos are displayed

---

### User Story 3 - Update Priority and Tags (Priority: P3)

As a user, I want to change the priority and tags of existing tasks so that I can adjust my task organization as priorities change.

**Why this priority**: Tasks evolve over time; users need to update priority and tags without recreating the task.

**Independent Test**: Create todo, then update its priority and tags, verify changes are reflected.

**Acceptance Scenarios**:
1. **Given** I have a todo with ID 1 and priority="medium", **When** I type "update 1 --priority high", **Then** todo priority changes to "high"
2. **Given** I have a todo with ID 1 and tags=["work"], **When** I type "update 1 --tag work,urgent", **Then** todo tags update to ["work", "urgent"]

---

### Edge Cases

- What happens when user provides invalid priority value (not high/medium/low)?
- How to handle tags with special characters or spaces?
- What happens when filtering by tag that doesn't exist on any todo?
- How to handle removing a tag from a todo (e.g., `--tag -work`)?
- What happens when filtering by multiple criteria simultaneously?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-PT-001**: Todo model MUST include `priority` field accepting values: high, medium, low
- **FR-PT-002**: Todo model MUST include `tags` field as list of strings
- **FR-PT-003**: Priority MUST default to 'medium' if not specified during add
- **FR-PT-004**: Add command MUST accept `--priority <value>` flag
- **FR-PT-005**: Add command MUST accept `--tag <comma,separated,tags>` flag
- **FR-PT-006**: Update command MUST support `--priority <value>` flag
- **FR-PT-007**: Update command MUST support `--tag <comma,separated,tags>` flag (replaces existing tags)
- **FR-PT-008**: List command MUST show priority column in output table
- **FR-PT-009**: List command MUST show tags column in output table
- **FR-PT-010**: List command MUST support `--priority <high|medium|low>` filter flag
- **FR-PT-011**: List command MUST support `--tag <tagname>` filter flag
- **FR-PT-012**: System MUST validate priority values and show error for invalid input
- **FR-PT-013**: Tags MUST be case-insensitive for filtering and display

### Key Entities *(include if feature involves data)*

- **Priority**: Enum with values HIGH, MEDIUM, LOW; default is MEDIUM
- **Tag**: String label for categorization; multiple tags per todo; case-insensitive
- **Todo**: Extended with priority (enum) and tags (list) fields

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-PT-001**: Users can add todos with priority and tags successfully
- **SC-PT-002**: Users can update todo priority and tags successfully
- **SC-PT-003**: List display shows priority and tags columns correctly formatted
- **SC-PT-004**: Filter by priority returns only matching todos
- **SC-PT-005**: Filter by tag returns only matching todos
- **SC-PT-006**: Invalid priority values show clear error messages
- **SC-PT-007**: Existing todos without priority/tags work with default values
- **SC-PT-008**: Multiple tags per todo are stored and displayed correctly
