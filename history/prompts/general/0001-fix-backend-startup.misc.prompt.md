---
id: 0001
title: Fix backend startup MCP import errors
stage: misc
date: 2026-01-24
surface: agent
model: sonnet-4.5
feature: backend
branch: main
user: human
command: fix server startup
labels: [\"backend\",\"mcp\",\"imports\",\"alembic\",\"neon\"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/api/routes/mcp/__init__.py (created)
  - backend/src/api/routes/mcp/*.py (imports/types fixed)
  - backend/.env (space removed)
  - backend/alembic.ini (PG URL)
tests:
  - None
---
## Prompt

User error log with ModuleNotFoundError for mcp.add_task, then get_current_user, get_db issues.

## Response snapshot

Fixed MCP package structure, imports (deps.py, get_session, TokenData), .env space, alembic.ini PG.

Server now starts on http://127.0.0.1:8000.

## Outcome
- ✅ Impact: Backend startup fixed, MCP tools ready
- 🧪 Tests: Manual uvicorn startup
- 📁 Files: 10+ MCP files edited, alembic.ini updated
- 🔁 Next prompts: Frontend dev, integration tests
- 🧠 Reflection: Relative imports fragile; use absolute or tools.py

## Evaluation notes (flywheel)
- Failure modes observed: Package vs module conflict, relative imports, .env parsing, hardcoded DB URL
- Graders run and results (PASS/FAIL): PASS (server starts)
- Prompt variant (if applicable): null
- Next experiment: Add MCP integration tests
