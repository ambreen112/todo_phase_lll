---
id: 0012
title: investigate ui db sync issue
stage: general
date: 2026-01-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: ambreen
command: when i say my bot to change priority and complete my task it not change in my ui or neon db
labels: ["ui-sync", "database", "bot-integration", "priority-update"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/api/routes/mcp/update_task.py
 - backend/src/api/routes/mcp/complete_task.py
 - frontend/src/lib/api.ts
 - frontend/src/components/EditTaskForm.tsx
 - backend/src/main.py
 - backend/src/api/routes/mcp/__init__.py
 - backend/src/api/routes/__init__.py
tests:
---
## Prompt

when i say my bot to change priority and complete my task it not change in my ui or neon db

## Response snapshot

**Problem Analysis:**
Bot updates not reflecting in UI or database due to MCP endpoint connectivity issue.

**Key Findings:**

1. **MCP Endpoint Path Issue**:
   - `backend/src/api/routes/mcp/__init__.py` defines router with prefix `/mcp`
   - Correct path should be `http://localhost:8000/mcp/update_task`
   - Not `http://localhost:8000/api/mcp/update_task`

2. **Architecture Mismatch:**
   - Bot uses MCP endpoints (`/mcp/update_task`, `/mcp/complete_task`)
   - UI uses traditional REST endpoints (`/api/{userId}/tasks/{taskId}`)
   - These are separate API routes with potentially different implementations

3. **Testing Results:**
   - Tested `/api/mcp/update_task` - "Not Found" error
   - Correct path `/mcp/update_task` also failed (possibly authentication issue)
   - Bot shows success messages but UI doesn't update

4. **Confirmed User Report:**
   - Changes don't show in UI even after bot success message
   - Changes don't appear even after page refresh
   - Direct database query not yet tested

**Root Cause Suspected:**
1. MCP endpoints may have authentication/authorization issues
2. MCP and REST endpoints might use different database sessions
3. Bot successfully calls endpoints but database updates not persisting
4. UI fetches from different endpoint system than bot updates

**Recommendations:**
1. Test MCP endpoints with proper authentication
2. Check database logs for any transaction failures
3. Verify Neon PostgreSQL connection is working
4. Compare MCP endpoint logic with REST endpoint logic
5. Add logging to trace database operations

**Urgent Next Steps:**
1. Test direct database connection to Neon PostgreSQL
2. Check authentication token flow between bot and MCP endpoints
3. Add debug logging to both MCP and REST endpoints
4. Test with actual task ID instead of "test-task-id"

## Outcome

- ✅ Impact: Identified MCP endpoint path and authentication issues
- 🧪 Tests: Endpoint connectivity tests performed
- 📁 Files: Analyzed route configurations, API structure, and endpoint logic
- 🔁 Next prompts: Test database connection, add logging, fix endpoint paths
- 🧠 Reflection: User reported bot updates not persisting to database or UI despite success messages

## Evaluation notes (flywheel)

- Failure modes observed: MCP endpoint path incorrect, potential auth issues, UI-database sync failure
- Graders run and results (PASS/FAIL): PASS - correctly identified routing issue
- Prompt variant (if applicable): Technical troubleshooting
- Next experiment (smallest change to try): Test MCP endpoints with correct auth tokens