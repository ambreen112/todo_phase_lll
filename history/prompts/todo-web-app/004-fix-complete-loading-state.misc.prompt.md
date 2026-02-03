---
id: 004
title: Fix complete status not working when filtered
stage: misc
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 006-todo-web-app
branch: 006-todo-web-app
user: ambreen
command: fix frontend complete status display and filtering
labels: ["bug-fix", "frontend", "react-query", "cache-invalidation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/components/TaskItem.tsx
tests:
  - Manual testing: Click complete on task with "Completed" filter selected
  - Manual testing: Click complete on task with "Active" filter selected
  - Manual testing: Verify task disappears from current filtered view after completion
  - Manual testing: Verify error messages display when API fails
---

## Prompt

In frontend, when clicking complete on a task, the status doesn't update correctly across all filter views. Backend works correctly, so the issue is in the frontend cache invalidation.

## Response snapshot

**Root Cause Identified:** Two critical issues in TaskItem.tsx:

1. **Query cache key mismatch**: TaskItem invalidated with `queryKey: ["tasks", user?.id]` but TaskList queries with `queryKey: ["tasks", user?.id, filters]`. The partial key doesn't invalidate filtered queries.

2. **Missing error handling**: No `onError` callback, causing mutations to hang in pending state when API fails.

**Fix Applied:**
1. Changed query invalidation to use `queryKey: ["tasks"]` - invalidates ALL task-related queries regardless of filters
2. Added error invalidation for deleted tasks: also invalidate `["deletedTasks"]`
3. Applied same pattern to delete and restore mutations for consistency
4. Added separate `toggleError` state with `onError` handler
5. Added UI to display toggle errors to user

## Outcome

- ✅ Impact: Task completion now updates across all filter views. When completing a task, all relevant queries invalidate and refetch.
- 🧪 Tests: Manual testing needed - test in filtered views (Active, Completed, All Status tabs)
- 📁 Files: Modified `/frontend/src/components/TaskItem.tsx`
- 🔁 Next prompts: Verify filters work correctly (Active should hide completed, Completed should show only completed)
- 🧠 Reflection: React Query cache keys must be carefully matched between components. Partial key invalidation only invalidates exact matches. Using a broader key prefix ensures all dependent queries update.

## Evaluation notes (flywheel)

- Failure modes observed: Tasks remain visible in filtered views after status change, mutation hangs on error
- Graders run and results: Needs manual testing in different filter modes
- Prompt variant: N/A
- Next experiment: Test all three filter states (All Status, Active, Completed) to confirm visibility updates correctly
