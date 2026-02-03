---
description: "Phase 2 Todo Web Application - Implementation task list"
---

# Tasks: Phase 2 Todo Web Application

**Input**: Design documents from `/specs/006-todo-web-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Include test tasks for critical paths - authentication, task CRUD, and ownership enforcement.

**Organization**: Tasks are grouped by phase and user story to enable independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create monorepo structure: /backend and /frontend directories
- [x] T002 Initialize backend Python project with pyproject.toml
- [x] T003 [P] Configure backend dependencies (FastAPI, SQLModel, Pydantic, uvicorn)
- [x] T004 [P] Configure backend dev dependencies (pytest, ruff, mypy, alembic)
- [x] T005 Initialize frontend Next.js 16+ project with TypeScript
- [x] T006 [P] Configure frontend dependencies (Better Auth, React Query, Tailwind)
- [x] T007 [P] Configure frontend dev dependencies (Jest, ESLint, Prettier)
- [x] T008 Create .env.example with all required environment variables
- [x] T009 Create .gitignore for monorepo (Python + Node.js patterns)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 [P] [Foundation] Create backend project structure (src/models, src/api, src/core)
- [x] T011 [P] [Foundation] Create SQLModel entities (User, Task) in backend/src/models/
- [x] T012 [P] [Foundation] Create database configuration in backend/src/core/config.py
- [x] T013 [Foundation] Set up Alembic migrations framework
- [x] T014 [Foundation] Create initial migration for User and Task tables
- [x] T015 [Foundation] Implement JWT verification dependency in backend/src/api/deps.py
- [x] T016 [Foundation] Create authentication error responses in backend/src/core/security.py
- [x] T017 [Foundation] Set up FastAPI application with CORS middleware
- [x] T018 [Foundation] Create frontend project structure (app, components, lib, types)
- [x] T019 [Foundation] Configure Better Auth in frontend (custom auth context)
- [x] T020 [Foundation] Create typed API client utility in frontend/src/lib/api.ts
- [x] T021 [Foundation] Set up React Query provider and auth context

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Account Creation and Authentication (Priority: P1) 🎯 MVP

**Goal**: Users can create accounts and authenticate to receive JWT tokens

**Independent Test**: A user can complete signup, login, and access authenticated routes

### Backend Implementation

- [x] T022 [US1] Implement password hashing utility in backend/src/core/security.py
- [x] T023 [US1] Create User model in backend/src/models/user.py
- [x] T024 [US1] Create signup endpoint POST /auth/signup in backend/src/api/routes/auth.py
- [x] T025 [US1] Create login endpoint POST /auth/login in backend/src/api/routes/auth.py
- [x] T026 [US1] Implement JWT token generation in security.py
- [x] T027 [US1] Add email uniqueness validation
- [x] T028 [US1] Add request validation (email format, password length)

### Frontend Implementation

- [x] T029 [US1] Create signup page at frontend/src/app/(auth)/signup/page.tsx
- [x] T030 [US1] Create login page at frontend/src/app/(auth)/login/page.tsx
- [x] T031 [US1] Configure Better Auth signUp and signIn methods (custom auth context)
- [x] T032 [US1] Create auth form components (Input, Button)
- [x] T033 [US1] Implement form validation with error display
- [x] T034 [US1] Create auth middleware for route protection

**Checkpoint**: Authentication flow complete - users can sign up, log in, and access protected routes

---

## Phase 4: User Story 2 - Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks with title and optional description

**Independent Test**: An authenticated user can create a task and see it in their list

### Backend Implementation

- [x] T035 [US2] Create Task model in backend/src/models/task.py
- [x] T036 [US2] Create TaskCreate schema in backend/src/models/schemas.py
- [x] T037 [US2] Implement POST /api/{user_id}/tasks endpoint
- [x] T038 [US2] Add task validation (title required, max 256 chars; description max 2000)
- [x] T039 [US2] Implement task ownership assignment from JWT user_id

### Frontend Implementation

- [x] T040 [US2] Create Task type definitions in frontend/src/types/index.ts
- [x] T041 [US2] Create task creation API call in frontend/src/lib/api.ts
- [x] T042 [US2] Create CreateTaskForm component
- [x] T043 [US2] Add create task functionality to dashboard

**Checkpoint**: Tasks can be created by authenticated users

---

## Phase 5: User Story 3 - Task List Viewing (Priority: P1) 🎯 MVP

**Goal**: Users can view all their tasks in a list

**Independent Test**: An authenticated user sees their complete task list on the dashboard

### Backend Implementation

- [x] T044 [US3] Create TaskListResponse schema in backend/src/models/schemas.py
- [x] T045 [US3] Implement GET /api/{user_id}/tasks endpoint with ownership filter
- [x] T046 [US3] Add response pagination (optional, for scalability)

### Frontend Implementation

- [x] T047 [US3] Create TaskList component
- [x] T048 [US3] Create TaskItem component
- [x] T049 [US3] Fetch and display tasks on dashboard
- [x] T050 [US3] Implement loading and empty states

**Checkpoint**: Users can view their task list on the dashboard

---

## Phase 6: User Story 4 - Task Completion Toggle (Priority: P1) 🎯 MVP

**Goal**: Users can mark tasks as complete or incomplete

**Independent Test**: Clicking completion checkbox updates task status and persists

### Backend Implementation

- [x] T051 [US4] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint
- [x] T052 [US4] Add ownership verification to complete endpoint

### Frontend Implementation

- [x] T053 [US4] Add completion toggle to TaskItem component
- [x] T054 [US4] Implement optimistic update for completion toggle
- [x] T055 [US4] Create API call for completion toggle

**Checkpoint**: Users can toggle task completion status

---

## Phase 7: User Story 5 - Task Editing (Priority: P2)

**Goal**: Users can edit task title and description

**Independent Test**: User can modify a task and changes persist

### Backend Implementation

- [x] T056 [US5] Create TaskUpdate schema in backend/src/models/schemas.py
- [x] T057 [US5] Implement PUT /api/{user_id}/tasks/{id} endpoint
- [x] T058 [US5] Add validation (title not empty if provided)

### Frontend Implementation

- [x] T059 [US5] Create EditTaskForm component (edit mode on TaskItem)
- [x] T060 [US5] Add edit mode to TaskItem
- [x] T061 [US5] Create API call for task update

**Checkpoint**: Users can edit existing tasks

---

## Phase 8: User Story 6 - Task Deletion (Priority: P2)

**Goal**: Users can delete tasks

**Independent Test**: User can delete a task and it no longer appears in the list

### Backend Implementation

- [x] T062 [US6] Implement DELETE /api/{user_id}/tasks/{id} endpoint
- [x] T063 [US6] Add soft-delete or hard-delete as per spec (hard-delete for Phase 2)

### Frontend Implementation

- [x] T064 [US6] Add delete button to TaskItem
- [x] T065 [US6] Create delete confirmation dialog
- [x] T066 [US6] Create API call for task deletion

**Checkpoint**: Users can delete tasks

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T067 [P] Write backend unit tests for User and Task models
- [ ] T068 [P] Write backend unit tests for security/password hashing
- [ ] T069 [P] Write API endpoint tests (authentication, task CRUD)
- [ ] T070 [P] Write frontend unit tests for auth context
- [ ] T071 [P] Write frontend unit tests for TaskItem component
- [ ] T072 Add error handling for network failures (frontend)
- [ ] T073 Add loading skeletons for better UX
- [ ] T074 Verify JWT ownership enforcement on all endpoints
- [ ] T075 Run type checking (mypy backend, tsc frontend)
- [ ] T076 Run linting (ruff backend, ESLint frontend)
- [ ] T077 Update README with setup instructions
- [ ] T078 Validate quickstart.md setup works end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - P1 stories (US1-US4) should be completed for MVP
  - P2 stories (US5-US6) can follow
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (Auth)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (Create)**: Depends on US1 (authentication required)
- **User Story 3 (List)**: Depends on US1 (authentication required)
- **User Story 4 (Toggle)**: Depends on US1 and US3 (auth + list view)
- **User Story 5 (Edit)**: Depends on US1 and US3
- **User Story 6 (Delete)**: Depends on US1 and US3

### Within Each User Story

- Backend models before API endpoints
- API endpoints before frontend components
- Components before integration tests

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- Backend and frontend foundational tasks can run in parallel
- All P1 user stories can run in parallel once foundational is done
- Unit tests within a story marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (Task Creation)
5. Complete Phase 5: User Story 3 (Task List)
6. Complete Phase 6: User Story 4 (Completion Toggle)
7. **STOP and VALIDATE**: Test authentication and task CRUD flow
8. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo
4. Continue with remaining stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- JWT authentication is enforced on ALL task endpoints
- Task ownership must be verified on every request
