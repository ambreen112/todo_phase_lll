"""MCP add_task tool implementation."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
import uuid

from ...deps import get_current_user
from ....core.security import TokenData
from ....models.task import Task, TaskPriority
from ....models.database import get_session

router = APIRouter()


@router.post("/add_task", response_model=dict)
def add_task(
    title: str,
    description: Optional[str] = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    due_date: Optional[datetime] = None,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Add a new task for the authenticated user.

    Args:
        title: Task title (required)
        description: Optional task description
        priority: Task priority (HIGH, MEDIUM, LOW)
        due_date: Optional due date

    Returns:
        Created task object
    """
    try:
        # Validate title length
        if len(title) < 1 or len(title) > 256:
            raise HTTPException(
                status_code=400,
                detail="Title must be between 1 and 256 characters"
            )

        # Create new task
        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            owner_id=current_user.user_id
        )

        # Add to database
        db.add(task)
        db.commit()
        db.refresh(task)

        # Return task data
        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat()
        }

    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")