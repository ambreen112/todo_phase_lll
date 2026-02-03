"""
Storage Skill for managing the in-memory todo list.
Provides CRUD operations for todo items.
"""

from typing import List, Optional
from datetime import datetime
from src.models.todo import Todo, Priority


class StorageSkill:
    """
    Manages the in-memory todo list with basic CRUD operations.
    """

    def __init__(self):
        """
        Initialize the storage with an empty list of todos.
        """
        self.todos: List[Todo] = []

    def add_todo(self, todo: Todo) -> bool:
        """
        Add a todo to the list.

        Args:
            todo (Todo): The todo object to add

        Returns:
            bool: True if successful, False otherwise
        """
        self.todos.append(todo)
        return True

    def get_todo_by_id(self, todo_id: int) -> Optional[Todo]:
        """
        Retrieve a todo by its ID.

        Args:
            todo_id (int): The ID of the todo to retrieve

        Returns:
            Optional[Todo]: The todo object if found, None otherwise
        """
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def update_todo_by_id(self, todo_id: int, updated_todo: Todo) -> bool:
        """
        Update a todo by its ID.

        Args:
            todo_id (int): The ID of the todo to update
            updated_todo (Todo): The updated todo object

        Returns:
            bool: True if successful, False if todo not found
        """
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                self.todos[i] = updated_todo
                return True
        return False

    def delete_todo_by_id(self, todo_id: int, reason: str) -> bool:
        """
        Soft delete a todo by its ID with a reason.

        Args:
            todo_id (int): The ID of todo to delete
            reason (str): The reason for deletion

        Returns:
            bool: True if successful, False if todo not found
        """
        todo = self.get_todo_by_id(todo_id)
        if todo:
            todo.mark_deleted(reason)
            return True
        return False

    def get_all_todos(self) -> List[Todo]:
        """
        Get all active (non-deleted) todos in the list.

        Returns:
            List[Todo]: List of all active todo objects
        """
        return [todo for todo in self.todos if not todo.is_deleted]

    def get_deleted_todos(self) -> List[Todo]:
        """
        Get all deleted todos in the list.

        Returns:
            List[Todo]: List of all deleted todo objects
        """
        return [todo for todo in self.todos if todo.is_deleted]

    def restore_todo_by_id(self, todo_id: int) -> bool:
        """
        Restore a soft-deleted todo back to active status.

        Args:
            todo_id (int): The ID of todo to restore

        Returns:
            bool: True if successful, False if todo not found or not deleted
        """
        todo = self.get_todo_by_id(todo_id)
        if todo and todo.is_deleted:
            todo.restore()
            return True
        return False

    def get_overdue_todos(self) -> List[Todo]:
        """
        Get all overdue todos (due date in the past).

        Returns:
            List[Todo]: List of overdue todo objects
        """
        if not hasattr(self, 'todos'):
            return []
        overdue = []
        now = datetime.now()
        for todo in self.todos:
            if todo.due_date and not todo.is_deleted:
                try:
                    due = datetime.fromisoformat(todo.due_date)
                    if due < now:
                        overdue.append(todo)
                except ValueError:
                    pass  # Invalid date format, skip
        return overdue

    def get_due_today_todos(self) -> List[Todo]:
        """
        Get all todos due today.

        Returns:
            List[Todo]: List of todos due today
        """
        if not hasattr(self, 'todos'):
            return []
        due_today = []
        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day)
        today_end = datetime(now.year, now.month, now.day, 23, 59, 59)
        for todo in self.todos:
            if todo.due_date and not todo.is_deleted:
                try:
                    due = datetime.fromisoformat(todo.due_date)
                    if today_start <= due <= today_end:
                        due_today.append(todo)
                except ValueError:
                    pass  # Invalid date format, skip
        return due_today

    def get_by_parent_id(self, parent_id: int) -> List[Todo]:
        """
        Get all todos with a given parent ID (for recurring instances).

        Args:
            parent_id (int): The parent todo ID

        Returns:
            List[Todo]: List of todos with matching parent_id
        """
        if not hasattr(self, 'todos'):
            return []
        return [todo for todo in self.todos if todo.parent_id == parent_id]