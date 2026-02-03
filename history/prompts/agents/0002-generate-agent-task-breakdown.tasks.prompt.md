---
id: 0002
title: Generate Agent Task Breakdown
stage: tasks
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: agents
branch: main
user: user
command: /sp.implementation @specs/agents/planning.md @specs/006-todo-web-app/spec-updated.md
labels: [agents, tasks, todo, phase2]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/agents/tasks.md
tests:
 - null
---

## Prompt

```text
/sp.implementation
@specs/agents/planning.md
@specs/006-todo-web-app/spec-updated.md
```

## Response snapshot

Generated an agent-focused `specs/agents/tasks.md` (spec-only) describing the
implementation task breakdown for the Phase 2 Todo Agent’s behavior and tool-
driven orchestration, based on:
- `specs/agents/planning.md`
- `specs/agents/tools.md`
- `specs/agents/todo-agent.md`
- `specs/006-todo-web-app/spec-updated.md` (parity constraints)

The tasks are organized by phases (setup/contracts/tool patterns/disambiguation/
parity alignment/polish) and include explicit file paths for where each doc-level
change should land.

## Outcome

- ✅ Impact: Created a dependency-ordered task list to drive agent behavior
  specification to completion.
- 🧪 Tests: None (spec-only)
- 📁 Files: Added `specs/agents/tasks.md`
- 🔁 Next prompts: Optionally run `/sp.tasks` for the 006 web-app feature if you
  also want updated implementation tasks for backend/frontend parity.
- 🧠 Reflection: Keeping agent tasks doc-only avoids premature MCP/tool schema
  commitments while still making behavior testable.

## Evaluation notes (flywheel)

- Failure modes observed: `create-phr.sh` failed due to template path lookup;
  wrote PHR via agent-native template.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Fix `.specify/scripts/bash/create-phr.sh`
  to locate `.specify/templates/phr-template.prompt.md`.
