# Todo App - Full Stack Task Management

A modern full-stack todo application built with FastAPI (backend) and Next.js (frontend), featuring an AI-powered chatbot for natural language task management.

## Features

### Core Task Management
- **Task Management**: Create, edit, complete, delete, and restore tasks
- **Priority Levels**: HIGH, MEDIUM, LOW with visual indicators
- **Due Dates**: Set deadlines with overdue and due-today alerts
- **Recurring Tasks**: Recurrence fields + next-instance behavior on task completion
- **Tags**: Organize tasks with multiple labels
- **Search & Filter**: Search by keyword; filter by status, priority, tags, or due date
- **Sort**: Reorder by created date, due date, priority, or title
- **Soft-Delete**: Delete with reasons and restore from deleted list
- **Notifications**: In-app + browser notifications for overdue and due-today tasks

### AI Chatbot (Phase 3)
- **Natural Language Commands**: Manage tasks using conversational language
- **Smart Intent Detection**: Preprocessor handles complex patterns reliably
- **Supported Commands**:
  - `add task [title] with [priority] priority` - Create new task
  - `add description [text] in task [name]` - Update task description
  - `change priority of [name] task to [priority]` - Update priority
  - `delete my [name] task with reason [reason]` - Soft delete with reason
  - `complete my [name] task` - Mark task complete
  - `show my all tasks` - List all tasks
  - `show [priority] priority tasks` - Filter by priority
  - `show deleted tasks` - View deleted tasks

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLModel**: Database ORM with SQLAlchemy
- **PostgreSQL (Neon)**: Primary database (configured via `DATABASE_URL`)
- **Alembic**: Database migrations
- **Uvicorn**: ASGI server
- **python-jose**: JWT authentication
- **OpenAI SDK**: AI agent integration (OpenRouter compatible)

### Frontend
- **Next.js 16**: React framework (App Router)
- **React 19**: UI library
- **Tailwind CSS**: Utility-first CSS framework
- **TanStack Query**: Data fetching and caching
- **Axios**: HTTP client

### AI Agent
- **OpenRouter**: LLM provider (supports multiple models)
- **Message Preprocessor**: Pattern detection for reliable command execution
- **Tool Executor**: Direct database operations via MCP tools

## Project Structure

```
phase1_todo/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes/          # API endpoints
│   │   │   │   ├── auth.py      # Authentication
│   │   │   │   ├── tasks.py     # Task CRUD
│   │   │   │   └── chat.py      # AI chatbot endpoint
│   │   │   └── deps.py          # Dependencies
│   │   ├── agents/              # AI Agent system
│   │   │   ├── main_agent.py    # TodoAgent class
│   │   │   ├── message_preprocessor.py  # Intent detection
│   │   │   ├── tool_executor.py # Tool execution
│   │   │   ├── tool_registry.py # MCP tool definitions
│   │   │   ├── system_prompt.py # Agent prompts
│   │   │   └── openai_client.py # OpenRouter client
│   │   ├── core/
│   │   │   ├── security.py      # JWT handling
│   │   │   └── config.py        # Settings
│   │   ├── models/
│   │   │   ├── schemas.py       # Pydantic schemas
│   │   │   ├── task.py          # Task model
│   │   │   ├── user.py          # User model
│   │   │   └── conversation.py  # Chat history model
│   │   └── main.py              # App entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/          # Auth pages (login, signup)
│   │   │   └── (dashboard)/     # Dashboard page
│   │   ├── components/          # React components
│   │   │   ├── Button.tsx
│   │   │   ├── CreateTaskForm.tsx
│   │   │   ├── EditTaskForm.tsx
│   │   │   ├── ChatBot.tsx      # AI chatbot component
│   │   │   ├── TaskItem.tsx
│   │   │   └── TaskList.tsx
│   │   ├── lib/                 # Utilities
│   │   │   ├── api.ts           # API client
│   │   │   ├── auth-provider.tsx
│   │   │   └── notifications.tsx
│   │   └── types/               # TypeScript types
│   └── package.json
├── specs/
│   └── agents/                  # Agent specifications
│       ├── todo-agent.constitution.md  # Core rules
│       └── todo-agent.spec.md   # Behavior spec
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
uvicorn src.main:app --reload
```

Backend runs at: http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend runs at: http://localhost:3000

### Environment Variables

#### Backend (.env)
```
# Database
DATABASE_URL=postgresql://user:pass@host/db

# JWT Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Agent (OpenRouter)
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=meta-llama/llama-3.1-8b-instruct
```

#### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=false  # Set to true for mock API
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login and get JWT token

### Tasks
- `GET /api/{user_id}/tasks` - List tasks with filters
- `GET /api/{user_id}/tasks/deleted` - List deleted tasks
- `GET /api/{user_id}/tasks/{task_id}` - Get single task
- `POST /api/{user_id}/tasks` - Create task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Soft-delete task
- `POST /api/{user_id}/tasks/{task_id}/restore` - Restore deleted task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle completion

### Chat (AI Agent)
- `POST /api/{user_id}/chat` - Send message to AI chatbot
- `GET /api/{user_id}/conversations` - List chat conversations
- `GET /api/{user_id}/conversations/{id}` - Get conversation history

## Filter Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `completed` | boolean | Filter by completion status |
| `priority` | string | Filter by priority (HIGH, MEDIUM, LOW) |
| `tag` | string | Filter by exact tag match |
| `due_status` | string | Filter by due status (overdue, due_today, future) |
| `search` | string | Search in title and description |
| `sort_by` | string | Sort field (created_at, due_date, priority, title) |
| `sort_order` | string | Sort order (asc, desc) |

## Agent Documentation

The Phase 2 Todo Agent is a web-based assistant that helps users manage tasks through a stateless, tool-driven interface. See:

- **Constitution**: `specs/agents/todo-agent.md` — Agent behavior rules, security invariants, non-goals
- **Tools**: `specs/agents/tools.md` — Tool definitions (create, list, get, update, toggle, delete, restore) and hard usage rules
- **Planning**: `specs/agents/planning.md` — Execution flow (intent → validate → tool → respond) and multi-step patterns
- **Tasks**: `specs/agents/tasks.md` — Implementation task breakdown for agent spec completion

## Development

This project follows **Spec-Driven Development (SDD)** methodology:

1. **Specs** (`specs/`): Feature requirements
2. **Plan**: Architecture decisions
3. **Tasks**: Implementation steps
4. **PHR** (`history/prompts/`): Prompt History Records for traceability
5. **ADR** (`history/adr/`): Architecture Decision Records
#   t o d o _ p h a s e _ l l l  
 