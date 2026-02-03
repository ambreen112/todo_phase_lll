"""MCP delete_task (soft delete) tool implementation."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import Optional

from ...deps import get_current_user
from ....core.security import TokenData
from ....models.task import Task
from ....models.database import get_session

router = APIRouter()


@router.post("/delete_task", response_model=dict)
def delete_task(
    task_id: UUID,
    deletion_reason: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Soft delete a task (mark as deleted).

    Args:
        task_id: UUID of the task to delete
        deletion_reason: Optional reason for deletion

    Returns:
        Soft deleted task object
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
                detail=f"Task with ID {task_id} not found or you don't have permission to delete it"
            )

        # Check if already deleted
        if task.deleted_at:
            raise HTTPException(
                status_code=400,
                detail=f"Task with ID {task_id} is already deleted"
            )

        # Perform soft delete
        task.deleted_at = datetime.now()
        task.deletion_reason = deletion_reason
        task.updated_at = datetime.now()

        # Save changes
        db.add(task)
        db.commit()
        db.refresh(task)

        # Format response
        return {
            "id": str(task.id),
            "title": task.title,
            "deleted_at": task.deleted_at.isoformat(),
            "deletion_reason": task.deletion_reason,
            "message": f"Task '{task.title}' has been soft deleted",
            "can_restore": True
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")