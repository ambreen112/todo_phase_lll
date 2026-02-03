# Feature Specification: Search, Filter, and Sort

**Feature Branch**: `003-search-filter-sort`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: Search by keyword; filter by status, priority, or tags; sort by due date, priority, or alphabetically

## Overview
Add search, filter, and sort capabilities to enable users to find and organize their todos efficiently.

## Agentic Structure
- **Main Agent**: Add commands for search, filter, sort
- **List/Search Subagent**: Implement search logic, filtering, sorting algorithms
- **Storage Skill**: No changes (uses existing get_all_todos)
- **Formatter Skill**: No changes (displays filtered/sorted results)

## Functional Requirements
- Search command: `search <keyword>` - finds todos matching title or description
- Filter by status: `list --status complete` or `--status incomplete`
- Filter by priority: `list --priority high` (already in PT spec)
- Filter by tag: `list --tag work` (already in PT spec)
- Sort by ID (default): `sort` or `list --sort id`
- Sort by priority: `list --sort priority` (high first, then medium, then low)
- Sort alphabetically: `list --sort title` (A-Z)
- Sort by status: `list --sort status` (complete first, then incomplete)
- Combined filters: `list --status complete --priority high`
- Combined search and filter: `search meeting --priority high`

## Non-Functional
- Search MUST be case-insensitive
- Sort MUST be stable (preserve order for equal values)
- Multiple filters MUST be AND logic (all conditions must match)
- Search with no filters returns all matching todos
- Empty filter results should show message "No matching todos found"

## Acceptance Criteria
- Search finds todos matching keyword in title or description
- Filter by status shows only complete or incomplete todos
- Filter by priority and tag work together
- Sort by priority orders high → medium → low
- Sort by title orders alphabetically A-Z
- Combine search with filters and sort
- Empty results show appropriate message

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search Todos (Priority: P1)

As a user, I want to search todos by keyword so that I can quickly find specific tasks.

**Why this priority**: Search is essential for finding tasks when list grows large; users shouldn't scroll through all todos to find one.

**Independent Test**: Add several todos, search for a keyword, verify only matching todos appear.

**Acceptance Scenarios**:
1. **Given** I have todos: "Buy groceries", "Weekly meeting", "Call mom", **When** I type "search meeting", **Then** only "Weekly meeting" appears in results
2. **Given** I have todo: "Review project documentation", **When** I type "search project", **Then** the todo appears (case-insensitive match)

---

### User Story 2 - Filter by Status (Priority: P2)

As a user, I want to filter todos by completion status so that I can focus on incomplete tasks or review completed work.

**Why this priority**: Status filtering helps users focus on actionable work; separating incomplete from complete improves productivity.

**Independent Test**: Add some complete and incomplete todos, filter by status, verify only matching todos appear.

**Acceptance Scenarios**:
1. **Given** I have 3 incomplete todos and 2 complete todos, **When** I type "list --status incomplete", **Then** only the 3 incomplete todos are displayed
2. **Given** I have completed tasks, **When** I type "list --status complete", **Then** only completed todos are displayed

---

### User Story 3 - Sort by Priority and Title (Priority: P3)

As a user, I want to sort todos by priority and title so that I can see them in logical order.

**Why this priority**: Sorting organizes tasks; priority sorting highlights urgent work, alphabetical sorting aids quick scanning.

**Independent Test**: Add todos with different priorities and titles, sort by each, verify order is correct.

**Acceptance Scenarios**:
1. **Given** I have todos with priorities high, low, medium, **When** I type "list --sort priority", **Then** todos display in order: high, medium, low
2. **Given** I have todos: "Buy milk", "Call doctor", "Send email", **When** I type "list --sort title", **Then** todos display alphabetically: "Buy milk", "Call doctor", "Send email"

---

### User Story 4 - Combined Search and Filter (Priority: P4)

As a user, I want to combine search with filters and sort so that I can find specific tasks matching multiple criteria.

**Why this priority**: Combined queries provide powerful task discovery; users often need to find high-priority work tasks about specific topics.

**Independent Test**: Add various todos with different priorities/tags, combine search and filters, verify correct subset appears sorted.

**Acceptance Scenarios**:
1. **Given** I have work and personal todos, **When** I type "search report --priority high --tag work", **Then** only high-priority work-tagged todos containing "report" are displayed
2. **Given** I search and filter, **When** no todos match, **Then** system shows "No matching todos found"

---

### Edge Cases

- What happens when searching for empty string or only whitespace?
- How to handle multiple sort criteria (e.g., sort by priority then by title)?
- What happens when filtering by invalid status value?
- How does system handle combining all filters with search?
- What if sort order is reversed (descending vs ascending)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-SFS-001**: System MUST provide `search <keyword>` command
- **FR-SFS-002**: Search MUST be case-insensitive
- **FR-SFS-003**: Search MUST match keywords in both title and description fields
- **FR-SFS-004**: List command MUST support `--status <complete|incomplete>` filter
- **FR-SFS-005**: List command MUST support `--sort <id|priority|title|status>` flag
- **FR-SFS-006**: Sort by priority MUST order: high → medium → low
- **FR-SFS-007**: Sort by title MUST order alphabetically A-Z
- **FR-SFS-008**: Sort by status MUST order: complete → incomplete
- **FR-SFS-009**: Multiple filters MUST be combined with AND logic
- **FR-SFS-010**: Search command MUST support combining with filter flags
- **FR-SFS-011**: System MUST display "No matching todos found" when results are empty
- **FR-SFS-012**: Sort order MUST be stable (preserve original order for equal values)
- **FR-SFS-013**: Invalid filter/sort values MUST show error messages

### Key Entities *(include if feature involves data)*

- **Search Query**: String keyword(s) for matching against todo title and description
- **Filter Criteria**: Set of conditions (status, priority, tags) that todos must satisfy
- **Sort Order**: Field (id, priority, title, status) and direction (ascending) for ordering results

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-SFS-001**: Search command finds todos matching keyword in title or description
- **SC-SFS-002**: Filter by status returns only matching todos
- **SC-SFS-003**: Sort by priority orders todos correctly (high → medium → low)
- **SC-SFS-004**: Sort by title orders todos alphabetically A-Z
- **SC-SFS-005**: Multiple filters combined with AND logic work correctly
- **SC-SFS-006**: Search combined with filters returns correct subset
- **SC-SFS-007**: Empty results display appropriate message
- **SC-SFS-008**: Invalid filter/sort values show clear error messages
- **SC-SFS-009**: All combinations of filters and sort work without errors
