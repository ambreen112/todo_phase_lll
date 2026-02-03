---
id: 6
title: Define Todo Agent Tools Rules
stage: general
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.tools @specs/agents/tools.md
labels: [agents, tools, todo, phase2, spec]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/agents/tools.md
tests:
 - null
---

## Prompt

```text
/sp.tools /sp.tools @specs/agents/tools.md

Purpose:
Define Phase 2 Todo Agent tool usage rules for a web application.

Context:
- Phase 2 is a multi-user web app
- Backend exposes REST APIs via FastAPI
- Authentication is handled via JWT
- Each request is stateless
- Agent does not directly access database or UI

Available Tools (Conceptual):
- create_task
- list_tasks
- get_task
- update_task
- toggle_task_completion
- soft_delete_task
- restore_task

Tool Usage Rules:
- Every task operation MUST be executed via a tool
- Tools implicitly scope data by authenticated user_id
- Agent must never invent task IDs
- Agent must never assume task existence
- Agent must fetch before modifying or deleting when ambiguous

Natural Language → Tool Mapping:
- "add / create / remember" → create_task
- "show / list / see" → list_tasks
- "update / change / rename" → update_task
- "complete / done / finished" → toggle_task_completion
- "delete / remove" → soft_delete_task
- "restore / undo delete" → restore_task

Error Handling:
- If tool returns "not found", explain clearly to user
- If multiple matches exist, ask user to clarify
- Never retry a destructive action automatically

Constraints:
- Specification only
- No application code
- No MCP server yet (Phase 3 responsibility)

Output:
- Structured markdown tables
- Clear mapping and rules

Write to:
specs/agents/tools.md
```

## Response snapshot

Created `specs/agents/tools.md` defining conceptual tools, hard tool-usage rules,
NL→tool mapping, and error handling policies for a stateless, JWT-scoped,
multi-user Phase 2 todo web application.

## Outcome

- ✅ Impact: Established tool usage governance to ensure all task operations are
  executed through scoped tools and never rely on fabricated IDs or assumed state.
- 🧪 Tests: None (spec-only)
- 📁 Files: Added `specs/agents/tools.md`
- 🔁 Next prompts: Implement MCP tool definitions in Phase 3 (out of scope here)
- 🧠 Reflection: Fetch-before-modify and no-auto-retry reduce ambiguity and prevent
  unintended destructive actions.

## Evaluation notes (flywheel)

- Failure modes observed: `create-phr.sh` failed due to template path lookup; used
  agent-native template instead.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Fix `create-phr.sh` to locate
  `.specify/templates/phr-template.prompt.md`.
