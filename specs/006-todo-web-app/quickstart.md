# Quickstart: Phase 2 Todo Web Application

This guide covers setting up the development environment for the Phase 2 web application.

## Prerequisites

- Python 3.13+
- Node.js 20+ (LTS recommended)
- PostgreSQL client (psql)
- Git

## Environment Setup

### 1. Clone and Checkout

```bash
git checkout 006-todo-web-app
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -e ".[dev]"

# Copy environment template
cp ../.env.example .env

# Edit .env with your credentials
nano .env
```

### 3. Frontend Setup

```bash
# In a new terminal (keep backend running)
cd frontend

# Install dependencies
npm install

# Copy environment template
cp ../.env.example .env.local

# Edit .env.local with your credentials
nano .env.local
```

### 4. Database Setup (Neon PostgreSQL)

1. Create a Neon project at https://neon.tech
2. Get your connection string from the Neon dashboard
3. Add to backend `.env`:

```env
DATABASE_URL=postgresql://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require
```

### 5. Initialize Database

```bash
cd backend
alembic upgrade head
```

## Running the Application

### Backend (Terminal 1)

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Application available at: http://localhost:3000

## Environment Variables

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | Neon PostgreSQL connection string | Yes |
| JWT_SECRET_KEY | Secret for signing JWTs (use long random string) | Yes |
| ALGORITHM | JWT algorithm (HS256) | No |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration (10080 = 7 days) | No |
| FRONTEND_URL | Frontend origin for CORS | Yes |
| BACKEND_URL | Backend origin (optional) | No |

### Frontend (.env.local)

| Variable | Description | Required |
|----------|-------------|----------|
| NEXT_PUBLIC_API_URL | Backend API URL | Yes |
| BETTER_AUTH_URL | Backend URL for auth | Yes |

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest --cov=src --cov-report=term-missing

# Frontend tests
cd frontend
npm test
```

### Type Checking

```bash
# Backend
cd backend
mypy src

# Frontend
cd frontend
npx tsc --noEmit
```

### Linting

```bash
# Backend
cd backend
ruff check src

# Frontend
cd frontend
npm run lint
```

## Common Tasks

### Creating a New Migration

```bash
cd backend
albic revision -m "description"
# Edit the generated file
alembic upgrade head
```

### Resetting the Database

```bash
cd backend
alembic downgrade base
alembic upgrade head
```

### Adding Dependencies

```bash
# Backend
cd backend
poetry add package-name
poetry add --group dev package-name

# Frontend
cd frontend
npm install package-name
```

## Troubleshooting

### Database Connection Failed

- Verify DATABASE_URL is correct
- Check Neon dashboard for connection issues
- Ensure IP is allowlisted if using IP restrictions

### CORS Errors

- Verify FRONTEND_URL matches actual frontend origin
- Check for trailing slashes (should not have them)

### JWT Verification Fails

- Ensure JWT_SECRET_KEY is the same in backend and frontend auth config
- Check token hasn't expired

## Next Steps

1. Review the API specification at `contracts/openapi.yaml`
2. Run `/sp.tasks` to generate implementation tasks
3. Begin implementation following the task list
