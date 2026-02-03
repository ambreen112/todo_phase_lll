"""Task API routes."""

from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case
from sqlmodel import Session, select, func, and_, or_
from sqlalchemy.sql import column, text

from src.core.security import TokenData
from src.models.database import get_session
from src.models.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskDelete,
    TaskResponse,
    TaskListResponse,
    DeletedTaskListResponse,
    ErrorResponse,
)
from src.models.task import Task, TaskPriority, TaskRecurrence
from src.models.user import User
from src.api.deps import get_current_user, verify_user_owns_resource

router = APIRouter(prefix="/api", tags=["Tasks"])


@router.get(
    "/{user_id}/tasks",
    response_model=TaskListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    },
)
async def list_tasks(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
    include_deleted: bool = Query(False, description="Include soft-deleted tasks"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    tag: Optional[List[str]] = Query(None, description="Filter by tag(s) - can specify multiple times for OR logic", alias="tag"),
    due_status: Optional[str] = Query(None, description="Filter by due status: overdue, due_today, future"),
    search: Optional[str] = Query(None, description="Search in title, description, and tags"),
    sort_by: Optional[str] = Query("created_at", description="Sort by: created_at, due_date, priority, title"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc, desc"),
) -> TaskListResponse:
    """
    List all tasks for a user with filtering, search, and sorting.

    Args:
        user_id: The user's UUID (from path)
        current_user: Authenticated user from JWT
        session: Database session
        include_deleted: Whether to include soft-deleted tasks
        completed: Filter by completion status
        priority: Filter by priority level
        tag: Filter by exact tag match
        due_status: Filter by due status (overdue, due_today, future)
        search: Search term for title, description, and tags
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)

    Returns:
        TaskListResponse with tasks, counts, and statistics

    Raises:
        HTTPException: If user doesn't own the requested resources
    """
    # Verify ownership
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks",
        )

    # Build base query - exclude deleted tasks by default
    query = select(Task).where(Task.owner_id == user_id)

    if not include_deleted:
        query = query.where(Task.deleted_at.is_(None))

    # Apply filters
    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority is not None:
        query = query.where(Task.priority == priority)

    if tag is not None:
        # Use PostgreSQL overlap operator && for OR logic (tasks matching ANY of the tags)
        query = query.where(Task.tags.op('&&')(tag))

    if due_status is not None:
        now = datetime.now(timezone.utc)
        today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

        if due_status == "overdue":
            query = query.where(
                and_(
                    Task.due_date.isnot(None),
                    Task.due_date < now,
                    Task.completed == False
                )
            )
        elif due_status == "due_today":
            tomorrow_start = today_start + timedelta(days=1)
            query = query.where(
                and_(
                    Task.due_date.isnot(None),
                    Task.due_date >= today_start,
                    Task.due_date < tomorrow_start,
                    Task.completed == False
                )
            )
        elif due_status == "future":
            tomorrow_start = today_start + timedelta(days=1)
            query = query.where(
                and_(
                    Task.due_date.isnot(None),
                    Task.due_date >= tomorrow_start,
                    Task.completed == False
                )
            )

    # Apply search
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        query = query.where(
            and_(
                func.lower(Task.title).like(search_term) |
                func.lower(Task.description).like(search_term)
            )
        )

    # Apply sorting
    sort_column = getattr(Task, sort_by, Task.created_at)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Special handling for priority sort: HIGH > MEDIUM > LOW
    if sort_by == "priority":
        priority_order = case(
            (Task.priority == "HIGH", 1),
            (Task.priority == "MEDIUM", 2),
            (Task.priority == "LOW", 3),
            else_=4
        )
        query = query.order_by(priority_order.asc() if sort_order == "asc" else priority_order.desc())

    tasks = session.exec(query).all()

    # Calculate counts
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    overdue_count = sum(1 for t in tasks if t.is_overdue)
    due_today_count = sum(1 for t in tasks if t.is_due_today)

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
        overdue_count=overdue_count,
        due_today_count=due_today_count,
    )


@router.get(
    "/{user_id}/tasks/deleted",
    response_model=DeletedTaskListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    },
)
async def list_deleted_tasks(
    user_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> DeletedTaskListResponse:
    """
    List all soft-deleted tasks for a user.

    Args:
        user_id: The user's UUID (from path)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        DeletedTaskListResponse with deleted tasks

    Raises:
        HTTPException: If user doesn't own the requested resources
    """
    # Verify ownership
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks",
        )

    # Get only soft-deleted tasks
    query = (
        select(Task)
        .where(Task.owner_id == user_id)
        .where(Task.deleted_at.isnot(None))
        .order_by(Task.deleted_at.desc())
    )

    tasks = session.exec(query).all()

    return DeletedTaskListResponse(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
    )


@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
    },
)
async def create_task(
    user_id: UUID,
    request: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Create a new task for a user.

    Args:
        user_id: The user's UUID (from path)
        request: Task creation request
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        TaskResponse with created task

    Raises:
        HTTPException: If user doesn't own the task
    """
    # Verify ownership
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user",
        )

    # Create task with proper enum conversions
    task = Task(
        title=request.title,
        description=request.description,
        priority=TaskPriority(request.priority.upper() if request.priority else "MEDIUM"),
        tags=request.tags,
        due_date=request.due_date,
        recurrence=TaskRecurrence(request.recurrence.upper() if request.recurrence else "NONE"),
        owner_id=user_id,
    )

    session.add(task)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
    session.refresh(task)

    return TaskResponse.model_validate(task)


@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def get_task(
    user_id: UUID,
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
    include_deleted: bool = Query(False, description="Include soft-deleted tasks"),
) -> TaskResponse:
    """
    Get a single task by ID.

    Args:
        user_id: The user's UUID (from path)
        task_id: The task's UUID (from path)
        current_user: Authenticated user from JWT
        session: Database session
        include_deleted: Whether to include soft-deleted tasks

    Returns:
        TaskResponse with task data

    Raises:
        HTTPException: If task not found or not owned by user
    """
    # Verify ownership
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task",
        )

    # Build query
    query = select(Task).where(Task.id == task_id, Task.owner_id == user_id)
    if not include_deleted:
        query = query.where(Task.deleted_at.is_(None))

    task = session.exec(query).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    request: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Update a task.

    Args:
        user_id: The user's UUID (from path)
        task_id: The task's UUID (from path)
        request: Task update request
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        TaskResponse with updated task

    Raises:
        HTTPException: If task not found or not owned by user
    """
    # Verify ownership
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task",
        )

    # Get task (only active tasks can be updated)
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.owner_id == user_id,
            Task.deleted_at.is_(None)
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update fields with proper enum conversion
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "priority" and value is not None:
            value = TaskPriority(value.upper())
        elif field == "recurrence" and value is not None:
            value = TaskRecurrence(value.upper())
        setattr(task, field, value)

    # Update timestamp
    task.updated_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def delete_task(
    user_id: UUID,
    task_id: UUID,
    request: TaskDelete,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Soft delete a task with a reason.

    Args:
        user_id: The user's UUID (from path)
        task_id: The task's UUID (from path)
        request: Delete request with deletion reason
        current_user: Authenticated user from JWT
        session: Database session

    Raises:
        HTTPException: If task not found, not owned by user, or reason missing
    """
    # Verify ownership
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task",
        )

    # Validate deletion reason
    if not request.deletion_reason or not request.deletion_reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deletion reason is required",
        )

    # Get task (only active tasks can be deleted)
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.owner_id == user_id,
            Task.deleted_at.is_(None)
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Soft delete - set deleted_at and deletion_reason
    task.deleted_at = datetime.now(timezone.utc)
    task.deletion_reason = request.deletion_reason.strip()
    task.updated_at = datetime.now(timezone.utc)

    session.commit()


@router.post(
    "/{user_id}/tasks/{task_id}/restore",
    response_model=TaskResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def restore_task(
    user_id: UUID,
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Restore a soft-deleted task.

    Args:
        user_id: The user's UUID (from path)
        task_id: The task's UUID (from path)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        TaskResponse with restored task

    Raises:
        HTTPException: If task not found or not owned by user
    """
    # Verify ownership
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to restore this task",
        )

    # Get soft-deleted task
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.owner_id == user_id,
            Task.deleted_at.isnot(None)
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deleted task not found",
        )

    # Restore - clear deletion metadata
    task.deleted_at = None
    task.deletion_reason = None
    task.updated_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)


@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def toggle_task_complete(
    user_id: UUID,
    task_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TaskResponse:
    """
    Toggle task completion status.

    For recurring tasks, completing the task will:
    1. Mark the current task as complete
    2. Auto-generate the next recurring instance (if recurrence is not NONE)
    3. Link the new instance to the parent via parent_id

    Args:
        user_id: The user's UUID (from path)
        task_id: The task's UUID (from path)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        TaskResponse with updated task

    Raises:
        HTTPException: If task not found or not owned by user
    """
    # Verify ownership
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task",
        )

    # Get task (only active tasks can be completed)
    task = session.exec(
        select(Task).where(
            Task.id == task_id,
            Task.owner_id == user_id,
            Task.deleted_at.is_(None)
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Toggle completion
    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)

    # If completing a recurring task, generate next instance
    if task.completed and task.recurrence != TaskRecurrence.NONE and task.due_date:
        # Calculate next due date based on recurrence
        from datetime import timedelta

        if task.recurrence == TaskRecurrence.DAILY:
            next_due_date = task.due_date + timedelta(days=1)
        elif task.recurrence == TaskRecurrence.WEEKLY:
            next_due_date = task.due_date + timedelta(weeks=1)
        elif task.recurrence == TaskRecurrence.MONTHLY:
            next_due_date = task.due_date + timedelta(days=30)
        else:
            next_due_date = task.due_date

        # Create next instance
        next_task = Task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            tags=task.tags,
            due_date=next_due_date,
            recurrence=task.recurrence,
            parent_id=task.id,  # Link to parent
            owner_id=task.owner_id,
        )
        session.add(next_task)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
    session.refresh(task)

    return TaskResponse.model_validate(task)
