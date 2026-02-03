---
id: 2
title: Phase 2 Constitution Update
stage: constitution
date: 2026-01-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-phase2
branch: main
user: user
command: sp.constitution
labels: [constitution, todo, phase2, governance, web-app]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - null
---

## Prompt

```text
You are working on Phase 2 of a Todo application.

This project follows Spec-Kit Plus and Agentic Dev Stack workflow.

CONSTITUTION:
- Phase: Phase 2 – Full-Stack Web Application
- Previous Phase: Phase 1 Console-based Todo app
- Development style: Spec-driven, no manual coding
- All changes must be derived from written specifications

TECH STACK (MANDATORY):
- Frontend: Next.js 16+ (App Router, TypeScript)
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (JWT-based)

SECURITY RULES:
- All API endpoints require JWT authentication
- JWT must be issued by Better Auth
- Backend must verify JWT using shared secret
- Users may only access their own tasks

ARCHITECTURE RULES:
- Monorepo structure with /frontend and /backend
- REST API design
- Stateless authentication
- Task ownership enforced at backend

PROCESS RULES:
- Always read specs before coding
- Do not invent features
- Follow Spec-Kit directory structure
- If a requirement is missing, ask for clarification

Acknowledge this constitution and wait for Phase 2 specifications.
```

## Response snapshot

Updated constitution from v1.0.0 to v2.0.0 with Phase 2 web application specifications. Replaced all 5 Phase 1 principles with 6 new Phase 2 principles (AI-Native Engineering, Agentic Architecture, Web-First Application, Spec-Driven Integrity, Type-Safe Development, Stateless Authentication). Added comprehensive sections: Technology Stack, Security Requirements, Architecture, Performance & Reliability, Data Management, Operational Readiness, Development Workflow, and Governance.

## Outcome

- ✅ Impact: Major constitution update transitioning from console CLI to full-stack web application with Next.js/FastAPI stack
- 🧪 Tests: No tests required for constitution update
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: Ready to receive Phase 2 feature specifications
- 🧠 Reflection: Constitution now mandates full tech stack (Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth JWT) and security requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
