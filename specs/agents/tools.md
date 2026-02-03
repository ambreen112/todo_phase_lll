# Phase 2 Todo Agent — Tool Usage Rules

## Purpose

Define how the Phase 2 Todo Agent MUST use **conceptual tools** to interact with
backend task resources in a stateless, multi-user web application.

This document is specification-only. It does not define an MCP server or
implementation.

## Operating Context

- **App type**: Multi-user web application
- **Backend**: FastAPI REST APIs
- **Auth**: JWT
- **Stateless**: Each request is handled independently
- **Separation of concerns**:
  - Agent does **not** directly access the database
  - Agent does **not** directly manipulate the UI
  - Agent performs task operations **only** through tools

## Available Tools (Conceptual)

| Tool | Description | Typical Inputs | Output (conceptual) |
|------|-------------|----------------|---------------------|
| `create_task` | Create a new task | `title` (required), `description?`, `priority?`, `tags?`, `due_date?`, `recurrence?` | Created task object |
| `list_tasks` | List tasks owned by user | filters (optional): `completed?`, `deleted?`, `priority?`, `tag?`, `due_before?`, `overdue?` | Array of tasks |
| `get_task` | Fetch one task | `task_id` | Task object or not found |
| `update_task` | Update fields for one task | `task_id`, patch fields | Updated task object or errors |
| `toggle_task_completion` | Toggle completion | `task_id` | Updated task object or errors |
| `soft_delete_task` | Soft delete a task | `task_id` | Deleted task object or errors |
| `restore_task` | Restore a soft-deleted task | `task_id` | Restored task object or errors |

## Tool Usage Rules (Hard Requirements)

### 1) Every operation MUST be executed via a tool

- The agent MUST NOT claim a task was created/updated/deleted/restored/completed
  unless the corresponding tool confirms success.
- The agent MUST NOT “simulate” state changes in text.

### 2) User scoping is implicit and mandatory

- Tools MUST implicitly scope all data access by **authenticated `user_id`
  derived from JWT**.
- The agent MUST NEVER accept a user-provided `user_id` as authority.

### 3) No invented identifiers or assumed existence

- The agent MUST NOT invent task IDs.
- The agent MUST NOT assume a task exists.
- If the user references a task ambiguously, the agent MUST gather enough info
  to identify the task before calling a destructive/modifying tool.

### 4) Fetch-before-modify when ambiguous

The agent MUST call `get_task` or `list_tasks` before **update/delete/restore/toggle** when:
- The user does not provide a `task_id`.
- The description matches multiple tasks.
- The agent is unsure which task the user means.

### 5) Destructive actions require confirmation when selection is unclear

- If more than one task could match “delete X”, the agent MUST ask the user to
  choose.
- The agent MUST NOT auto-select “the closest match” for destructive actions.

### 6) No automatic retries for destructive actions

- The agent MUST NOT automatically retry `soft_delete_task` or `restore_task`.
- For transient failures, the agent MAY suggest the user retry, but must not
  re-issue the tool call without explicit user intent.

## Natural Language → Tool Mapping

| User intent (examples) | Tool | Notes |
|---|---|---|
| “add”, “create”, “remember” | `create_task` | Validate title required before calling tool |
| “show”, “list”, “see my tasks” | `list_tasks` | Apply filters if user asked (completed/overdue/tag/etc.) |
| “details”, “open”, “view task” | `get_task` | Prefer when user provides an ID |
| “update”, “change”, “rename”, “edit” | `update_task` | Use patch semantics; update only requested fields |
| “complete”, “done”, “finished”, “mark incomplete” | `toggle_task_completion` | If the tool toggles only, confirm current state if needed |
| “delete”, “remove” | `soft_delete_task` | Must be soft delete only; confirm selection if ambiguous |
| “restore”, “undo delete” | `restore_task` | If user unsure what was deleted, list deleted tasks first |

## Error Handling Policy

### Tool returns `not found`

- The agent MUST explain that the task could not be found (or is not accessible
  in the current account).
- The agent MUST NOT reveal whether the task exists for another user.
- The agent SHOULD suggest next steps (e.g., “list your tasks” or “check the ID”).

### Tool returns validation errors

- The agent MUST translate errors into user-friendly messages.
- The agent MUST ask for corrected inputs.

### Tool returns multiple matches (if applicable)

- The agent MUST present a disambiguation question with enough identifying info
  (e.g., titles + due dates) and ask the user to choose.

## Stateless Conversation Pattern

- If a user says “mark it done” without a task reference, the agent MUST ask
  which task they mean (or list recently viewed tasks if the UI provides that
  context explicitly in the request).

## Non-Goals

- Defining actual MCP tool schemas or implementation details.
- Defining database queries, UI flows, or backend endpoints.

## Acceptance Checks

- [ ] All task operations are performed via tools.
- [ ] No task IDs are fabricated; no task existence is assumed.
- [ ] Tools implicitly scope by JWT-derived `user_id`.
- [ ] Agent fetches (`get_task`/`list_tasks`) before modify/delete when ambiguous.
- [ ] Destructive actions are not retried automatically.
