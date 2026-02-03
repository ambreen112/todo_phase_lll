"""
Delete/Complete Subagent for handling removal and status changes of todos.
"""

from src.skills.storage_skill import StorageSkill


class DeleteCompleteAgent:
    """
    Handles removal and status changes of todos.
    """

    def __init__(self, storage_skill: StorageSkill):
        """
        Initialize the Delete/Complete agent with required skills.

        Args:
            storage_skill (StorageSkill): Skill for managing the todo list
        """
        self.storage_skill = storage_skill

    def delete_todo(self, todo_id: int, reason: str) -> bool:
        """
        Soft delete a todo by its ID with a reason.

        Args:
            todo_id (int): The ID of the todo to delete
            reason (str): The reason for deletion

        Returns:
            bool: True if successful, False if todo not found
        """
        return self.storage_skill.delete_todo_by_id(todo_id, reason)

    def restore_todo(self, todo_id: int) -> bool:
        """
        Restore a soft-deleted todo by its ID.

        Args:
            todo_id (int): The ID of the todo to restore

        Returns:
            bool: True if successful, False if todo not found or not deleted
        """
        return self.storage_skill.restore_todo_by_id(todo_id)

    def complete_todo(self, todo_id: int) -> bool:
        """
        Mark a todo as complete by its ID.

        Args:
            todo_id (int): The ID of the todo to mark as complete

        Returns:
            bool: True if successful, False if todo not found
        """
        # Get the existing todo
        existing_todo = self.storage_skill.get_todo_by_id(todo_id)
        if not existing_todo:
            return False

        # Create an updated todo with the same details but marked as complete
        from src.models.todo import Todo
        completed_todo = Todo(
            id=existing_todo.id,
            title=existing_todo.title,
            description=existing_todo.description,
            complete=True,
            deletion_metadata=existing_todo.deletion_metadata,
            priority=existing_todo.priority,
            tags=existing_todo.tags,
            due_date=existing_todo.due_date,
            recurrence=existing_todo.recurrence,
            parent_id=existing_todo.parent_id
        )

        # Update the todo in storage
        return self.storage_skill.update_todo_by_id(todo_id, completed_todo)

    def incomplete_todo(self, todo_id: int) -> bool:
        """
        Mark a todo as incomplete by its ID.

        Args:
            todo_id (int): The ID of the todo to mark as incomplete

        Returns:
            bool: True if successful, False if todo not found
        """
        # Get the existing todo
        existing_todo = self.storage_skill.get_todo_by_id(todo_id)
        if not existing_todo:
            return False

        # Create an updated todo with the same details but marked as incomplete
        from src.models.todo import Todo
        incomplete_todo_obj = Todo(
            id=existing_todo.id,
            title=existing_todo.title,
            description=existing_todo.description,
            complete=False,
            deletion_metadata=existing_todo.deletion_metadata,
            priority=existing_todo.priority,
            tags=existing_todo.tags,
            due_date=existing_todo.due_date,
            recurrence=existing_todo.recurrence,
            parent_id=existing_todo.parent_id
        )

        # Update the todo in storage
        return self.storage_skill.update_todo_by_id(todo_id, incomplete_todo_obj)
