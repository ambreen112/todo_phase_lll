---
id: 0004
title: Fix missing authorization header error
stage: misc
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-web-app
branch: 006-todo-web-app
user: HAJI LAPTOP KARACHI
command: none
labels: [auth, debugging, fix]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/src/lib/api.ts
 - frontend/src/app/(dashboard)/dashboard/page.tsx
 - frontend/src/components/TaskList.tsx
 - frontend/src/components/CreateTaskForm.tsx
tests:
 - manual
---

## Prompt

detail": "Missing authorization header ye kya hai

## Response snapshot

I investigated the "Missing authorization header" error and found it was caused by a race condition where the frontend made API requests before the authentication token was initialized in the ApiClient singleton. I updated the ApiClient interceptor, DashboardPage, and Task components to correctly respect the authentication loading state, ensuring requests only fire once the token is ready.

## Outcome

- ✅ Impact: Resolved a frequent authentication error on page refresh and initial load.
- 🧪 Tests: Manually verified state handling logic and added development logging.
- 📁 Files: Updated 4 frontend files to handle auth loading state.
- 🔁 Next prompts: none
- 🧠 Reflection: Race conditions between auth initialization and component mounting are common in SPA/Next.js apps using side-effect based auth initialization. Explicitly waiting for `isLoading` is the correct pattern.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
