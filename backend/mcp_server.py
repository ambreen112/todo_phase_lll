#!/usr/bin/env python3
"""
MCP Server for Todo App - Claude Code Integration

This MCP server exposes task management tools for the Todo app backend.
It connects directly to the PostgreSQL database and provides:
- list_tasks: List user's tasks with optional filters
- create_task: Create a new task
- get_task: Get a single task by ID
- update_task: Update task fields
- delete_task: Soft delete a task
- restore_task: Restore a soft-deleted task
- complete_task: Toggle task completion

Usage:
    python mcp_server.py

Environment Variables Required:
    DATABASE_URL: PostgreSQL connection string
    MCP_USER_ID: User ID to scope all operations (required)
"""

import os
import sys
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session, select, create_engine

# Import models
from models.task import Task, TaskPriority, TaskRecurrence
from models.user import User

# Create MCP server
mcp = FastMCP("todo-app")

# Database configuration
def get_database_url() -> str:
    """Get database URL from environment."""
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise ValueError("DATABASE_URL environment variable is required")
    # Convert to psycopg3 driver format
    if "postgresql://" in url and "postgresql+psycopg://" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://")
    return url

def get_engine():
    """Create database engine."""
    return create_engine(
        get_database_url(),
        echo=False,
        pool_pre_ping=True,
    )

def get_user_id() -> UUID:
    """Get user ID from environment."""
    user_id = os.environ.get("MCP_USER_ID", "")
    if not user_id:
        raise ValueError("MCP_USER_ID environment variable is required")
    return UUID(user_id)

def task_to_dict(task: Task) -> dict:
    """Convert Task model to dictionary."""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority.value,
        "tags": task.tags or [],
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "recurrence": task.recurrence.value,
        "is_deleted": task.deleted_at is not None,
        "deleted_at": task.deleted_at.isoformat() if task.deleted_at else None,
        "deletion_reason": task.deletion_reason,
        "is_overdue": task.is_overdue,
        "is_due_today": task.is_due_today,
        "is_recurring": task.is_recurring,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


@mcp.tool()
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    include_deleted: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """
    List tasks for the authenticated user with optional filters.

    Args:
        status: Filter by status - 'active', 'completed', or 'all' (default: 'active')
        priority: Filter by priority - 'HIGH', 'MEDIUM', or 'LOW'
        search: Search in title and description
        include_deleted: Include soft-deleted tasks (default: False)
        limit: Maximum number of tasks to return (default: 50)
        offset: Number of tasks to skip (default: 0)

    Returns:
        Dictionary with 'success', 'tasks' list, and 'total' count
    """
    try:
        user_id = get_user_id()
        engine = get_engine()

        with Session(engine) as session:
            # Base query
            query = select(Task).where(Task.owner_id == user_id)

            # Filter by deletion status
            if not include_deleted:
                query = query.where(Task.deleted_at.is_(None))

            # Filter by status
            if status == "completed":
                query = query.where(Task.completed == True)
            elif status == "active":
                query = query.where(Task.completed == False)
            # 'all' or None means no status filter

            # Filter by priority
            if priority:
                try:
                    priority_enum = TaskPriority(priority.upper())
                    query = query.where(Task.priority == priority_enum)
                except ValueError:
                    return {"success": False, "error": f"Invalid priority: {priority}. Use HIGH, MEDIUM, or LOW."}

            # Search filter
            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    (Task.title.ilike(search_pattern)) |
                    (Task.description.ilike(search_pattern))
                )

            # Get total count before pagination
            count_query = select(Task).where(Task.owner_id == user_id)
            if not include_deleted:
                count_query = count_query.where(Task.deleted_at.is_(None))
            total = len(session.exec(count_query).all())

            # Apply pagination
            query = query.offset(offset).limit(limit)

            # Execute
            tasks = session.exec(query).all()

            return {
                "success": True,
                "tasks": [task_to_dict(t) for t in tasks],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "MEDIUM",
    due_date: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """
    Create a new task.

    Args:
        title: Task title (required, max 256 chars)
        description: Task description (optional, max 2000 chars)
        priority: Task priority - 'HIGH', 'MEDIUM', or 'LOW' (default: 'MEDIUM')
        due_date: Due date in ISO format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
        tags: List of tags (optional)

    Returns:
        Dictionary with 'success' and created 'task' object
    """
    try:
        user_id = get_user_id()
        engine = get_engine()

        # Validate title
        if not title or len(title.strip()) == 0:
            return {"success": False, "error": "Title is required"}
        if len(title) > 256:
            return {"success": False, "error": "Title must be 256 characters or less"}

        # Validate description
        if description and len(description) > 2000:
            return {"success": False, "error": "Description must be 2000 characters or less"}

        # Validate priority
        try:
            priority_enum = TaskPriority(priority.upper())
        except ValueError:
            return {"success": False, "error": f"Invalid priority: {priority}. Use HIGH, MEDIUM, or LOW."}

        # Parse due date
        parsed_due_date = None
        if due_date:
            try:
                # Try ISO format with time
                if "T" in due_date:
                    parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                else:
                    # Date only - set to end of day
                    parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d").replace(
                        hour=23, minute=59, second=59, tzinfo=timezone.utc
                    )
            except ValueError:
                return {"success": False, "error": f"Invalid due_date format: {due_date}. Use YYYY-MM-DD or ISO format."}

        with Session(engine) as session:
            task = Task(
                title=title.strip(),
                description=description.strip() if description else None,
                priority=priority_enum,
                due_date=parsed_due_date,
                tags=tags,
                owner_id=user_id,
                completed=False,
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task": task_to_dict(task),
                "message": f"Task '{title}' created successfully",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_task(task_id: str) -> dict:
    """
    Get a single task by ID.

    Args:
        task_id: UUID of the task

    Returns:
        Dictionary with 'success' and 'task' object
    """
    try:
        user_id = get_user_id()
        engine = get_engine()

        # Validate UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return {"success": False, "error": f"Invalid task_id format: {task_id}"}

        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_uuid, Task.owner_id == user_id)
            ).first()

            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}

            return {
                "success": True,
                "task": task_to_dict(task),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: Optional[list[str]] = None,
    completed: Optional[bool] = None,
) -> dict:
    """
    Update task fields. Only provided fields will be updated.

    Args:
        task_id: UUID of the task to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority - 'HIGH', 'MEDIUM', or 'LOW' (optional)
        due_date: New due date in ISO format (optional)
        tags: New tags list (optional)
        completed: New completion status (optional)

    Returns:
        Dictionary with 'success' and updated 'task' object
    """
    try:
        user_id = get_user_id()
        engine = get_engine()

        # Validate UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return {"success": False, "error": f"Invalid task_id format: {task_id}"}

        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_uuid, Task.owner_id == user_id)
            ).first()

            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}

            if task.deleted_at:
                return {"success": False, "error": f"Task {task_id} is deleted. Restore it first."}

            # Update fields
            if title is not None:
                if len(title.strip()) == 0:
                    return {"success": False, "error": "Title cannot be empty"}
                if len(title) > 256:
                    return {"success": False, "error": "Title must be 256 characters or less"}
                task.title = title.strip()

            if description is not None:
                if len(description) > 2000:
                    return {"success": False, "error": "Description must be 2000 characters or less"}
                task.description = description.strip() if description else None

            if priority is not None:
                try:
                    task.priority = TaskPriority(priority.upper())
                except ValueError:
                    return {"success": False, "error": f"Invalid priority: {priority}. Use HIGH, MEDIUM, or LOW."}

            if due_date is not None:
                try:
                    if due_date == "":
                        task.due_date = None
                    elif "T" in due_date:
                        task.due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    else:
                        task.due_date = datetime.strptime(due_date, "%Y-%m-%d").replace(
                            hour=23, minute=59, second=59, tzinfo=timezone.utc
                        )
                except ValueError:
                    return {"success": False, "error": f"Invalid due_date format: {due_date}"}

            if tags is not None:
                task.tags = tags

            if completed is not None:
                task.completed = completed

            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task": task_to_dict(task),
                "message": f"Task '{task.title}' updated successfully",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_task(task_id: str, reason: Optional[str] = None) -> dict:
    """
    Soft delete a task (marks as deleted but preserves data).

    Args:
        task_id: UUID of the task to delete
        reason: Reason for deletion (optional)

    Returns:
        Dictionary with 'success' and deletion confirmation
    """
    try:
        user_id = get_user_id()
        engine = get_engine()

        # Validate UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return {"success": False, "error": f"Invalid task_id format: {task_id}"}

        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_uuid, Task.owner_id == user_id)
            ).first()

            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}

            if task.deleted_at:
                return {"success": False, "error": f"Task {task_id} is already deleted"}

            task.deleted_at = datetime.now(timezone.utc)
            task.deletion_reason = reason
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()

            return {
                "success": True,
                "message": f"Task '{task.title}' deleted successfully",
                "task_id": str(task.id),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def restore_task(task_id: str) -> dict:
    """
    Restore a soft-deleted task.

    Args:
        task_id: UUID of the task to restore

    Returns:
        Dictionary with 'success' and restored 'task' object
    """
    try:
        user_id = get_user_id()
        engine = get_engine()

        # Validate UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return {"success": False, "error": f"Invalid task_id format: {task_id}"}

        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_uuid, Task.owner_id == user_id)
            ).first()

            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}

            if not task.deleted_at:
                return {"success": False, "error": f"Task {task_id} is not deleted"}

            task.deleted_at = None
            task.deletion_reason = None
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task": task_to_dict(task),
                "message": f"Task '{task.title}' restored successfully",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def complete_task(task_id: str) -> dict:
    """
    Toggle task completion status.

    Args:
        task_id: UUID of the task

    Returns:
        Dictionary with 'success', 'task' object, and 'was_completed' status
    """
    try:
        user_id = get_user_id()
        engine = get_engine()

        # Validate UUID
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            return {"success": False, "error": f"Invalid task_id format: {task_id}"}

        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_uuid, Task.owner_id == user_id)
            ).first()

            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}

            if task.deleted_at:
                return {"success": False, "error": f"Task {task_id} is deleted. Restore it first."}

            was_completed = task.completed
            task.completed = not task.completed
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
            session.refresh(task)

            status_msg = "completed" if task.completed else "marked as incomplete"
            return {
                "success": True,
                "task": task_to_dict(task),
                "was_completed": was_completed,
                "message": f"Task '{task.title}' {status_msg}",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run()
