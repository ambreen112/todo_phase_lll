"""MCP restore_task tool implementation."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime

from ...deps import get_current_user
from ....core.security import TokenData
from ....models.task import Task
from ....models.database import get_session

router = APIRouter()


@router.post("/restore_task", response_model=dict)
def restore_task(
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Restore a soft-deleted task.

    Args:
        task_id: UUID of the task to restore

    Returns:
        Restored task object
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
                detail=f"Task with ID {task_id} not found or you don't have permission to restore it"
            )

        # Check if task is actually deleted
        if not task.deleted_at:
            raise HTTPException(
                status_code=400,
                detail=f"Task with ID {task_id} is not deleted"
            )

        # Restore task
        task.deleted_at = None
        task.deletion_reason = None
        task.updated_at = datetime.now()

        # Save changes
        db.add(task)
        db.commit()
        db.refresh(task)

        # Format response
        return {
            "id": str(task.id),
            "title": task.title,
            "restored_at": task.updated_at.isoformat(),
            "deleted_at": None,
            "deletion_reason": None,
            "message": f"Task '{task.title}' has been restored",
            "status": "active"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to restore task: {str(e)}")