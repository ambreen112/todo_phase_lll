---
id: 0008
title: disable-mock-mode
stage: misc
date: 2026-01-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-web-app
branch: 006-todo-web-app
user: user
command: task
labels: ["frontend", "config", "backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/src/lib/api.ts
tests:
 - none
---

## Prompt

ui bany k bd mera data neon database me nai gaya

## Response snapshot

Disabled mock mode in frontend API client to allow connection to real backend (Neon DB).

## Outcome

- ✅ Impact: Frontend defaults to real API
- 🧪 Tests: none
- 📁 Files: Modified api.ts
- 🔁 Next prompts: none
- 🧠 Reflection: User provided feedback that data wasn't persisting, which was caused by the demo mock mode.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
