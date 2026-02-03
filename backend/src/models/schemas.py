"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from .user import User
from .task import Task, TaskPriority, TaskRecurrence


# Authentication Schemas
class SignupRequest(BaseModel):
    """Signup request with email and password."""

    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Login request with email and password."""

    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=128)


class AuthResponse(BaseModel):
    """Authentication response with JWT token."""

    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str


# Task Schemas
class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[str] = Field("medium")
    tags: Optional[List[str]] = Field(None)
    due_date: Optional[datetime] = Field(None, json_schema_extra={"format": "date-time"})
    recurrence: Optional[str] = Field("none")


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[str] = Field(None)
    tags: Optional[List[str]] = Field(None)
    due_date: Optional[datetime] = Field(None, json_schema_extra={"format": "date-time"})
    recurrence: Optional[str] = Field(None)


class TaskDelete(BaseModel):
    """Schema for soft-deleting a task."""

    deletion_reason: str = Field(..., min_length=1, max_length=500)


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: Optional[List[str]]
    due_date: Optional[datetime]
    recurrence: str
    parent_id: Optional[UUID]
    deleted_at: Optional[datetime]
    deletion_reason: Optional[str]
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    is_overdue: bool
    is_due_today: bool
    is_recurring: bool

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for list of tasks."""

    tasks: List[TaskResponse]
    total: int
    overdue_count: int
    due_today_count: int


class DeletedTaskListResponse(BaseModel):
    """Schema for list of deleted tasks."""

    tasks: List[TaskResponse]
    total: int


# User Schemas (for responses)
class UserResponse(BaseModel):
    """Schema for user response (without password)."""

    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
