---
id: 0004
title: Generate Phase3 AI Chatbot Tasks
stage: tasks
date: 2026-01-22
surface: agent
model: Sonnet 4.5
feature: phase3-todo-agent
branch: main
user: cli-user
command: /sp.tasks
labels: ["phase3", "tasks", "ai-agent", "mcp", "chatbot"]
links:
  spec: specs/agents/todo-agent.spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/agents/tasks.md
tests:
  - N/A

---

## Prompt

/sp.tasks

You are upgrading the project from Phase 2 (Web CRUD) to Phase 3 (AI Chatbot).

Context:
- Repo already contains Phase 2 Todo Web App (FastAPI + Next.js + Neon + Better Auth)
- Phase 3 introduces an AI chatbot using OpenAI Agents SDK (OpenRouter compatible)
- MCP (Model Context Protocol) MUST be used
- No manual coding — spec-driven only
- Backend remains stateless; all state is stored in the database
- OpenRouter API key will be used instead of OpenAI key

────────────────────────────────────────
STEP 1 — AGENT CONSTITUTION
────────────────────────────────────────
Create or update agent constitution with STRICT rules:

- Agent MUST be stateless
- Agent MUST NEVER access database, ORM, SQL, or REST directly
- Agent MUST ONLY interact with tasks via MCP tools
- Agent MUST NOT bypass MCP tools under any circumstance
- Agent MUST confirm every action in natural language
- Agent MUST gracefully handle errors (task not found, invalid input)
- Agent MUST support OpenAI Agents SDK with OpenRouter compatibility

Output:
specs/agents/todo-agent.constitution.md

────────────────────────────────────────
STEP 2 — AGENT SPECIFICATION
────────────────────────────────────────
Define detailed agent behavior and intent mapping.

Agent must support ALL task operations:
- List tasks with filters
- List deleted tasks
- Get single task
- Create task
- Update task
- Soft delete task
- Restore deleted task
- Toggle completion

Include:
- Intent → MCP tool mapping
- Natural language examples
- Confirmation responses
- Error scenarios
- Stateless conversation flow

Output:
specs/agents/todo-agent.spec.md

────────────────────────────────────────
STEP 3 — MCP TOOLS SPECIFICATION
────────────────────────────────────────
Define MCP tools (stateless, DB-backed):

Required tools:
- add_task
- list_tasks (filters + include_deleted)
- get_task
- update_task
- delete_task (soft delete only)
- restore_task
- complete_task (toggle)

For each tool include:
- Purpose
- Parameters (types + validation)
- DB behavior
- Example input/output

Output:
specs/mcp/tools.md

────────────────────────────────────────
STEP 4 — CHAT API SPECIFICATION
────────────────────────────────────────
Define Chat API using stateless request cycle.

Endpoint:
POST /api/{user_id}/chat

Include:
- Request/response schema
- Conversation persistence
- Message storage
- Agent execution flow
- Tool call logging
- Stateless guarantees

Output:
specs/agents/chat-api.spec.md

────────────────────────────────────────
STEP 5 — IMPLEMENTATION PLAN
────────────────────────────────────────
Generate a step-by-step implementation plan (NO CODE).

Must include:
- FastAPI chat endpoint
- OpenAI Agents SDK setup (OpenRouter)
- MCP server integration
- Tool registration
- Conversation persistence
- Frontend ChatKit integration
- Authentication handling
- Validation checkpoints

Output:
specs/agents/implementation-plan.md

────────────────────────────────────────
STEP 6 — TASK BREAKDOWN
────────────────────────────────────────
Break implementation into executable tasks.

Group tasks by:
1. Agent layer
2. MCP server
3. Database
4. Chat API
5. Frontend ChatKit
6. Testing & validation

Each task must include:
- Task ID
- Description
- Inputs
- Outputs
- Validation criteria

Output:
specs/agents/tasks.md

────────────────────────────────────────
IMPORTANT CONSTRAINTS
────────────────────────────────────────
- Do NOT write application code
- Do NOT implement UI or backend logic
- Specs must be Phase 3 complete and judge-ready
- OpenRouter must be treated as OpenAI-compatible

Begin Phase 3 specification update now.

## Response snapshot

Created Phase 3 spec documents:
- specs/agents/todo-agent.constitution.md
- specs/agents/todo-agent.spec.md
- specs/mcp/tools.md
- specs/agents/chat-api.spec.md
- specs/agents/implementation-plan.md

Generated tasks.md with 36 tasks organized by user story:
- Setup: 3 tasks
- Foundational: 4 tasks
- US1 (Core Agent): 4 tasks
- US2 (MCP Tools): 8 tasks (7 parallel)
- US3 (Chat API): 5 tasks
- US4 (Frontend ChatKit): 5 tasks
- Polish: 7 tasks

Total tasks: 36. All follow format: - [ ] TXXX [P?] [Story?] Description with file path.

Parallel opportunities: MCP tools (7 parallel), frontend+backend dev, setup/foundational tasks.

MVP scope: US1+US2 (Core Agent + MCP Tools) provides working backend AI agent.

Tasks.md includes dependencies, execution order, and implementation strategy.

## Outcome

- ✅ Impact: High - Comprehensive task breakdown for Phase 3 AI chatbot implementation
- 🧪 Tests: Not included (spec-driven only)
- 📁 Files: Updated specs/agents/tasks.md with 36 executable tasks
- 🔁 Next prompts: /sp.implement for execution
- 🧠 Reflection: Tasks follow proper template format, organized by user stories, include parallelization opportunities and clear dependencies.

## Evaluation notes (flywheel)

- Failure modes observed: Branch check failed (not on feature branch), ignored per instruction
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
