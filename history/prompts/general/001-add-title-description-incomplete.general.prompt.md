---
id: 001
title: Add Title/Description and Incomplete Command
stage: green
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: ambreen
command: Working console application demonstrating: Adding tasks with title and description; Listing all tasks with status indicators; Updating task details; Deleting tasks by ID; Marking tasks as complete/incomplete; ye tamam cheezy meri todo me hai check kr k batao
labels: ["feature-enhancement","title-description","incomplete-command"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - src/models/todo.py
 - src/agents/add_update_agent.py
 - src/agents/delete_complete_agent.py
 - src/agents/main_agent.py
 - src/skills/formatter_skill.py
tests:
 - Manual test via CLI: add/list/complete/incomplete/update/delete workflow
---
## Prompt

Working console application demonstrating:
Adding tasks with title and description
Listing all tasks with status indicators
Updating task details
Deleting tasks by ID
Marking tasks as complete/incomplete
ye tamam cheezy meri todo me hai check kr k batao

User confirmed to implement: yes

User preferences confirmed via AskUserQuestion:
- Add command syntax: `add <title> --description <desc>`
- Incomplete command name: `incomplete`

## Response snapshot

Analyzed existing todo app codebase and identified feature coverage:

**Features present:**
- Adding tasks (single `task` field only - no separate title/description)
- Listing with status indicators (ID, Task, Status columns)
- Updating task details
- Deleting by ID with reason
- Marking complete

**Missing:**
- Separate title + description fields
- Mark as incomplete command

Implemented both features following existing architectural patterns:
1. Added `title` and `description` fields to Todo model with backward compatibility
2. Updated add command to parse `--description` flag
3. Added `incomplete_todo()` method to DeleteCompleteAgent
4. Added `incomplete` command to MainAgent
5. Updated formatter to display Title + Description + Status columns

Tested successfully with:
```
add Buy groceries --description Milk, eggs, and bread
add Finish project report --description Complete -> Q4 analysis
add Call mom
list
complete 1
incomplete 1
update 2 Call dad
delete 3 Not important
list-deleted
```

## Outcome

- ✅ Impact: Enhanced todo app with full feature parity - now supports title/description separation and complete/incomplete toggle
- 🧪 Tests: Manual CLI test passed - all commands working correctly
- 📁 Files: 5 files modified (model, 3 agents, 1 skill)
- 🔁 Next prompts: None - implementation complete
- 🧠 Reflection: Maintained existing architecture patterns (dependency injection, skill-based composition, agent hierarchy). Backward compatibility preserved for existing todo objects that only have `task` field.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS (manual testing)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): None needed
