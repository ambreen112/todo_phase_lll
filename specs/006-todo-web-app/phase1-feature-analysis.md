# Phase 1 CLI Application - Complete Feature Analysis

**Date**: 2026-01-08
**Purpose**: Comprehensive review of Phase 1 features for Phase 2 migration

---

## Phase 1 Feature Inventory

### 1. **Core Task Fields**

| Field | Type | Details | Current Phase 2 Status |
|-------|------|---------|----------------------|
| `id` | int | Auto-incremented unique identifier | ✅ Implemented (as UUID) |
| `title` | str | Required, task title (previously `task` field) | ✅ Implemented |
| `description` | Optional[str] | Detailed task description | ✅ Implemented |
| `complete` | bool | Completion status, defaults to False | ✅ Implemented (as `completed`) |
| `deletion_metadata` | Optional[dict] | `{"reason": str, "timestamp": ISO8601}` | ❌ Missing |
| `priority` | Priority enum | HIGH, MEDIUM, LOW (defaults to MEDIUM) | ❌ Missing |
| `tags` | List[str] | Multiple categorization labels | ❌ Missing |
| `due_date` | Optional[str] | ISO 8601 datetime string | ❌ Missing |
| `recurrence` | Recurrence enum | NONE, DAILY, WEEKLY, MONTHLY | ❌ Missing |
| `parent_id` | Optional[int] | Parent todo ID for recurring instances | ❌ Missing |

### 2. **Priority System**

**Enum Definition**:
```python
class Priority(Enum):
    HIGH = "high"      # Visual indicator: 🔴
    MEDIUM = "medium"  # Visual indicator: 🟡
    LOW = "low"        # Visual indicator: 🟢
```

**Features**:
- Default priority is MEDIUM for new tasks
- Filter by priority: `list --priority high`
- Sort by priority: `list --sort priority`
- Update priority: `update <id> --priority high`
- Search with priority filter: `search <keyword> --priority high`

**Current Phase 2 Status**: ❌ Not implemented

---

### 3. **Tags/Categories System**

**Implementation**:
- Multiple tags per task stored as `List[str]`
- Add tags on creation: `add <title> --tag work,urgent`
- Filter by tag: `list --tag work`
- Search by tag: tasks match if keyword found in any tag
- Update tags: `update <id> --tag newtag1,newtag2`

**Use Cases**:
- Categorization: work, personal, shopping, etc.
- Context-based filtering
- Cross-cutting organization independent of status/priority

**Current Phase 2 Status**: ❌ Not implemented

---

### 4. **Due Dates & Reminders**

**Implementation**:
- Due date stored as ISO 8601 datetime string
- Add due date: `add <title> --due 2026-01-15`
- Update due date: `update <id> --due 2026-01-20`
- Remove due date: `update <id> --due none`

**Automatic Alerts**:
- **Startup Alert**: Shows overdue and due-today tasks when app launches
- **Overdue Tasks**: `⚠` indicator, date in past
- **Due Today Tasks**: `⏰` indicator, date is today
- **Manual Reminder**: `remind` command shows overdue and due-today lists

**Filtering**:
- `list --due overdue`: Show only overdue tasks
- `list --due today`: Show only tasks due today

**Current Phase 2 Status**: ❌ Not implemented

---

### 5. **Recurring Tasks**

**Enum Definition**:
```python
class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
```

**Features**:
- Add recurrence: `add <title> --recur weekly`
- Visual indicator: `🔄` in list view
- Update recurrence: `update <id> --recur daily`
- Stop recurrence: `stop-recur <id>` (sets to NONE)
- Parent-child relationship: `parent_id` field links recurring instances

**How It Works**:
- When a recurring task is completed, a new instance is auto-generated
- New instance inherits: title, description, priority, tags, recurrence
- New instance gets: new ID, new due date (calculated based on frequency), `parent_id` pointing to original

**Current Phase 2 Status**: ❌ Not implemented

---

### 6. **Soft Delete with Reasons**

**Implementation**:
```python
deletion_metadata = {
    "reason": str,        # User-provided reason (required, max 500 chars)
    "timestamp": str      # ISO 8601 timestamp of deletion
}
```

**Features**:
- Delete with reason: `delete <id> <reason text>`
- Reason is required (cannot be empty)
- Soft delete: Task stays in storage, marked with `deletion_metadata`
- List deleted: `list-deleted` shows all deleted tasks with reasons/timestamps
- Restore: `restore <id>` clears `deletion_metadata`, returns to active
- Active list excludes deleted: `get_all_todos()` filters out `is_deleted=True`

**Business Value**:
- Audit trail for why tasks were removed
- Ability to undo accidental deletions
- Historical record of removed tasks

**Current Phase 2 Status**: ❌ Not implemented (hard delete only)

---

### 7. **Advanced Filtering & Search**

**List Command Filters**:
```bash
list --priority <high|med|low>      # Filter by priority
list --tag <tag>                    # Filter by tag
list --status <complete|incomplete> # Filter by completion status
list --due <overdue|today>          # Filter by due date
list --sort <id|priority|title|status>  # Sort results
```

**Search Command**:
```bash
search <keyword> [filters]
```
- Searches across: title, description, tags (case-insensitive)
- Can combine with filters: `search urgent --priority high --tag work`
- Can apply sorting: `search meeting --sort priority`

**Current Phase 2 Status**:
- ✅ Basic filtering by completion status (completed/active)
- ❌ Priority, tags, due date filtering
- ❌ Multi-field search
- ❌ Sorting

---

### 8. **Sorting Capabilities**

**Sort Fields**:
- `--sort id`: Ascending by ID
- `--sort priority`: HIGH → MEDIUM → LOW
- `--sort title`: Alphabetical (case-insensitive)
- `--sort status`: Incomplete first, then completed

**Applies To**:
- List command
- Search results

**Current Phase 2 Status**: ❌ Not implemented

---

### 9. **Visual Formatting (CLI-Specific)**

**Console Table Format**:
```
ID  | Pri    | Title                | Tags            | Due          | Status
----------------------------------------------------------------------------------
1   | 🔴 HI  | Buy Milk             | grocery         |              | Incomplete
2   | 🟡 ME  | Weekly Sync          | work            | 2026-01-01   | 🔄 Incomplete
```

**Visual Indicators**:
- Priority: 🔴 HIGH, 🟡 MEDIUM, 🟢 LOW
- Recurring: 🔄
- Overdue: ⚠
- Due Today: ⏰
- Completed: ✅

**Note**: Phase 2 web UI will need its own visual design for these concepts

---

### 10. **Other Commands**

| Command | Purpose | Phase 2 Equivalent |
|---------|---------|-------------------|
| `complete <id>` | Mark as complete | ✅ PATCH toggle endpoint |
| `incomplete <id>` | Mark as incomplete | ✅ PATCH toggle endpoint |
| `update <id> [options]` | Update task fields | ✅ PUT endpoint (partial) |
| `remind` | Show overdue/due today | ❌ Need notification/alert system |
| `stop-recur <id>` | Stop recurrence | ❌ Need recurrence management |
| `list-deleted` | View deleted tasks | ❌ Need soft-delete system |
| `restore <id>` | Restore deleted task | ❌ Need restore endpoint |

---

## Feature Gaps Summary

### Missing from Phase 2:

1. **Priority System** (HIGH/MEDIUM/LOW)
2. **Tags/Categories** (multiple per task)
3. **Due Dates** with overdue/today detection
4. **Reminders/Alerts** for due dates
5. **Recurring Tasks** (daily/weekly/monthly)
6. **Soft Delete** with deletion reasons
7. **Restore Deleted Tasks**
8. **Advanced Filtering** (by priority, tags, due date)
9. **Search** across multiple fields
10. **Sorting** (by priority, title, status)

### Architectural Considerations:

**Phase 1 (CLI)**:
- Single-user, in-memory storage
- Synchronous operations
- Text-based UI with emoji indicators
- Auto-incrementing integer IDs

**Phase 2 (Web)**:
- Multi-user with authentication
- Database persistence (PostgreSQL)
- Graphical web UI (React)
- UUID-based IDs
- RESTful API architecture

---

## Migration Recommendations

### Data Model Changes Required:

```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN tags TEXT[];  -- PostgreSQL array type
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN recurrence VARCHAR(10) DEFAULT 'none';
ALTER TABLE tasks ADD COLUMN parent_id UUID REFERENCES tasks(id);
ALTER TABLE tasks ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN deletion_reason TEXT;
```

### API Endpoints to Add/Modify:

**New Endpoints**:
- `GET /api/{user_id}/tasks/deleted` - List deleted tasks
- `POST /api/{user_id}/tasks/{id}/restore` - Restore deleted task
- `GET /api/{user_id}/tasks/overdue` - Get overdue tasks
- `GET /api/{user_id}/tasks/due-today` - Get tasks due today
- `POST /api/{user_id}/tasks/{id}/stop-recurrence` - Stop recurring

**Modified Endpoints**:
- `GET /api/{user_id}/tasks` - Add query params: `?priority=high&tag=work&due=overdue&sort=priority`
- `POST /api/{user_id}/tasks` - Accept priority, tags, due_date, recurrence
- `PUT /api/{user_id}/tasks/{id}` - Accept priority, tags, due_date, recurrence updates
- `DELETE /api/{user_id}/tasks/{id}` - Change to soft delete, require `reason` in body

### UI Components to Add:

- Priority selector (dropdown or buttons)
- Tag input with multi-select
- Date picker for due dates
- Recurrence selector (none/daily/weekly/monthly)
- Overdue/due-today badge indicators
- Deleted tasks view with restore button
- Delete confirmation modal with reason input
- Advanced filter panel
- Sort dropdown
- Search bar with multi-field search

---

## Next Steps

1. ✅ Document Phase 1 features (this file)
2. ⏳ Update `spec.md` with new user stories
3. ⏳ Update `data-model.md` with new fields
4. ⏳ Update `tasks.md` with implementation plan
5. ⏳ Create migration scripts
6. ⏳ Implement features incrementally
