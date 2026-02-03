"""Task database model."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, ARRAY, String, Text
from sqlmodel import Field, Relationship, SQLModel

from .user import User


class TaskPriority(str, Enum):
    """Task priority levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TaskRecurrence(str, Enum):
    """Task recurrence patterns."""
    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class Task(SQLModel, table=True):
    """Task entity belonging to a user."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(min_length=1, max_length=256)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(Text)))
    due_date: Optional[datetime] = Field(default=None)
    recurrence: TaskRecurrence = Field(default=TaskRecurrence.NONE)
    parent_id: Optional[UUID] = Field(default=None, foreign_key="task.id")
    deleted_at: Optional[datetime] = Field(default=None)
    deletion_reason: Optional[str] = Field(default=None, max_length=500)
    owner_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    owner: User = Relationship(back_populates="tasks")
    parent: Optional["Task"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Task.id", "foreign_keys": "[Task.parent_id]"}
    )
    children: List["Task"] = Relationship(back_populates="parent")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title} completed={self.completed}>"

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.completed:
            return False
        return self.due_date < datetime.now(timezone.utc)

    @property
    def is_due_today(self) -> bool:
        """Check if task is due today."""
        if not self.due_date or self.completed:
            return False
        today = datetime.now(timezone.utc).date()
        return self.due_date.date() == today

    @property
    def is_recurring(self) -> bool:
        """Check if task is recurring."""
        return self.recurrence != TaskRecurrence.NONE
