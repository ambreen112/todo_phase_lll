"""
Todo data model representing a single task with id, task text, completion status, and deletion metadata.
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Priority(Enum):
    """Priority levels for todos."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def __str__(self) -> str:
        """Return string representation of priority."""
        return self.value.upper()


class Recurrence(Enum):
    """Recurrence frequency for todos."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

    def __str__(self) -> str:
        """Return string representation of recurrence."""
        return self.value.lower()


class Todo:
    """
    Represents a single todo item with id, task description, and completion status.
    """

    def __init__(self, id: int, title: str, task: Optional[str] = None, description: Optional[str] = None,
                 complete: bool = False, deletion_metadata: Optional[dict] = None,
                 priority: Priority = Priority.MEDIUM, tags: Optional[List[str]] = None,
                 due_date: Optional[str] = None, recurrence: Recurrence = Recurrence.NONE,
                 parent_id: Optional[int] = None):
        """
        Initialize a Todo object.

        Args:
            id (int): Unique identifier for todo
            title (str): Title of task
            task (Optional[str]): Legacy task field (for backward compatibility, mapped to description if provided)
            description (Optional[str]): Detailed description of task
            complete (bool): Completion status, defaults to False
            deletion_metadata (Optional[dict]): Deletion info with 'reason' and 'timestamp', defaults to None
            priority (Priority): Priority level (HIGH, MEDIUM, LOW), defaults to MEDIUM
            tags (Optional[List[str]]): List of tags/categories, defaults to empty list
            due_date (Optional[str]): ISO 8601 datetime string for due date, defaults to None
            recurrence (Recurrence): Recurrence frequency, defaults to NONE
            parent_id (Optional[int]): Parent todo ID for recurring instances, defaults to None
        """
        self.id = id
        self.title = title
        # If description is provided, use it; otherwise use task for backward compatibility
        self.description = description if description is not None else task
        self.task = task  # Keep task for backward compatibility
        self.complete = complete
        self.deletion_metadata = deletion_metadata
        self.priority = priority
        self.tags = tags if tags is not None else []
        self.due_date = due_date
        self.recurrence = recurrence
        self.parent_id = parent_id

    @property
    def is_deleted(self) -> bool:
        """
        Check if this todo is soft-deleted.

        Returns:
            bool: True if deletion_metadata exists, False otherwise
        """
        return self.deletion_metadata is not None

    def mark_deleted(self, reason: str):
        """
        Mark this todo as deleted with given reason.

        Args:
            reason (str): The reason for deletion
        """
        self.deletion_metadata = {
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }

    def restore(self):
        """
        Restore this todo to active status by clearing deletion metadata.
        """
        self.deletion_metadata = None

    def __repr__(self):
        """
        String representation of Todo object.
        """
        return f"Todo(id={self.id}, title='{self.title}', description='{self.description}', complete={self.complete})"

    def __str__(self):
        """
        Human-readable string representation of Todo object.
        """
        status = "Complete" if self.complete else "Incomplete"
        desc = self.description if self.description else "No description"
        return f"ID: {self.id}, Title: {self.title}, Description: {desc}, Status: {status}"

    def to_dict(self):
        """
        Convert the Todo object to a dictionary.

        Returns:
            dict: Dictionary representation of the Todo
        """
        result = {
            "id": self.id,
            "title": self.title,
            "complete": self.complete
        }
        if self.description:
            result["description"] = self.description
        # Keep task for backward compatibility
        if self.task:
            result["task"] = self.task
        if self.deletion_metadata:
            result["deletion_metadata"] = self.deletion_metadata
        if self.priority:
            result["priority"] = self.priority.value
        if self.tags:
            result["tags"] = self.tags
        if self.due_date:
            result["due_date"] = self.due_date
        if self.recurrence and self.recurrence != Recurrence.NONE:
            result["recurrence"] = self.recurrence.value
        if self.parent_id:
            result["parent_id"] = self.parent_id
        return result

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Todo object from a dictionary.

        Args:
            data (dict): Dictionary containing todo data

        Returns:
            Todo: Todo object created from dictionary
        """
        deletion_metadata = data.get("deletion_metadata")
        # Handle backward compatibility: if title is missing, use task as both title and description
        title = data.get("title")
        task = data.get("task")
        description = data.get("description")

        if title is None:
            # Old format: use task as title
            title = task if task else "Untitled"
            description = None  # Don't duplicate task as description

        # Parse priority
        priority_str = data.get("priority", "medium")
        try:
            priority = Priority(priority_str.lower())
        except ValueError:
            priority = Priority.MEDIUM

        # Parse recurrence
        recurrence_str = data.get("recurrence", "none")
        try:
            recurrence = Recurrence(recurrence_str.lower())
        except ValueError:
            recurrence = Recurrence.NONE

        return cls(
            id=data["id"],
            title=title,
            task=task,  # Keep task for backward compatibility
            description=description,
            complete=data["complete"],
            deletion_metadata=deletion_metadata,
            priority=priority,
            tags=data.get("tags", []),
            due_date=data.get("due_date"),
            recurrence=recurrence,
            parent_id=data.get("parent_id")
        )
