"""Tool executor for MCP tools - executes tools with user_id injection."""

import json
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select, and_, or_

from ..models.task import Task, TaskPriority
from ..models.database import get_session


def get_week_bounds() -> tuple[datetime, datetime]:
    """Get start (Monday) and end (Sunday) of current week."""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)  # Sunday end
    return start_of_week, end_of_week


def get_today_bounds() -> tuple[datetime, datetime]:
    """Get start and end of today."""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = today + timedelta(hours=23, minutes=59, seconds=59)
    return today, end_of_today

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes MCP tools with user_id context."""

    def __init__(self, user_id: str):
        """
        Initialize tool executor with user context.

        Args:
            user_id: UUID of the authenticated user (injected server-side)
        """
        self.user_id = UUID(user_id)

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name with given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments (from LLM)

        Returns:
            Tool execution result as dict
        """
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")

        tool_map = {
            "add_task": self._add_task,
            "list_tasks": self._list_tasks,
            "get_task": self._get_task,
            "update_task": self._update_task,
            "delete_task": self._delete_task,
            "restore_task": self._restore_task,
            "complete_task": self._complete_task,
        }

        if tool_name not in tool_map:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            # Get a fresh session for this execution
            session_gen = get_session()
            session = next(session_gen)
            try:
                result = tool_map[tool_name](session, arguments)
                return result
            finally:
                try:
                    next(session_gen)
                except StopIteration:
                    pass
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return {"error": str(e)}

    def _add_task(self, db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new task."""
        title = args.get("title", "").strip()
        if not title or len(title) > 256:
            return {"error": "Title must be between 1 and 256 characters"}

        description = args.get("description")
        priority_str = args.get("priority", "MEDIUM").upper()
        due_date_str = args.get("due_date")
        tags_input = args.get("tags")

        # Parse tags - handle both array and string formats
        tags: Optional[List[str]] = None
        if tags_input:
            if isinstance(tags_input, list):
                tags = [str(t).strip() for t in tags_input if t]
            elif isinstance(tags_input, str):
                # Handle string format like "['food', 'weekly']" or "food, weekly"
                tags_str = tags_input.strip()
                if tags_str.startswith("[") and tags_str.endswith("]"):
                    try:
                        tags = json.loads(tags_str.replace("'", '"'))
                    except json.JSONDecodeError:
                        # Try parsing as comma-separated
                        tags = [t.strip().strip("'\"") for t in tags_str[1:-1].split(",") if t.strip()]
                else:
                    # Comma-separated string
                    tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        try:
            priority = TaskPriority(priority_str)
        except ValueError:
            priority = TaskPriority.MEDIUM

        # Parse due date - handle multiple formats
        due_date = None
        if due_date_str:
            try:
                # Try ISO format first
                due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
            except ValueError:
                try:
                    # Try simple date format YYYY-MM-DD
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except ValueError:
                    pass

        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags,
            owner_id=self.user_id
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority.value,
            "tags": task.tags or [],
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "message": f"Task '{task.title}' created successfully"
        }

    def _list_tasks(self, db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """List tasks with optional filters."""
        filters = args.get("filters", {})

        query = select(Task).where(Task.owner_id == self.user_id)

        # Apply filters
        if "completed" in filters:
            query = query.where(Task.completed == filters["completed"])

        if "deleted" in filters:
            if filters["deleted"]:
                query = query.where(Task.deleted_at.isnot(None))
            else:
                query = query.where(Task.deleted_at.is_(None))
        else:
            # Default: don't show deleted tasks
            query = query.where(Task.deleted_at.is_(None))

        if "priority" in filters:
            try:
                priority = TaskPriority(filters["priority"].upper())
                query = query.where(Task.priority == priority)
            except ValueError:
                pass

        # Search filter - searches in title and description (case-insensitive)
        if "search" in filters and filters["search"]:
            search_term = filters["search"].lower()
            query = query.where(
                or_(
                    Task.title.ilike(f"%{search_term}%"),
                    Task.description.ilike(f"%{search_term}%")
                )
            )

        # Tag filter - only used when explicitly filtering by tag
        if "tag" in filters and filters["tag"]:
            query = query.where(Task.tags.contains([filters["tag"]]))

        # Date filters
        if "due_today" in filters and filters["due_today"]:
            start_of_today, end_of_today = get_today_bounds()
            query = query.where(
                and_(
                    Task.due_date >= start_of_today,
                    Task.due_date <= end_of_today
                )
            )

        if "due_this_week" in filters and filters["due_this_week"]:
            start_of_week, end_of_week = get_week_bounds()
            query = query.where(
                and_(
                    Task.due_date >= start_of_week,
                    Task.due_date <= end_of_week
                )
            )

        if "due_before" in filters and filters["due_before"]:
            try:
                due_before = datetime.fromisoformat(filters["due_before"].replace("Z", "+00:00"))
                query = query.where(Task.due_date < due_before)
            except ValueError:
                pass

        if "due_after" in filters and filters["due_after"]:
            try:
                due_after = datetime.fromisoformat(filters["due_after"].replace("Z", "+00:00"))
                query = query.where(Task.due_date > due_after)
            except ValueError:
                pass

        if "overdue" in filters and filters["overdue"]:
            now = datetime.now(timezone.utc)
            query = query.where(
                and_(
                    Task.due_date < now,
                    Task.completed == False
                )
            )

        tasks = db.exec(query).all()

        task_list = []
        for task in tasks:
            task_list.append({
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "priority": task.priority.value,
                "tags": task.tags or [],
                "due_date": task.due_date.isoformat() if task.due_date else None,
            })

        return {"tasks": task_list, "count": len(task_list)}

    def _get_task(self, db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get a single task by ID."""
        task_id_str = args.get("task_id")
        if not task_id_str:
            return {"error": "task_id is required"}

        try:
            task_id = UUID(task_id_str)
        except ValueError:
            return {"error": "Invalid task_id format"}

        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == self.user_id
        )
        task = db.exec(query).first()

        if not task:
            return {"error": f"Task with ID {task_id} not found"}

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority.value,
            "tags": task.tags or [],
            "due_date": task.due_date.isoformat() if task.due_date else None,
        }

    def _update_task(self, db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task."""
        task_id_str = args.get("task_id")
        if not task_id_str:
            return {"error": "task_id is required"}

        try:
            task_id = UUID(task_id_str)
        except ValueError:
            return {"error": "Invalid task_id format"}

        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == self.user_id
        )
        task = db.exec(query).first()

        if not task:
            return {"error": f"Task with ID {task_id} not found"}

        # Update fields if provided
        if "title" in args:
            title = args["title"].strip()
            if not title or len(title) > 256:
                return {"error": "Title must be between 1 and 256 characters"}
            task.title = title

        if "description" in args:
            task.description = args["description"]

        if "priority" in args:
            try:
                task.priority = TaskPriority(args["priority"].upper())
            except ValueError:
                pass

        if "completed" in args:
            task.completed = bool(args["completed"])

        if "tags" in args:
            task.tags = args["tags"]

        if "due_date" in args:
            due_date_str = args["due_date"]
            if due_date_str:
                try:
                    task.due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
                except ValueError:
                    pass
            else:
                task.due_date = None

        task.updated_at = datetime.now()
        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority.value,
            "tags": task.tags or [],
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "message": f"Task '{task.title}' updated successfully"
        }

    def _delete_task(self, db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Soft delete a task."""
        task_id_str = args.get("task_id")
        if not task_id_str:
            return {"error": "task_id is required"}

        try:
            task_id = UUID(task_id_str)
        except ValueError:
            return {"error": "Invalid task_id format"}

        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == self.user_id
        )
        task = db.exec(query).first()

        if not task:
            return {"error": f"Task with ID {task_id} not found"}

        if task.deleted_at:
            return {"error": f"Task is already deleted"}

        task.deleted_at = datetime.now()
        task.deletion_reason = args.get("reason")
        task.updated_at = datetime.now()
        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "deleted_at": task.deleted_at.isoformat(),
            "message": f"Task '{task.title}' deleted successfully"
        }

    def _restore_task(self, db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Restore a soft-deleted task."""
        task_id_str = args.get("task_id")
        if not task_id_str:
            return {"error": "task_id is required"}

        try:
            task_id = UUID(task_id_str)
        except ValueError:
            return {"error": "Invalid task_id format"}

        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == self.user_id
        )
        task = db.exec(query).first()

        if not task:
            return {"error": f"Task with ID {task_id} not found"}

        if not task.deleted_at:
            return {"error": f"Task is not deleted"}

        task.deleted_at = None
        task.deletion_reason = None
        task.updated_at = datetime.now()
        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "message": f"Task '{task.title}' restored successfully"
        }

    def _complete_task(self, db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Toggle task completion status."""
        task_id_str = args.get("task_id")
        if not task_id_str:
            return {"error": "task_id is required"}

        try:
            task_id = UUID(task_id_str)
        except ValueError:
            return {"error": "Invalid task_id format"}

        query = select(Task).where(
            Task.id == task_id,
            Task.owner_id == self.user_id,
            Task.deleted_at.is_(None)
        )
        task = db.exec(query).first()

        if not task:
            return {"error": f"Task with ID {task_id} not found or is deleted"}

        task.completed = not task.completed
        task.updated_at = datetime.now()
        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "id": str(task.id),
            "title": task.title,
            "completed": task.completed,
            "message": f"Task '{task.title}' marked as {'completed' if task.completed else 'incomplete'}"
        }
