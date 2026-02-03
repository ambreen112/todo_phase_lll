"""MCP update_task tool implementation."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
from typing import Optional
from datetime import datetime

from ...deps import get_current_user
from ....core.security import TokenData
from ....models.task import Task, TaskPriority
from ....models.database import get_session

router = APIRouter()


@router.post("/update_task", response_model=dict)
def update_task(
    task_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[TaskPriority] = None,
    completed: Optional[bool] = None,
    due_date: Optional[datetime] = None,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Update fields for a single task.

    Args:
        task_id: UUID of the task to update
        title: New task title
        description: New task description
        priority: New priority
        completed: Completion status
        due_date: New due date

    Returns:
        Updated task object
    """
    try:
        # Fetch task owned by current user
        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == current_user.user_id
        )
        task = db.exec(query).first()

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found or you don't have permission to update it"
            )

        # Validate title length if provided
        if title is not None:
            if len(title) < 1 or len(title) > 256:
                raise HTTPException(
                    status_code=400,
                    detail="Title must be between 1 and 256 characters"
                )
            task.title = title

        # Update other fields if provided
        if description is not None:
            task.description = description

        if priority is not None:
            task.priority = priority

        if completed is not None:
            task.completed = completed

        if due_date is not None:
            task.due_date = due_date

        # Update timestamp
        task.updated_at = datetime.now()

        # Save changes
        db.add(task)
        db.commit()
        db.refresh(task)

        # Format response
        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "updated_at": task.updated_at.isoformat(),
            "changes": {
                "title_changed": title is not None,
                "description_changed": description is not None,
                "priority_changed": priority is not None,
                "completed_changed": completed is not None,
                "due_date_changed": due_date is not None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")