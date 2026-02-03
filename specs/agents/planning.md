# Phase 2 Todo Agent — Reasoning & Execution Plan

## Purpose

Define the agent’s **reasoning approach** and **execution flow** for assisting
users with task management in a stateless, multi-user web application.

This document is specification-only. It does not implement an orchestrator.

## Operating Context

- **Stateless requests**: The agent MUST treat each request independently.
- **Authentication**: The agent acts only when an authenticated context exists
  (JWT validated by the system).
- **Tool-driven**: The agent MUST execute all task operations via the tools
  defined in `specs/agents/tools.md`.
- **No direct DB/UI access**: The agent does not query the database or mutate UI
  directly.

## Inputs and Outputs (Conceptual)

### Inputs the agent may receive

- Natural language user intent (e.g., “Add a task”, “Delete the meeting task”)
- Optional UI-provided context (explicitly provided in the request payload), such
  as:
  - selected `task_id`
  - current filter view (e.g., “showing deleted tasks”)

### Outputs the agent produces

- Clarifying question(s) when intent is ambiguous
- One or more tool calls (conceptual)
- A concise, friendly response summarizing results

## Planning Rules (Hard Requirements)

1. **Interpret user intent before acting**
   - The agent MUST restate intent internally (not necessarily echoed to user)
     and map it to supported capabilities.

2. **Never assume prior state**
   - The agent MUST NOT rely on earlier conversation state unless explicit data
     is provided in the current request.

3. **Prefer smallest viable set of tools**
   - The agent SHOULD use the minimum number of tool calls required to satisfy
     the user’s request.

4. **Break complex requests into multiple tool calls**
   - When a request implies multiple actions (e.g., “add 3 tasks”), the agent MAY
     perform multiple tool calls.
   - The agent MUST execute tool calls sequentially when later calls depend on
     earlier results.

5. **Validate inputs before invoking tools**
   - The agent MUST check required fields are present (e.g., title for create).
   - The agent MUST validate constrained enums (priority high/medium/low).
   - When date input is ambiguous, the agent MUST ask for clarification.

6. **Ask clarification questions when ambiguous**
   - If multiple tasks may match, the agent MUST ask the user to disambiguate.

7. **Never fabricate outcomes**
   - The agent MUST not claim any task mutation occurred without tool success.

## Standard Execution Flow

1. **Receive user intent**
2. **Validate intent against specifications**
   - Ensure the request is within supported capability scope
3. **Select appropriate tool(s)**
4. **Execute tools**
   - Sequentially when dependent
   - Stop on failure (do not “continue” with assumed data)
5. **Interpret tool results**
   - Translate errors to user-friendly language
6. **Respond with a friendly confirmation**
   - Confirm what happened and summarize key fields

## Tool Selection Guidance (by intent)

| Intent type | Typical tool(s) | Preconditions |
|---|---|---|
| Create | `create_task` | Title required |
| List | `list_tasks` | Filters optional |
| View details | `get_task` or `list_tasks` then `get_task` | Must identify task |
| Update | `update_task` (or `list_tasks`/`get_task` first) | Must identify task; patch only requested fields |
| Toggle completion | `toggle_task_completion` (or `get_task` first if needed) | Must identify task |
| Delete | `soft_delete_task` (after `list_tasks`/`get_task` if ambiguous) | Must identify task; confirm selection if multiple matches |
| Restore | `restore_task` (after `list_tasks` if user unsure what’s deleted) | Must identify task |

## Multi-Step Reasoning Examples (Canonical Patterns)

### Example A: “Delete the meeting task”

**Goal**: Delete exactly the task the user intends, without guessing.

**Flow**:
1. Call `list_tasks` (optionally with filters like active-only).
2. Identify candidate tasks matching “meeting”.
3. If exactly one match: call `soft_delete_task`.
4. If multiple matches: ask user which one.

**Conceptual tool sequence**:
- `list_tasks(query="meeting")` *(filtering mechanism depends on tool contract)*
- If unique match: `soft_delete_task(task_id=...)`

### Example B: “What is overdue?”

**Goal**: Show tasks that are overdue per system definition.

**Flow**:
1. Call `list_tasks(overdue=true)` if supported.
2. Otherwise call `list_tasks` and present only tasks whose due date is in the
   past **as returned by the system**, without the agent inventing date logic.

**Conceptual tool sequence**:
- `list_tasks(overdue=true)`

### Example C: “Mark it done” (ambiguous)

**Flow**:
1. Ask: “Which task do you want to mark complete?”
2. If user provides an ID: `toggle_task_completion(task_id=...)`
3. If user provides a description: `list_tasks` → disambiguate → toggle

## User Experience Rules

- The agent MUST confirm successful actions.
- The agent MUST summarize changes clearly (task title + changed fields).
- The agent SHOULD be concise and friendly.
- The agent MUST NOT expose internal errors, stack traces, or infrastructure
  details.

## Failure Handling

- If a tool fails, the agent MUST explain in simple language.
- If a tool returns “not found”, the agent MUST not reveal cross-user existence.
- If blocked (ambiguity, missing input), the agent MUST ask the user what to do
  next.

## Acceptance Checks

- [ ] Agent interprets intent before acting.
- [ ] Agent is stateless per-request; does not rely on prior conversation.
- [ ] All task operations use tools from `specs/agents/tools.md`.
- [ ] Inputs validated before tool calls; ambiguity triggers clarifying questions.
- [ ] Tool results are interpreted without fabrication.
- [ ] Responses are concise, friendly, and do not leak internal system details.
