"""MCP complete_task (toggle) tool implementation."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime

from ...deps import get_current_user
from ....core.security import TokenData
from ....models.task import Task
from ....models.database import get_session

router = APIRouter()


@router.post("/complete_task", response_model=dict)
def complete_task(
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Toggle completion status of a task.

    Args:
        task_id: UUID of the task to toggle completion

    Returns:
        Task with updated completion status
    """
    try:
        # Fetch task owned by current user
        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == current_user.user_id,
            Task.deleted_at.is_(None)  # Don't toggle completion on deleted tasks
        )
        task = db.exec(query).first()

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found, you don't have permission, or it's deleted"
            )

        # Toggle completion status
        new_status = not task.completed
        task.completed = new_status
        task.updated_at = datetime.now()

        # Save changes
        db.add(task)
        db.commit()
        db.refresh(task)

        # Format response
        return {
            "id": str(task.id),
            "title": task.title,
            "completed": task.completed,
            "status": "completed" if task.completed else "incomplete",
            "updated_at": task.updated_at.isoformat(),
            "message": f"Task '{task.title}' marked as {'completed' if task.completed else 'incomplete'}"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to toggle task completion: {str(e)}")