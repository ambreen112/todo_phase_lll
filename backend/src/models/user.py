"""User database model."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """User entity for authentication and task ownership."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="owner", cascade_delete="all")
    conversations: List["Conversation"] = Relationship(back_populates="user", cascade_delete="all")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
