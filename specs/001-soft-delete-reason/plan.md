# Implementation Plan: Soft Delete with Reason Tracking

**Branch**: `001-soft-delete-reason` | **Date**: 2025-12-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-soft-delete-reason/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add soft delete capability to the Todo CLI app with deletion reason tracking. The system will mark todos as deleted instead of permanently removing them, while maintaining backward compatibility with all existing commands. New commands (`list-deleted`, `restore`) and modified `delete` command (now requires reason) will be added.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (pure Python, in-memory storage)
**Storage**: In-memory list (existing StorageSkill)
**Testing**: pytest (existing test framework)
**Target Platform**: Linux/macOS/WSL (CLI application)
**Project Type**: single
**Performance Goals**: <100ms for all CRUD operations
**Constraints**: Must maintain backward compatibility with existing commands
**Scale/Scope**: In-memory application supporting hundreds of todos per session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file is in template state with no active principles. This feature aligns with the existing agentic architecture pattern used in the Todo app (001-todo-app).

## Project Structure

### Documentation (this feature)

```text
specs/001-soft-delete-reason/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── todo.py              # MODIFIED: Add deletion_metadata field
├── skills/
│   └── storage_skill.py     # MODIFIED: Add soft delete filtering, restore capability
├── agents/
│   ├── main_agent.py        # MODIFIED: New commands (list-deleted, restore), updated delete parsing
│   ├── delete_complete_agent.py  # MODIFIED: Soft delete with reason
│   └── list_search_agent.py     # MODIFIED: list-deleted command
└── cli/
    └── todo_app.py          # NO CHANGES (entry point)

tests/
├── test_soft_delete.py      # NEW: Acceptance tests for soft delete feature
├── unit/
│   ├── test_todo_model.py   # MODIFIED: Test deletion metadata
│   └── test_storage_skill.py # MODIFIED: Test soft delete methods
└── integration/
    └── test_soft_delete_integration.py  # NEW: End-to-end tests
```

**Structure Decision**: Single project structure following the existing Todo app pattern. All modifications extend the current agentic architecture without breaking changes.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | Constitution is in template state |

## Design Decisions Summary

### Data Model Changes
- Add `deletion_metadata` optional field to Todo model
- DeletionRecord as inner class/dict within Todo

### Storage Layer Changes
- Modify `delete_todo_by_id()` to soft delete instead of hard delete
- Add `get_deleted_todos()` method
- Add `restore_todo_by_id()` method
- Filter deleted items in `get_all_todos()` (default behavior)
- Optional parameter to include deleted in queries

### Command Interface Changes
- **BREAKING**: `delete <id>` → `delete <id> <reason>` (requires reason argument)
- NEW: `list-deleted` - Show all deleted items with reasons
- NEW: `restore <id>` - Restore deleted todo to active status
- NO CHANGES: `add`, `list`, `update`, `complete` (backward compatible)

### Backward Compatibility Strategy
- All existing commands (except delete signature change) work identically
- Default `list` command excludes deleted items (maintains current behavior)
- Delete command change is intentional and documented in help text

---

## Phase 0: Research & Decisions

### Decision 1: Soft Delete Data Model
Add `deletion_metadata` optional dict field to Todo model containing `reason` and `timestamp`.

### Decision 2: Storage Layer Filtering
Modify `get_all_todos()` to filter deleted items by default. Add `get_deleted_todos()` method.

### Decision 3: Delete Command Breaking Change
Change `delete <id>` to `delete <id> <reason>` - intentional breaking change.

### Decision 4: Command Naming
Use kebab-case: `list-deleted`, `restore`.

### Decision 5: Restore Behavior
Clear `deletion_metadata` to None when restoring.

### Decision 6: Error Handling
Return False from storage methods, let agent layer format error messages.

### Decision 7: Reason Length Validation
Validate in DeleteCompleteAgent, limit to 500 characters.

### Decision 8: Backward Compatibility
Only delete command tests need updates; all other commands work identically.

---

## Phase 1: Design Artifacts

### Data Model

**Todo Entity**:
```python
Todo:
  - id: int (required)
  - task: str (required)
  - complete: bool (required)
  - deletion_metadata: Optional[dict] (optional)
    - reason: str
    - timestamp: str (ISO format)
```

**Deletion States**:
- Active: `deletion_metadata = None`
- Deleted: `deletion_metadata = {"reason": "...", "timestamp": "..."}`

**Validation Rules**:
- Reason must not be empty or whitespace only
- Reason maximum 500 characters
- Timestamp automatically set on deletion

### API Contracts (CLI Interface)

| Command | Signature | Behavior | Returns |
|----------|------------|----------|----------|
| `delete <id> <reason>` | 2+ args | Soft delete with reason | Success/error message |
| `list-deleted` | 0 args | Show deleted items with reasons | Formatted table |
| `restore <id>` | 1 arg | Restore todo to active | Success/error message |
| `list` | 0 args | Show active todos only | Formatted table (unchanged) |

**Error Responses**:
- Invalid ID: "Error: ID must be a number."
- Not found: "Error: Todo with ID {id} not found."
- Missing reason: "Usage: delete <id> <reason>"
- Empty reason: "Error: Deletion reason cannot be empty."
- Reason too long: "Error: Deletion reason must be 500 characters or less."
- Already active: "Error: Todo {id} is not deleted."
- Already deleted: "Error: Todo {id} is already deleted."

### Quick Start

**Modified Files**:
1. `src/models/todo.py` - Add `deletion_metadata` field
2. `src/skills/storage_skill.py` - Soft delete, `get_deleted_todos()`, `restore_todo_by_id()`
3. `src/agents/delete_complete_agent.py` - Update `delete_todo(todo_id, reason)`
4. `src/agents/list_search_agent.py` - Add `list_deleted_todos()`
5. `src/agents/main_agent.py` - New command handlers for `list-deleted`, `restore`
6. `src/skills/formatter_skill.py` - Add `format_deleted_list()` (optional)

**New Tests**:
- `tests/test_soft_delete.py` - Acceptance tests
- Integration tests for full delete-list-restore workflow

---

## Phase 2: Implementation Tasks

See [tasks.md](tasks.md) (generated by `/sp.tasks` command)
