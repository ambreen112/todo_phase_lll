---
id: 3
title: Define Phase2 Todo Agent Constitution
stage: constitution
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution @specs/agents/todo-agent.md
labels: [constitution, agents, todo, phase2, web]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/agents/todo-agent.md
tests:
 - null
---

## Prompt

```text
/sp.constitution @specs/agents/todo-agent.md

Purpose:
Define the Phase 2 Todo Agent constitution by upgrading the Phase 1 CLI agent.

Context:
- Phase 1 agent worked with a CLI todo app
- Phase 2 is a full-stack web application
- Backend: FastAPI + SQLModel
- Frontend: Next.js
- Authentication: Better Auth with JWT
- Each request is stateless
- Each action is scoped to an authenticated user

Agent Responsibilities:
- Interpret user intent related to todo management
- Operate only on tasks owned by the authenticated user
- Support the following capabilities:
  - Create tasks
  - List tasks
  - Update tasks
  - Toggle completion
  - Soft delete and restore tasks
  - Handle priorities (high/medium/low)
  - Handle tags/categories
  - Handle due dates and overdue detection
  - Handle recurring tasks conceptually (no scheduling logic)

Behavior Rules:
- Always act as a web-based assistant (not CLI)
- Never assume application state
- Never fabricate task data
- Respect validation rules from specs
- Provide clear and friendly confirmations after actions
- Ask for clarification if user intent is ambiguous

Security Rules:
- All actions are scoped by user_id derived from JWT
- Never access or modify another user’s tasks
- Never operate without authentication context

Constraints:
- This is a specification-only document
- Do NOT write application code
- Do NOT define MCP tools yet
- Output must be clean, structured markdown

Write the complete agent constitution to:
specs/agents/todo-agent.md
```

## Response snapshot

Created a specification-only constitution for the Phase 2 Todo Agent at
`specs/agents/todo-agent.md`, defining:
- Web-first assistant behavior (not CLI)
- Stateless request handling
- Non-fabrication/truthfulness rules
- Spec/validation compliance requirements
- JWT-derived user scoping and ownership enforcement
- Supported capabilities (CRUD, completion toggle, soft delete/restore, priority,
  tags/categories, due dates/overdue, conceptual recurrence)
- Non-goals (no scheduling/reminders, no cross-user collaboration)

## Outcome

- ✅ Impact: Established Phase 2 agent governance for secure, user-scoped todo
  management in a stateless web app context.
- 🧪 Tests: No tests required for specification document.
- 📁 Files: Added `specs/agents/todo-agent.md` and recorded this prompt in a
  constitution PHR.
- 🔁 Next prompts: If desired, align the app’s API/UI behavior and validation
  rules with this constitution.
- 🧠 Reflection: Explicit scoping and non-enumeration rules reduce privacy and
  multi-tenant risk.

## Evaluation notes (flywheel)

- Failure modes observed: PHR creation script failed (template path lookup), so
  PHR was created via agent-native template.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Ensure `.specify/scripts/bash/create-phr.sh`
  resolves `.specify/templates/phr-template.prompt.md` correctly.
