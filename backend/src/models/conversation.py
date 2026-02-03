"""Conversation and message database models for AI chat agent."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class Conversation(SQLModel, table=True):
    """Conversation entity for AI chat sessions."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["ChatMessage"] = Relationship(back_populates="conversation")


class ChatMessage(SQLModel, table=True):
    """Individual message in a conversation."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id")
    role: str = Field(min_length=1, max_length=20)  # "user", "assistant", "system", "tool"
    content: str = Field(default="", max_length=10000)
    tool_name: Optional[str] = Field(default=None, max_length=100)
    tool_input: Optional[str] = Field(default=None, max_length=5000)
    tool_output: Optional[str] = Field(default=None, max_length=5000)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")


# Add conversation relationship to User model
# Note: This will be added to user.py in a separate migration