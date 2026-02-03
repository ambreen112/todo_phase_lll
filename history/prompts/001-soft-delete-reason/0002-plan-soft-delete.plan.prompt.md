---
id: 0002
title: plan-soft-delete
stage: plan
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5
feature: 001-soft-delete-reason
branch: 001-soft-delete-reason
user: user
command: /sp.plan
labels: ["plan", "soft-delete", "architecture"]
links:
  spec: specs/001-soft-delete-reason/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-soft-delete-reason/plan.md
tests:
  - Constitution check passed
  - Technical context defined
  - Design decisions documented
---

## Prompt

Create a technical plan to implement delete reason support
using soft delete without breaking existing commands.

## Response snapshot

Created implementation plan for soft delete with reason tracking:

**Technical Context**:
- Python 3.13+, in-memory storage, pytest testing
- <100ms performance target
- Backward compatibility constraint

**8 Design Decisions**:
1. Data Model: Add optional `deletion_metadata` dict to Todo
2. Storage: Filter deleted items in `get_all_todos()`, add `get_deleted_todos()`
3. Breaking Change: `delete <id>` → `delete <id> <reason>`
4. Naming: Use kebab-case (`list-deleted`, `restore`)
5. Restore: Clear `deletion_metadata` to None
6. Error Handling: Return False, let agents format messages
7. Validation: 500 char limit in DeleteCompleteAgent
8. Compatibility: Only delete tests need updates

**Files to Modify**:
- src/models/todo.py
- src/skills/storage_skill.py
- src/agents/delete_complete_agent.py
- src/agents/list_search_agent.py
- src/agents/main_agent.py
- src/skills/formatter_skill.py (optional)

## Outcome

- ✅ Impact: Complete technical architecture plan for soft delete feature
- 🧪 Tests: Constitution check passed, all decisions documented
- 📁 Files: Created plan.md with Phase 0 & Phase 1 artifacts
- 🔁 Next prompts: /sp.tasks
- 🧠 Reflection: Plan maintains backward compatibility except intentional delete change. Ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All PASS
- Prompt variant: N/A
- Next experiment: N/A
