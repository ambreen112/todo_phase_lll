---
description: "Task list for Phase 3 AI Chatbot Agent implementation"
---

# Tasks: Phase 3 AI Chatbot Agent

**Input**: Design documents from `/specs/agents/`
**Prerequisites**: plan.md, spec.md, todo-agent.spec.md, todo-agent.constitution.md, chat-api.spec.md, mcp/tools.md

**Tests**: Not requested in spec. Tests optional but recommended for validation.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **DB migrations**: `backend/alembic/versions/`
- **Tests**: `backend/tests/`, `frontend/tests/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Install OpenAI Agents SDK and dependencies in backend/requirements.txt
- [X] T002 Configure OpenRouter API key in backend/.env
- [X] T003 [P] Add conversation and message models to backend/src/models/conversation.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create Alembic migration for conversations table in backend/alembic/versions/003_add_conversations.py
- [X] T005 [P] Create Alembic migration for chat_messages table in backend/alembic/versions/003_add_conversations.py
- [ ] T006 Run alembic upgrade head to apply migrations
- [X] T007 Create MCP router skeleton in backend/src/api/routes/mcp.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Core Agent (Priority: P1) 🎯 MVP

**Goal**: Stateless OpenAI Agents SDK client that loads constitution + spec as system prompt

**Independent Test**: Can import and initialize client; system prompt loads from constitution + spec

### Implementation for User Story 1

- [X] T008 [P] [US1] Create OpenAI client config with OpenRouter in backend/src/agents/openai_client.py
- [X] T009 [P] [US1] Load constitution and spec as system prompt in backend/src/agents/system_prompt.py
- [X] T010 [US1] Register placeholder tool schemas in backend/src/agents/tool_registry.py
- [X] T011 [US1] Initialize agent with model claude-3.5-sonnet and max_turns=5

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - MCP Tools (Priority: P2)

**Goal**: 7 MCP endpoints (add_task, list_tasks, get_task, update_task, delete_task, restore_task, complete_task) per specs/mcp/tools.md

**Independent Test**: Each tool responds to curl POST with JSON; DB operations work

### Implementation for User Story 2

- [X] T012 [P] [US2] Implement add_task tool in backend/src/api/routes/mcp/add_task.py
- [X] T013 [P] [US2] Implement list_tasks tool in backend/src/api/routes/mcp/list_tasks.py
- [X] T014 [P] [US2] Implement get_task tool in backend/src/api/routes/mcp/get_task.py
- [X] T015 [P] [US2] Implement update_task tool in backend/src/api/routes/mcp/update_task.py
- [X] T016 [P] [US2] Implement delete_task (soft) tool in backend/src/api/routes/mcp/delete_task.py
- [X] T017 [P] [US2] Implement restore_task tool in backend/src/api/routes/mcp/restore_task.py
- [X] T018 [P] [US2] Implement complete_task (toggle) tool in backend/src/api/routes/mcp/complete_task.py
- [X] T019 [US2] Register all MCP tools with FastAPI router and auth middleware in backend/src/api/routes/mcp.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Chat API (Priority: P3)

**Goal**: POST /api/{user_id}/chat endpoint with conversation persistence

**Independent Test**: Endpoint returns agent_response with tool_calls log; DB persistence works

### Implementation for User Story 3

- [ ] T020 [P] [US3] Create conversation service in backend/src/services/conversation_service.py
- [ ] T021 [P] [US3] Implement POST chat endpoint in backend/src/api/routes/chat.py
- [ ] T022 [US3] Connect chat endpoint to OpenAI client with MCP tools in backend/src/api/routes/chat.py
- [ ] T023 [US3] Persist messages + tool calls to DB in backend/src/api/routes/chat.py
- [ ] T024 [US3] Add conversation_id handling (fetch/create) in backend/src/api/routes/chat.py

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should work independently

---

## Phase 6: User Story 4 - Frontend ChatKit (Priority: P4)

**Goal**: Chat UI in dashboard with localStorage for conversation_id

**Independent Test**: UI renders, sends/receives messages, integrates with /api/chat

### Implementation for User Story 4

- [ ] T025 [P] [US4] Install @vercel/chatkit or compatible in frontend/package.json
- [ ] T026 [P] [US4] Create Chat component in frontend/src/components/Chat.tsx
- [ ] T027 [P] [US4] Add Chat UI to dashboard/page.tsx
- [ ] T028 [US4] Integrate Chat component with auth token and /api/chat endpoint
- [ ] T029 [US4] Implement localStorage for conversation_id persistence

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T030 [P] Add error handling in all MCP tools
- [ ] T031 [P] Add validation on chat API input (message length, content)
- [ ] T032 [P] Write unit tests for MCP tools in backend/tests/test_mcp_tools.py
- [ ] T033 [P] Write integration test for chat flow in backend/tests/test_chat_api.py
- [ ] T034 Add logging for agent decisions + tool calls in backend/src/agents/logging.py
- [ ] T035 Add rate limiting to chat API (10 req/min per user)
- [ ] T036 Add statelessness validation test (parallel requests independent)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for tool schemas
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 + US2
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on US3

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- MCP tools (T012-T018) can all be built in parallel
- Frontend tasks (T025-T027) can run in parallel with backend
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 2 (MCP Tools)

```bash
# Launch all MCP tools in parallel:
Task: "Implement add_task tool in backend/src/api/routes/mcp/add_task.py"
Task: "Implement list_tasks tool in backend/src/api/routes/mcp/list_tasks.py"
Task: "Implement get_task tool in backend/src/api/routes/mcp/get_task.py"
Task: "Implement update_task tool in backend/src/api/routes/mcp/update_task.py"
Task: "Implement delete_task (soft) tool in backend/src/api/routes/mcp/delete_task.py"
Task: "Implement restore_task tool in backend/src/api/routes/mcp/restore_task.py"
Task: "Implement complete_task (toggle) tool in backend/src/api/routes/mcp/complete_task.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Core Agent)
4. Complete Phase 4: User Story 2 (MCP Tools)
5. **STOP and VALIDATE**: Test Agent + MCP tools work together
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Core Agent → Test independently
3. Add User Story 2 → MCP Tools → Test independently
4. Add User Story 3 → Chat API → Test independently
5. Add User Story 4 → Frontend ChatKit → Test independently
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Core Agent)
   - Developer B: User Story 2 (MCP Tools)
   - Developer C: User Story 3 (Chat API)
   - Developer D: User Story 4 (Frontend ChatKit)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

**Total task count**: 36 tasks
**Task count per user story**:
- US1: 4 tasks
- US2: 8 tasks
- US3: 5 tasks
- US4: 5 tasks
- Setup: 3 tasks
- Foundational: 4 tasks
- Polish: 7 tasks

**Parallel opportunities identified**:
- MCP tools (7 parallel)
- Frontend + backend development
- Setup tasks
- Foundational tasks
- Polish tasks

**Suggested MVP scope**: US1 + US2 (Core Agent + MCP Tools) provides working backend AI agent.