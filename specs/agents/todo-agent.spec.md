# Todo Agent Specification

## Overview
The Todo AI Agent is a stateless conversational interface for managing todo tasks. It interprets natural language user input, maps intents to MCP tools, executes operations, and responds conversationally. Built with OpenAI Agents SDK (OpenRouter compatible), ensuring statelessness via DB-persisted conversation history.

## Supported Operations
The agent supports all Phase 2 task operations via MCP tools:
- **List tasks**: With optional filters (status: active/completed/deleted, priority, due date, search text, tags).
- **List deleted tasks**: Filtered view of soft-deleted tasks.
- **Get single task**: By ID.
- **Create task**: Title, description, priority, tags, due date.
- **Update task**: Patch title, description, priority, tags, due date, completion.
- **Soft delete task**: Mark as deleted (not hard delete).
- **Restore deleted task**: Un-delete by ID.
- **Toggle completion**: Complete/incomplete by ID.

## Response Format Rules
**CRITICAL**: Always respond in natural language. NEVER output raw JSON or function calls to the user.

### Good Response Examples:
- "Here are your tasks with high priority: 1. Buy groceries 2. Call mom"
- "Task 'Buy milk' created successfully with high priority, due on March 15, 2024."
- "I found 3 tasks due this week: ..."

### Bad Response Examples (NEVER DO THIS):
- `{"type": "function", "name": "list_tasks", ...}` ← WRONG
- `{"name": "add_task", "parameters": {...}}` ← WRONG
- Just outputting tool calls without explanation ← WRONG

### Priority vs Due Date Clarification
- **Priority** (HIGH/MEDIUM/LOW): User-defined importance level. NOT related to due dates.
- **Due date**: When the task should be completed by.
- **Overdue**: Tasks past their due date that are NOT completed.
- These are SEPARATE concepts. A HIGH priority task can have any due date or no due date.

## Intent → MCP Tool Mapping
| User Intent | Example Phrases | MCP Tool | Parameters |
|-------------|-----------------|----------|------------|
| List all tasks | "show tasks", "what's on my list?" | `list_tasks` | `filters: {}` |
| Search tasks by keyword | "search sun", "find meeting", "tasks about groceries" | `list_tasks` | `filters: {search: 'sun'}` |
| Filter by tag/label | "tasks with tag work", "show label urgent", "tagged personal" | `list_tasks` | `filters: {tag: 'work'}` |
| Filter by priority | "high priority tasks", "show important tasks" | `list_tasks` | `filters: {priority: 'HIGH'}` |
| Tasks due today | "what's due today?", "today's tasks" | `list_tasks` | `filters: {due_today: true}` |
| Tasks due this week | "what's due this week?", "this week's tasks" | `list_tasks` | `filters: {due_this_week: true}` |
| Overdue tasks | "overdue tasks", "what did I miss?" | `list_tasks` | `filters: {overdue: true}` |
| Completed tasks | "show completed tasks", "done tasks" | `list_tasks` | `filters: {completed: true}` |
| List deleted | "show deleted", "trash" | `list_tasks` | `filters: {deleted: true}` |

## Search vs Tag Intent Rules
**CRITICAL**: Keywords in queries should be treated as SEARCH terms by default, NOT tags.

- **Use `search` filter** for:
  - \"search [keyword]\" → `filters: {search: 'keyword'}`
  - \"find [keyword]\" → `filters: {search: 'keyword'}`
  - \"tasks about [keyword]\" → `filters: {search: 'keyword'}`
  - \"[keyword] tasks\" → `filters: {search: 'keyword'}`
  - Any keyword without explicit \"tag\" or \"label\" → `filters: {search: 'keyword'}`

- **Use `tag` filter ONLY when user explicitly says \"tag\" or \"label\"**:
  - \"tasks with tag [name]\" → `filters: {tag: 'name'}`
  - \"show label [name]\" → `filters: {tag: 'name'}`
  - \"tagged [name]\" → `filters: {tag: 'name'}`

**Example**: \"search task sun\" → `list_tasks(filters: {search: 'sun'})` (searches title/description for \"sun\")

## Add vs Update Intent Rules (CRITICAL)
**CRITICAL**: Distinguish between CREATE (new task) and UPDATE (modify existing task).

### Use `add_task` (CREATE) ONLY when:
- User wants to create a NEW task
- Pattern: "add task [title]", "add '[title]'", "new task: [title]", "create task [title]"
- Examples:
  - "add task buy milk" → `add_task(title: 'buy milk')`
  - "add 'groceries'" → `add_task(title: 'groceries')`
  - "new task: call mom" → `add_task(title: 'call mom')`

### Use `update_task` (UPDATE) when:
- User references an EXISTING task by name/title AND wants to modify it
- Pattern: "add [field] to [task]", "add [field] in [task]", "update [task] with [field]", "set [field] for [task]"
- Examples:
  - "add description to task clothes" → First `list_tasks` to find task, then `update_task(task_id: found_id, description: '...')`
  - "add description in tasks clothes we are buyer" → `update_task` with description "we are buyer" on task "clothes"
  - "set priority high for groceries task" → `update_task` with priority on task "groceries"
  - "add tag work to meeting task" → `update_task` with tags on task "meeting"

### Intent Detection Rules:
1. If user mentions an EXISTING task name (e.g., "task clothes", "the groceries task") → UPDATE intent
2. If user says "add [field] to/in/for task [name]" → UPDATE the existing task, NOT create new
3. Keywords indicating UPDATE: "to task", "in task", "for task", "on task", "task [name] with"
4. Keywords indicating CREATE: "add task", "new task", "create task", "add '[quoted title]'"

### Disambiguation Protocol:
If ambiguous, check if a task with that name exists:
1. Call `list_tasks(filters: {search: '[name]'})` to find matching tasks
2. If task exists → interpret as UPDATE
3. If no task exists → interpret as CREATE

| Get task | \"task 123\", \"details on task 5\" | `get_task` | `task_id: '123'` |
| Create task | \"add task 'buy milk'\", \"new task: call mom due tomorrow\" | `add_task` | `title: 'buy milk', description: '', priority: 'medium', due_date: null` |
| Update task | \"update task 1 to 'buy bread'\", \"set priority high for 2\", \"add description to task X\" | `update_task` | `task_id: '1', title: 'buy bread'` |
| Delete task | \"delete task 3\", \"remove 4\" | `delete_task` | `task_id: '3'` |
| Restore task | \"restore task 5\", \"undelete 6\" | `restore_task` | `task_id: '5'` |
| Complete task | \"complete 7\", \"done with 8\" | `complete_task` | `task_id: '7'` |
| Help | \"help\", \"what can you do?\" | N/A | Fallback response |

## Conversation Flow (Stateless)
1. **Input**: User message + conversation history (from DB).
2. **Intent Parsing**: Agent classifies intent, extracts entities (IDs, dates, text).
3. **Confirmation (Mutations)**: For create/update/delete/complete/restore: Respond \"Confirm: [action] task [details]? YES/NO.\" Wait for user reply.
4. **Tool Execution**: Call MCP tool(s); handle sequential if needed (e.g., get then update).
5. **Response Generation**: Natural language summary of result + task list snippet if relevant.
6. **Persistence**: Log message, tool calls, response to DB for next turn context.

## Confirmation Responses
- Create: \"Confirm: Create task 'Buy groceries' (due tomorrow, high priority)? Reply YES to proceed.\"
- Update: \"Confirm: Update task 123 title to 'Buy bread'? YES/NO.\"
- Delete: \"Confirm: Soft delete task 123 ('Buy milk')? YES/NO.\"
- Always block until YES/NO received in next turn.

## Error Scenarios
- **Task not found**: \"Task ID 999 not found. Say 'list tasks' to see available tasks.\"
- **Invalid input**: \"Sorry, couldn't parse that. Try 'add task [title]' or 'help'.\"
- **Tool error**: \"Operation failed (e.g., DB issue). Try again?\"
- **No intent match**: \"I manage todos: list, add, update, delete, complete, restore. What next?\"
- **Graceful retry**: Suggest alternatives, never crash.

## Stateless Guarantees
- Each request: Fresh agent instance + full history injected as system prompt.
- No shared memory; all state in DB (tasks + conversations).
- Tool calls atomic per turn; multi-tool chains via agent reasoning.

## Examples

### Example 1: Create Task
**User**: \"Add task buy milk due tomorrow.\"
**Agent**: \"Confirm: Create task 'buy milk' due 2024-01-23? YES/NO.\"
**User**: \"YES\"
**Agent**: \"Task created (ID: 456). Current tasks: 1. buy milk (due tomorrow).\"

### Example 2: List Tasks
**User**: \"Show completed tasks.\"
**Agent**: \"Completed: 1. 'Done task' (ID: 123). Anything else?\"

### Example 3: Update Task with Description (IMPORTANT)
**User**: \"add description in tasks clothes we are buyer\"
**Agent Intent**: This is an UPDATE, not a CREATE. User wants to add description to existing task "clothes".
**Agent Steps**:
1. Call `list_tasks(filters: {search: 'clothes'})` → Finds task ID: abc-123
2. Call `update_task(task_id: 'abc-123', description: 'we are buyer')`
**Agent Response**: \"Confirm: Update task 'clothes' with description 'we are buyer'? YES/NO.\"
**User**: \"YES\"
**Agent**: \"Task 'clothes' updated with description 'we are buyer'.\"

### Example 4: Distinguish Add Task vs Add Field
**WRONG interpretation**:
- User says: "add description to task meeting notes"
- Agent WRONGLY creates new task called "description to task meeting notes" ← WRONG!

**CORRECT interpretation**:
- User says: "add description to task meeting notes"
- Agent recognizes: UPDATE existing task "meeting notes" with a description
- Agent asks: "What description would you like to add to task 'meeting notes'?"
- OR if description provided: Agent updates the task with that description