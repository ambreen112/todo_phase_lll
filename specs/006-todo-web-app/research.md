# Research: Phase 2 Todo Web Application

This document captures technology decisions made during the planning phase.

## Technology Stack Decisions

### Backend: FastAPI with SQLModel

**Decision**: Use FastAPI as the backend framework with SQLModel for database operations.

**Rationale**:
- FastAPI provides automatic OpenAPI documentation from type hints
- Native async/await support for handling concurrent requests
- SQLModel integrates SQLAlchemy with Pydantic for unified model definitions
- Type safety from Python 3.13+ type hints throughout
- Automatic request validation with clear error responses

**Alternatives Considered**:
- Django: More features than needed, heavier weight for this use case
- Flask: Less modern, no automatic async support or OpenAPI generation

### Database: Neon Serverless PostgreSQL

**Decision**: Use Neon Serverless PostgreSQL as the database.

**Rationale**:
- Serverless PostgreSQL with automatic scaling
- Good free tier for development
- Connection pooling for serverless environments
- Compatible with existing SQLModel/SQLAlchemy patterns
- Industry-standard PostgreSQL for data persistence

**Alternatives Considered**:
- SQLite: Not suitable for multi-user production deployment
- MongoDB: NoSQL doesn't fit the relational user-task model well
- Supabase: Good alternative, but Neon was selected for simplicity

### Authentication: Better Auth with JWT

**Decision**: Use Better Auth on the frontend with JWT tokens.

**Rationale**:
- Better Auth provides React hooks for authentication state
- JWT enables stateless authentication suitable for serverless environments
- Shared secret allows backend to verify tokens without session storage
- Industry-standard approach for modern web applications

**Alternatives Considered**:
- NextAuth.js: Good alternative, but Better Auth was specified in constitution
- Session-based auth: Requires server-side session storage, less scalable

### Frontend: Next.js 16+ with App Router

**Decision**: Use Next.js 16+ with App Router and TypeScript.

**Rationale**:
- App Router provides modern React server components
- Built-in routing and API routes capability
- Excellent TypeScript support
- Server-side rendering for initial page loads
- Large ecosystem of UI component libraries

**Alternatives Considered**:
- React + Vite: Simpler but lacks Next.js features (SSR, API routes)
- Remix: Good alternative but less market adoption

## Implementation Patterns

### JWT Token Structure

**Decision**: JWT tokens contain user_id, email, and expiration.

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1234567890
}
```

**Rationale**:
- Minimal claims to reduce token size
- User ID extracted from token for ownership enforcement
- Email included for potential display purposes
- Standard expiration for 7-day session length

### Task Ownership Enforcement

**Decision**: Backend validates task ownership on every request.

**Rationale**:
- Security enforced at API layer, not trusted to frontend
- Database queries filter by owner_id matching authenticated user
- Returns 404 (not 403) for non-existent tasks to prevent enumeration
- Consistent ownership check across all task endpoints

**Implementation**:
```python
# Example ownership check pattern
task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user_id).first()
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

### API Design Patterns

**Decision**: RESTful API with JSON request/response bodies.

**Rationale**:
- Simple, well-understood pattern
- Easy to document with OpenAPI
- Good fit for CRUD operations
- Frontend can use standard fetch or axios

**Endpoint Pattern**:
- Authentication: `/auth/signup`, `/auth/login`
- Tasks: `/api/{user_id}/tasks` with standard CRUD methods

### Frontend State Management

**Decision**: Use React Query (TanStack Query) for server state.

**Rationale**:
- Automatic caching and revalidation
- Optimistic updates for better UX
- Loading and error states handled automatically
- Works well with React hooks pattern

**Alternatives Considered**:
- Redux: Too much boilerplate for this use case
- Context API: Sufficient for auth, but React Query better for data

## Security Considerations

### Password Storage

**Decision**: Store bcrypt hashes of passwords.

**Rationale**:
- Industry-standard password hashing
- Configurable work factor (cost factor 12)
- Salt included in hash, no separate storage needed
- Well-supported in Python via bcrypt library

### JWT Configuration

**Decision**: HS256 algorithm, 7-day expiration.

**Rationale**:
- HS256 widely supported and audited
- 7-day expiration balances security with UX
- Secret key stored in environment variables
- Token refresh not implemented (user re-logs in)

### CORS Configuration

**Decision**: Configure CORS to allow only frontend origin.

**Rationale**:
- Prevents cross-origin attacks
- Explicit origin list rather than wildcard
- Credentials allowed (cookies/auth headers)

## Development Setup

### Environment Variables

**Decision**: Use `.env` file for local development.

**Required Variables**:
```
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

**Rationale**:
- Separates configuration from code
- Easy to manage different environments
- Not committed to version control

### Testing Strategy

**Decision**: pytest for backend, Jest/Vitest for frontend.

**Rationale**:
- pytest is Python standard for testing
- Jest/Vitest is JavaScript/TypeScript standard
- Coverage targets of 80% for backend, 70% for frontend
- Integration tests for API contracts

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Soft-delete or hard-delete? | Hard-delete for simplicity; users can recreate tasks if needed |
| Task filtering/sorting? | Deferred to future Phase; focus on CRUD for Phase 2 |
| Real-time updates? | React Query revalidation; no WebSocket for Phase 2 |
| Password reset flow? | Deferred to future Phase; email sending requires external service |
