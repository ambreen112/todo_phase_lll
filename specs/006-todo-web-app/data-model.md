# Data Model: Phase 2 Todo Web Application

This document defines the database schema and data models for the application.

## Entity Relationship

```
User (1) ----< (N) Task
```

A User has zero or more Tasks. Each Task belongs to exactly one User.

## User Entity

### Database Schema

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import List, Optional
import uuid

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="owner")
```

### Validation Rules

| Field | Constraint |
|-------|------------|
| email | Required, max 255 chars, valid email format, unique |
| password_hash | Required, stores bcrypt hash (not plaintext) |

## Task Entity

### Database Schema

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(256) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'MEDIUM' CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
    tags TEXT[],
    due_date TIMESTAMP WITH TIME ZONE,
    recurrence VARCHAR(10) DEFAULT 'NONE' CHECK (recurrence IN ('NONE', 'DAILY', 'WEEKLY', 'MONTHLY')),
    parent_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    deletion_reason VARCHAR(500),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_owner ON tasks(owner_id);
CREATE INDEX idx_tasks_completed ON tasks(completed) WHERE completed = FALSE;
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_deleted ON tasks(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_tasks_recurrence ON tasks(recurrence) WHERE recurrence != 'NONE';
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
```

### SQLModel Definition

```python
from enum import Enum

class TaskPriority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class TaskRecurrence(str, Enum):
    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=256, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String(50))))
    due_date: Optional[datetime] = Field(default=None)
    recurrence: TaskRecurrence = Field(default=TaskRecurrence.NONE)
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="task.id", on_delete="SET NULL")
    deleted_at: Optional[datetime] = Field(default=None)
    deletion_reason: Optional[str] = Field(default=None, max_length=500)
    owner_id: uuid.UUID = Field(foreign_key="user.id", on_delete="CASCADE")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    owner: User = Relationship(back_populates="tasks")
    parent: Optional["Task"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )
    children: List["Task"] = Relationship(back_populates="parent")
```

### Validation Rules

| Field | Constraint |
|-------|------------|
| title | Required, 1-256 characters, not empty string |
| description | Optional, max 2000 characters |
| completed | Boolean, defaults to false |
| priority | Enum: HIGH/MEDIUM/LOW, defaults to MEDIUM |
| tags | Optional array of strings, max 50 characters per tag |
| due_date | Optional, ISO 8601 datetime format |
| recurrence | Enum: NONE/DAILY/WEEKLY/MONTHLY, defaults to NONE |
| parent_id | Optional, foreign key to tasks.id (for recurring instances) |
| deleted_at | Optional, ISO 8601 datetime, set on soft delete |
| deletion_reason | Required when deleting, max 500 characters |
| owner_id | Required, foreign key to users.id |

## API Schemas (Pydantic)

### Authentication Schemas

```python
class SignupRequest(SQLModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

class LoginRequest(SQLModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=128)

class AuthResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
    email: str
```

### Task Schemas

```python
class TaskCreate(SQLModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[TaskPriority] = Field(TaskPriority.MEDIUM)
    tags: Optional[List[str]] = Field(None)
    due_date: Optional[datetime] = Field(None)
    recurrence: Optional[TaskRecurrence] = Field(TaskRecurrence.NONE)

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[TaskPriority] = Field(None)
    tags: Optional[List[str]] = Field(None)
    due_date: Optional[datetime] = Field(None)
    recurrence: Optional[TaskRecurrence] = Field(None)

class TaskDelete(SQLModel):
    deletion_reason: str = Field(..., min_length=1, max_length=500)

class TaskResponse(SQLModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    completed: bool
    priority: TaskPriority
    tags: Optional[List[str]]
    due_date: Optional[datetime]
    recurrence: TaskRecurrence
    parent_id: Optional[uuid.UUID]
    deleted_at: Optional[datetime]
    deletion_reason: Optional[str]
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Computed fields
    is_overdue: bool
    is_due_today: bool
    is_recurring: bool

class TaskListResponse(SQLModel):
    tasks: List[TaskResponse]
    total: int
    overdue_count: int
    due_today_count: int
```

## State Transitions

### Task Completion State Machine

```
[incomplete] --toggle--> [complete]
[complete] --toggle--> [incomplete]
```

### Recurring Task Lifecycle

```
[recurring task] --complete--> [generate next instance with parent_id]
                              [mark current as complete]
                              [calculate next due_date]
```

**Recurrence calculation**:
- DAILY: due_date + 1 day
- WEEKLY: due_date + 7 days
- MONTHLY: due_date + 30 days

### Soft Delete State Machine

```
[active] --delete with reason--> [soft-deleted]
[soft-deleted] --restore--> [active]
```

**Active tasks**: `deleted_at IS NULL`
**Soft-deleted tasks**: `deleted_at IS NOT NULL`

## Migration Strategy

### Initial Migration (Alembic)

```python
# alembic/versions/001_create_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(256), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('completed', sa.Boolean, server_default='false'),
        sa.Column('priority', sa.String(10), server_default='MEDIUM', nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recurrence', sa.String(10), server_default='NONE', nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deletion_reason', sa.String(500), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Add check constraints
    op.create_check_constraint(
        'ck_tasks_priority',
        'tasks',
        "priority IN ('HIGH', 'MEDIUM', 'LOW')"
    )
    op.create_check_constraint(
        'ck_tasks_recurrence',
        'tasks',
        "recurrence IN ('NONE', 'DAILY', 'WEEKLY', 'MONTHLY')"
    )

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_tasks_owner', 'tasks', ['owner_id'])
    op.create_index('idx_tasks_completed', 'tasks', ['completed'], postgresql_where=sa.text('completed = false'))
    op.create_index('idx_tasks_priority', 'tasks', ['priority'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'], postgresql_where=sa.text('due_date IS NOT NULL'))
    op.create_index('idx_tasks_deleted', 'tasks', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_tasks_recurrence', 'tasks', ['recurrence'], postgresql_where=sa.text("recurrence != 'NONE'"))
    op.create_index('idx_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')

def downgrade():
    op.drop_index('idx_tasks_tags', table_name='tasks')
    op.drop_index('idx_tasks_recurrence', table_name='tasks')
    op.drop_index('idx_tasks_deleted', table_name='tasks')
    op.drop_index('idx_tasks_due_date', table_name='tasks')
    op.drop_index('idx_tasks_priority', table_name='tasks')
    op.drop_index('idx_tasks_completed', table_name='tasks')
    op.drop_index('idx_tasks_owner', table_name='tasks')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_constraint('ck_tasks_recurrence', 'tasks')
    op.drop_constraint('ck_tasks_priority', 'tasks')
    op.drop_table('tasks')
    op.drop_table('users')
```

## Index Strategy

| Table | Index | Columns | Purpose | Notes |
|-------|-------|---------|---------|-------|
| users | idx_users_email | email | Fast lookup for login | Unique constraint |
| tasks | idx_tasks_owner | owner_id | Filter tasks by user | Foreign key |
| tasks | idx_tasks_completed | completed | Filter incomplete tasks | Partial index (WHERE completed = false) |
| tasks | idx_tasks_priority | priority | Filter/sort by priority | Supports HIGH/MEDIUM/LOW filters |
| tasks | idx_tasks_due_date | due_date | Filter overdue/due-today | Partial index (WHERE due_date IS NOT NULL) |
| tasks | idx_tasks_deleted | deleted_at | Exclude soft-deleted | Partial index (WHERE deleted_at IS NULL) |
| tasks | idx_tasks_recurrence | recurrence | Find recurring tasks | Partial index (WHERE recurrence != 'NONE') |
| tasks | idx_tasks_tags | tags (GIN) | Search by tags | Full-text search on array |

## Constraints

1. **Unique Constraint**: User email must be unique across all users
2. **Foreign Key**: Task.owner_id references User.id with CASCADE delete (deleting user deletes all their tasks)
3. **Foreign Key**: Task.parent_id references Task.id with SET NULL (deleting parent clears parent_id on children)
4. **Not Null**: title, owner_id, completed, priority, recurrence cannot be null
5. **Check Constraint**: priority must be one of 'HIGH', 'MEDIUM', 'LOW'
6. **Check Constraint**: recurrence must be one of 'NONE', 'DAILY', 'WEEKLY', 'MONTHLY'
7. **Length Limits**:
   - title: 1-256 characters
   - description: max 2000 characters
   - email: max 255 characters
   - deletion_reason: 1-500 characters
   - tags: max 50 characters per tag
8. **Soft Delete Logic**: When deleted_at IS NOT NULL, deletion_reason MUST be provided

## Business Logic & Computed Fields

### Overdue Detection
```python
def is_overdue(task: Task) -> bool:
    """Task is overdue if due_date exists, is in the past, and task is not completed"""
    if not task.due_date or task.completed:
        return False
    return task.due_date < datetime.now(timezone.utc)
```

### Due Today Detection
```python
def is_due_today(task: Task) -> bool:
    """Task is due today if due_date is today and task is not completed"""
    if not task.due_date or task.completed:
        return False
    today = datetime.now(timezone.utc).date()
    return task.due_date.date() == today
```

### Recurring Task Logic
```python
def calculate_next_due_date(current_due_date: datetime, recurrence: TaskRecurrence) -> datetime:
    """Calculate next due date based on recurrence frequency"""
    if recurrence == TaskRecurrence.DAILY:
        return current_due_date + timedelta(days=1)
    elif recurrence == TaskRecurrence.WEEKLY:
        return current_due_date + timedelta(days=7)
    elif recurrence == TaskRecurrence.MONTHLY:
        return current_due_date + timedelta(days=30)
    else:
        return current_due_date

def handle_recurring_completion(task: Task) -> Optional[Task]:
    """When a recurring task is completed, generate the next instance"""
    if task.recurrence == TaskRecurrence.NONE or not task.due_date:
        return None

    next_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        tags=task.tags,
        due_date=calculate_next_due_date(task.due_date, task.recurrence),
        recurrence=task.recurrence,
        parent_id=task.id,  # Link to original task
        owner_id=task.owner_id
    )
    return next_task
```

### Query Patterns

**Get active tasks for user (exclude soft-deleted)**:
```sql
SELECT * FROM tasks
WHERE owner_id = :user_id
  AND deleted_at IS NULL
ORDER BY created_at DESC;
```

**Get overdue tasks**:
```sql
SELECT * FROM tasks
WHERE owner_id = :user_id
  AND deleted_at IS NULL
  AND completed = FALSE
  AND due_date < NOW()
ORDER BY due_date ASC;
```

**Get due today tasks**:
```sql
SELECT * FROM tasks
WHERE owner_id = :user_id
  AND deleted_at IS NULL
  AND completed = FALSE
  AND DATE(due_date) = CURRENT_DATE
ORDER BY due_date ASC;
```

**Filter by priority**:
```sql
SELECT * FROM tasks
WHERE owner_id = :user_id
  AND deleted_at IS NULL
  AND priority = :priority
ORDER BY created_at DESC;
```

**Filter by tag**:
```sql
SELECT * FROM tasks
WHERE owner_id = :user_id
  AND deleted_at IS NULL
  AND :tag = ANY(tags)
ORDER BY created_at DESC;
```

**Search across title, description, tags**:
```sql
SELECT * FROM tasks
WHERE owner_id = :user_id
  AND deleted_at IS NULL
  AND (
    LOWER(title) LIKE :search_term
    OR LOWER(description) LIKE :search_term
    OR EXISTS (
      SELECT 1 FROM unnest(tags) AS tag
      WHERE LOWER(tag) LIKE :search_term
    )
  )
ORDER BY created_at DESC;
```

**Get soft-deleted tasks**:
```sql
SELECT * FROM tasks
WHERE owner_id = :user_id
  AND deleted_at IS NOT NULL
ORDER BY deleted_at DESC;
```

**Get recurring task instances (children of a parent)**:
```sql
SELECT * FROM tasks
WHERE parent_id = :parent_task_id
ORDER BY created_at ASC;
```
