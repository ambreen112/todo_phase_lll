---
id: 5
title: "Configure FastAPI Swagger Authentication"
stage: explainer
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-web-app
branch: 006-todo-web-app
user: default
command: none
labels: ["fastapi", "swagger-ui", "jwt", "oauth2"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - none
tests:
  - none
---

## Prompt

I have a FastAPI backend with JWT authentication.
My APIs work correctly in Thunder Client when I manually send the Authorization: Bearer <token> header, but in Swagger UI (/docs) the Authorize (🔒) button does not appear, and I keep getting 401 Missing authorization header.

I want you to:

Show me how to correctly configure OAuth2 / Bearer authentication in FastAPI so that Swagger UI shows the Authorize button.

Provide a minimal but complete example including:

OAuth2PasswordBearer

/auth/login endpoint

JWT token generation

get_current_user dependency

A protected endpoint like POST /api/{user_id}/tasks

Make sure the Swagger UI accepts the token and sends
Authorization: Bearer <token> automatically.

Explain common mistakes that cause Swagger to miss the authorization header.

## Response snapshot

Showed how to correctly configure OAuth2PasswordBearer in FastAPI to enable the "Authorize" button in Swagger UI. Provided a minimal example including JWT generation, a login endpoint using OAuth2PasswordRequestForm, and a protected route. Explained that the Authorize button requires the oauth2_scheme dependency to be present in the OpenAPI schema components.

## Outcome

- ✅ Impact: User confirmed the button appeared after adding the dependency to a route.
- 🧪 Tests: Manual verification by user.
- 📁 Files: none
- 🔁 Next prompts: None
- 🧠 Reflection: The "Authorize" button is lazily rendered based on the presence of security dependencies in the OpenAPI spec. Linking a route to the OAuth2PasswordBearer is mandatory for visibility.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
