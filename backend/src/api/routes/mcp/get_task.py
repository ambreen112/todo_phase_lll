"""MCP get_task tool implementation."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID

from ...deps import get_current_user
from ....core.security import TokenData
from ....models.task import Task
from ....models.database import get_session

router = APIRouter()


@router.post("/get_task", response_model=dict)
def get_task(
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get a single task by ID for the authenticated user.

    Args:
        task_id: UUID of the task to fetch

    Returns:
        Task object or 404 if not found
    """
    try:
        # Query task owned by current user
        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == current_user.id
        )
        task = db.exec(query).first()

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found or you don't have permission to access it"
            )

        # Format response
        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority.value,
            "tags": task.tags or [],
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "deleted_at": task.deleted_at.isoformat() if task.deleted_at else None,
            "deletion_reason": task.deletion_reason,
            "recurrence": task.recurrence.value,
            "parent_id": str(task.parent_id) if task.parent_id else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "is_overdue": task.is_overdue,
            "is_due_today": task.is_due_today,
            "is_recurring": task.is_recurring
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch task: {str(e)}")