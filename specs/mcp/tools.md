# MCP Tools Specification

## Overview
MCP (Model Context Protocol) tools provide stateless, database-backed operations for the Todo AI Agent. All tools are implemented as FastAPI endpoints or functions that interact with the PostgreSQL database via SQLAlchemy ORM. Tools return JSON responses with success/error status.

**Stateless Guarantee**: Each tool call is independent; no session state required. User ID passed in every call for scoping.

**Common Parameters** (all tools):
- `user_id: str` - Owner of tasks (from auth).
- Error response: `{\"success\": false, \"error\": \"message\"}`

## Tool Definitions

### 1. `add_task`
**Purpose**: Create a new task for the user.

**Parameters**:
- `title: str` (required, max 200 chars)
- `description: str` (optional, max 1000 chars)
- `priority: str` (optional, enum: 'low'|'medium'|'high', default 'medium')
- `due_date: str|None` (optional, ISO date YYYY-MM-DD)

**Validation**: Title non-empty, valid date if provided.

**DB Behavior**: INSERT into `tasks` table with `user_id`, `is_deleted=false`, `is_completed=false`.

**Example**:
Input: `{\"user_id\": \"abc123\", \"title\": \"Buy milk\", \"priority\": \"high\", \"due_date\": \"2024-01-23\"}`
Output: `{\"success\": true, \"task_id\": \"456\", \"task\": {\"id\": \"456\", \"title\": \"Buy milk\", ...}}`

### 2. `list_tasks`
**Purpose**: List user's tasks with optional filters.

**Parameters**:
- `filters: dict` (optional):
  - `status: str` ('active'|'completed'|'deleted')
  - `include_deleted: bool` (default false)
  - `priority: str` ('low'|'medium'|'high')
  - `search: str` (title/desc fuzzy match)
  - `due_before: str` (ISO date)
  - `due_after: str` (ISO date)
  - `limit: int` (default 50)
  - `offset: int` (default 0)

**Validation**: Valid filter values.

**DB Behavior**: SELECT with WHERE `user_id` AND filters (e.g., `is_deleted=true` for deleted).

**Example**:
Input: `{\"user_id\": \"abc123\", \"filters\": {\"status\": \"completed\"}}`
Output: `{\"success\": true, \"tasks\": [{\"id\": \"123\", \"title\": \"Done\", ...}, ...], \"total\": 5}`

### 3. `get_task`
**Purpose**: Retrieve single task by ID.

**Parameters**:
- `task_id: str` (required)

**Validation**: UUID format.

**DB Behavior**: SELECT WHERE `id=task_id` AND `user_id`.

**Example**:
Input: `{\"user_id\": \"abc123\", \"task_id\": \"123\"}`
Output: `{\"success\": true, \"task\": {\"id\": \"123\", \"title\": \"Buy milk\", ...}}`
Error: `{\"success\": false, \"error\": \"Task 123 not found\"}`

### 4. `update_task`
**Purpose**: Patch update task fields.

**Parameters**:
- `task_id: str` (required)
- `title: str|None`
- `description: str|None`
- `priority: str|None`
- `due_date: str|None`
- `is_completed: bool|None`

**Validation**: At least one field; task exists.

**DB Behavior**: UPDATE SET provided fields WHERE `id` AND `user_id`.

**Example**:
Input: `{\"user_id\": \"abc123\", \"task_id\": \"123\", \"title\": \"Buy bread\"}`
Output: `{\"success\": true, \"task\": {... updated ...}}`

### 5. `delete_task`
**Purpose**: Soft delete task (set `is_deleted=true`).

**Parameters**:
- `task_id: str` (required)

**Validation**: Task exists and not already deleted.

**DB Behavior**: UPDATE `is_deleted=true` WHERE `id` AND `user_id`.

**Example**:
Input: `{\"user_id\": \"abc123\", \"task_id\": \"123\"}`
Output: `{\"success\": true, \"message\": \"Task 123 soft deleted\"}`

### 6. `restore_task`
**Purpose**: Restore soft-deleted task.

**Parameters**:
- `task_id: str` (required)

**Validation**: Task exists and is deleted.

**DB Behavior**: UPDATE `is_deleted=false` WHERE `id` AND `user_id`.

**Example**:
Input: `{\"user_id\": \"abc123\", \"task_id\": \"123\"}`
Output: `{\"success\": true, \"message\": \"Task 123 restored\"}`

### 7. `complete_task`
**Purpose**: Toggle task completion.

**Parameters**:
- `task_id: str` (required)

**Validation**: Task exists.

**DB Behavior**: UPDATE `is_completed = NOT is_completed` WHERE `id` AND `user_id`.

**Example**:
Input: `{\"user_id\": \"abc123\", \"task_id\": \"123\"}`
Output: `{\"success\": true, \"task\": {... toggled ...}, \"was_completed\": false}`