---
id: "004"
title: "Fix search input unresponsive during typing"
stage: "misc"
date: "2026-01-13"
surface: "agent"
model: "sonnet-4-5-20250929"
feature: "none"
branch: "006-todo-web-app"
user: "user"
command: "Bug report: Search tasks input becomes unresponsive when typing"
labels: "bugfix,frontend,react-query"
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "/mnt/d/phase2_todo/phase1_todo/frontend/src/components/TaskList.tsx"
tests:
  - "none"
---

## Prompt

The user reported a bug: "Whenever I try to type something in the 'Search tasks' field, the input becomes unresponsive. I cannot type anything and the UI immediately goes into a loading state."

## Response snapshot

Identified root cause: React Query's `isLoading` state triggered an early return that unmounted the search input on every keystroke. Fixed by:
1. Adding `placeholderData` to keep previous data during background fetches
2. Changing loading check from `isLoading` to `isInitialLoad` (isLoading && !data)
3. Moving loading state to a conditional banner instead of early return

## Outcome

- ✅ Impact: Search input now remains responsive while typing; tasks refresh in background
- 🧪 Tests: none
- 📁 Files: frontend/src/components/TaskList.tsx (modified)
- 🔁 Next prompts: none
- 🧠 Reflection: Early returns during async loading can break controlled inputs. Use placeholderData and separate initial-load state from background-refetch state.

## Evaluation notes (flywheel)

- Failure modes observed: Input unmounting on state change prevented text input
- Graders run and results (PASS/FAIL): Manual test - typing now works
- Prompt variant (if applicable): "none"
- Next experiment (smallest change to try): Add debouncing to search input to reduce API calls
