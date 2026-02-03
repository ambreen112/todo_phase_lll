"""MCP list_tasks tool implementation."""

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, and_, col
from typing import Optional
from datetime import datetime

from ...deps import get_current_user
from ....core.security import TokenData
from ....models.task import Task, TaskPriority
from ....models.database import get_session

router = APIRouter()


@router.post("/list_tasks", response_model=dict)
def list_tasks(
    completed: Optional[bool] = None,
    deleted: Optional[bool] = None,
    priority: Optional[TaskPriority] = None,
    tag: Optional[str] = None,
    due_before: Optional[datetime] = None,
    overdue: Optional[bool] = None,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    List tasks for the authenticated user with optional filters.

    Args:
        completed: Filter by completion status
        deleted: Filter by deletion status
        priority: Filter by priority
        tag: Filter by tag (supports JSON arrays like ["tag1", "tag2"])
        due_before: Filter tasks due before this date
        overdue: Filter for overdue tasks

    Returns:
        List of task objects with filter summary
    """
    try:
        # Base query - only tasks owned by current user
        query = select(Task).where(Task.owner_id == current_user.user_id)

        # Apply filters
        if completed is not None:
            query = query.where(Task.completed == completed)

        if deleted is not None:
            if deleted:
                query = query.where(Task.deleted_at.isnot(None))
            else:
                query = query.where(Task.deleted_at.is_(None))

        if priority is not None:
            query = query.where(Task.priority == priority)

        if tag is not None:
            # Parse JSON arrays (e.g., ["work", "new"]) from tag parameter
            if tag.strip().startswith('['):
                try:
                    tag_list = json.loads(tag)
                    if isinstance(tag_list, list) and tag_list:
                        # Match ANY of the tags from the array using PostgreSQL array overlap operator
                        query = query.where(Task.tags.op('&&')(tag_list))
                except json.JSONDecodeError:
                    # Fallback: treat as single tag
                    if tag.strip() != '':
                        query = query.where(Task.tags.op('&&')([tag]))
            else:
                # Single tag filter
                if tag.strip() != '':
                    query = query.where(Task.tags.op('&&')([tag]))

        if due_before is not None:
            query = query.where(Task.due_date <= due_before)

        if overdue is not None:
            now_utc = datetime.now()
            if overdue:
                # Overdue tasks: due_date < now AND completed = False AND deleted_at is null
                query = query.where(
                    and_(
                        Task.due_date < now_utc,
                        Task.completed == False,
                        Task.deleted_at.is_(None)
                    )
                )
            else:
                # Not overdue: either due_date >= now OR completed = True OR deleted_at is not null
                query = query.where(
                    or_(
                        Task.due_date >= now_utc,
                        Task.completed == True,
                        Task.deleted_at.isnot(None)
                    )
                )

        # Execute query
        tasks = db.exec(query).all()

        # Format response
        task_list = []
        for task in tasks:
            task_data = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "tags": task.tags or [],
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "deleted_at": task.deleted_at.isoformat() if task.deleted_at else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            task_list.append(task_data)

        return {
            "tasks": task_list,
            "count": len(task_list),
            "filters": {
                "completed": completed,
                "deleted": deleted,
                "priority": priority.value if priority else None,
                "tag": tag,
                "due_before": due_before.isoformat() if due_before else None,
                "overdue": overdue
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")
