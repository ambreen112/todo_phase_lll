# Phase 3 Implementation Plan: AI Chatbot Agent

## Scope
Upgrade Phase 2 Todo Web App to Phase 3 by adding stateless AI Todo Agent using OpenAI Agents SDK (OpenRouter), MCP tools for task ops, Chat API, conversation persistence, and Frontend ChatKit integration.

**In Scope**:
- Backend: Chat API endpoint, MCP tools, DB schemas for convos/messages.
- Agent: Stateless OpenAI Agents SDK setup with MCP tools.
- Frontend: ChatKit UI in dashboard.
- Auth: Reuse Better Auth.

**Out of Scope**:
- New task fields/models.
- Production deployment changes.
- Advanced agent features (multi-agent, long-term memory).

**Dependencies**:
- OpenRouter API key in `.env`.
- Existing task DB schema.
- Phase 2 auth/DB.

## Key Decisions
1. **OpenAI SDK + OpenRouter**: Compatible; base_url override.
2. **Stateless Agent**: History injected per request.
3. **MCP as Tools**: HTTP endpoints for agent tools.
4. **ChatKit**: Vercel/ChatKit for UI (Next.js compatible).

**Rationale**: Minimal changes; leverages SDK strengths.

## Step-by-Step Plan

### 1. Database Migrations
- Add `conversations` table: id, user_id, created_at, updated_at.
- Add `chat_messages` table: id, conversation_id, role, content, tool_calls JSONB, timestamp.
- Alembic migration.

### 2. MCP Server/Tools
- Create `/mcp/{tool_name}` POST endpoints (e.g., /mcp/add_task).
- Implement each tool per specs/mcp/tools.md.
- Auth middleware: user_id from token.
- Return JSON as spec'd.

### 3. Chat API Endpoint
- POST /api/{user_id}/chat.
- Fetch/create convo, load history.
- Init OpenAI client (OpenRouter).
- System prompt: Embed constitution + spec.
- Agent.run() with tools (MCP URLs).
- Persist messages/tool calls.
- Return response.

### 4. Agent Configuration
- Tools: Register MCP as OpenAI tools (schemas from specs).
- Model: claude-3.5-sonnet.
- Max turns: 5.
- Prompt engineering for confirmation flow.

### 5. OpenRouter Setup
- Client: OpenAI(api_key=OPENROUTER_KEY, base_url=OPENROUTER_BASE).
- Env vars: OPENROUTER_API_KEY, OPENROUTER_BASE_URL.

### 6. Frontend Integration
- Install @vercel/chatkit or similar.
- Add Chat component to dashboard/page.tsx.
- Auth: Pass user token.
- Connect to /api/{user_id}/chat.
- Handle convo ID persistence (localStorage).

### 7. Authentication Handling
- Reuse backend/src/api/deps.py get_current_user.
- Frontend: lib/auth-provider.tsx token.

### 8. Validation Checkpoints
- **Post-DB**: Run migration; verify tables.
- **Post-MCP**: Test each tool curl; verify DB changes.
- **Post-Chat API**: Postman test convo flow.
- **Post-Agent**: Manual chat; confirm statelessness.
- **Post-Frontend**: E2E chat UI; CRUD via natural lang.
- **Tests**: Add pytest for tools/API; Cypress for UI.

## Risks & Mitigations
- **Agent Hallucination**: Strict system prompt + few-shot examples.
- **Cost**: Rate limits; monitor OpenRouter usage.
- **Latency**: Async DB; timeout agent turns.

## Next Steps
Run `/sp.tasks` then `/sp.implement`.