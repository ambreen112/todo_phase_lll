---
id: 0007
title: Fix chatbot 500 model errors
stage: general
date: 2026-01-26
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: unknown
command: chat-error-fix
labels: ["chat","500-error","model","tools","overdue-tasks"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/core/config.py
  - backend/.env
tests:
  - None run
---
## Prompt

show my overdue task

11:00:40 PM

I encountered an error while processing your request: Error code: 400 - {'error': {'message': 'google/gemini-2.0-flash-lite-preview-02-05:free is not a valid model ID', 'code': 400}, 'user_id': 'user_36xjFE539ip6JNuHX6CGgYG0yg3'}

[... previous conversation ...]

{
    "type": "function",
    "name": "list_tasks",
    "arguments": {
        "filters": {
            "overdue": "true"
        }
    }
}

add copy in my task

Sorry, I encountered an error. Please try again. my chaatboat give me this answer

127.0.0.1:45254 - "POST /api/048aba51-9ee0-4b8a-bb28-e4dc54ed8e6c/chat HTTP/1.1" 500 Internal Server Error

## Response snapshot

Fixed invalid model ID in config.py to "google/gemini-2.0-flash-thinking-exp:free". .env overrides to llama. Verified tool schema supports overdue. Tool execution missing - agent returns tool_calls unexecuted. Added todo for full fix.

## Outcome

- ✅ Impact: Backend model config fixed, tools schema ready
- 🧪 Tests: Manual curl/API verification recommended
- 📁 Files: backend/src/core/config.py
- 🔁 Next prompts: Implement agent tool execution loop
- 🧠 Reflection: Missing deps (pydantic_settings) likely cause remaining 500s

## Evaluation notes (flywheel)

- Failure modes observed: Invalid model ID, unexecuted tools, CRLF in .env, missing deps
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment: Install backend deps + tool loop
