# Chat API Specification

## Overview
The Chat API provides a stateless endpoint for interacting with the Todo AI Agent. Each request processes a single user message in the context of persisted conversation history. Built on FastAPI, integrates OpenAI Agents SDK (OpenRouter), and MCP tools.

**Endpoint**: `POST /api/{user_id}/chat`

**Path Param**: `user_id: str` - Authenticated user ID.

**Stateless Guarantee**: No in-memory state; conversation history fetched/stored in DB per request.

## Request Schema
```json
{
  \"message\": \"string\" (required, user input, max 2000 chars),
  \"conversation_id\": \"string|null\" (optional, continue existing convo or create new)
}
```

## Response Schema
```json
{
  \"success\": true,
  \"conversation_id\": \"string\",
  \"agent_response\": \"string\" (final response text),
  \"tool_calls\": [  // Logged tool calls this turn
    {
      \"tool_name\": \"string\",
      \"input\": object,
      \"output\": object|null
    }
  ],
  \"messages\": [  // Updated history snippet (last 10)
    {
      \"role\": \"user|assistant|system|tool\",
      \"content\": \"string\",
      \"timestamp\": \"ISO datetime\"
    }
  ]
}
```

Error Response:
```json
{
  \"success\": false,
  \"error\": \"string\"
}
```

## Conversation Persistence
- **Storage**: New table `conversations` (id, user_id, created_at, updated_at).
- **Messages Table**: `chat_messages` (id, conversation_id, role, content, tool_calls JSONB, timestamp).
- **New Convo**: If no `conversation_id`, create new; return ID.
- **History Injection**: Fetch last N=20 messages for agent context (system prompt + history).
- **Pruning**: Keep last 50 messages per convo; archive older.

## Agent Execution Flow
1. **Auth & Input Validation**: Verify user_id, message non-empty.
2. **Fetch History**: GET last 20 messages for `conversation_id` (or create new).
3. **Build System Prompt**: Embed constitution + spec + history.
4. **Agent Invocation**:
   - OpenAI Agents SDK client (OpenRouter base_url, api_key).
   - Model: claude-3.5-sonnet (or equiv).
   - Tools: MCP endpoints (add_task, list_tasks, etc.).
5. **Process Turns**: Agent loop until final response (max 5 turns).
6. **Log Messages**: INSERT user message, tool calls, agent response.
7. **Return Response**: JSON with agent_response, tool_calls, updated messages.

## Tool Call Logging
- Each tool call: Stored in `tool_calls` array in message.
- MCP calls: HTTP POST to `/mcp/{tool_name}` with user_id.
- Retry: Agent handles via SDK; log failures.

## Security & NFRs
- **Auth**: Bearer token → user_id.
- **Rate Limit**: 10 req/min per user.
- **Timeouts**: 30s per agent turn.
- **Data Isolation**: All queries scoped to `user_id`.
- **PII**: No logging of sensitive content.

## Error Handling
- Auth fail: 401 Unauthorized.
- Invalid input: 400 Bad Request.
- Agent timeout: 408, fallback \"Try again.\"
- DB fail: 500, rollback tx.

## Example Flow
**Req**: POST /api/user123/chat { \"message\": \"add task buy milk\" }
**Flow**:
1. Fetch/create convo.
2. Agent: Parses → Confirms → (waits, but since stateless, next req).
3. Log: User msg.
**Res**: { \"agent_response\": \"Confirm: Create...?\", ... }

**Next Req**: { \"message\": \"YES\" }
**Res**: Tool call logged, task created.