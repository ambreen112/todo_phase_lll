"""
Add/Update Subagent for handling creating and editing todos.
"""

from typing import Optional
from src.models.todo import Todo, Priority, Recurrence
from src.skills.storage_skill import StorageSkill
from src.skills.id_generator_skill import IDGeneratorSkill


class AddUpdateAgent:
    """
    Handles creating and editing todos.
    """

    def __init__(self, storage_skill: StorageSkill, id_generator_skill: IDGeneratorSkill):
        """
        Initialize the Add/Update agent with required skills.

        Args:
            storage_skill (StorageSkill): Skill for managing the todo list
            id_generator_skill (IDGeneratorSkill): Skill for generating IDs
        """
        self.storage_skill = storage_skill
        self.id_generator_skill = id_generator_skill

    def add_task(self, title: str, description: Optional[str] = None,
                priority: Optional[Priority] = None, tags: Optional[list] = None,
                due_date: Optional[str] = None, recurrence: Optional[Recurrence] = None) -> Optional[Todo]:
        """
        Create a new todo with the provided fields.

        Args:
            title (str): The title of the todo
            description (Optional[str]): The description of the todo
            priority (Optional[Priority]): The priority level
            tags (Optional[list]): List of tags
            due_date (Optional[str]): ISO 8601 datetime string
            recurrence (Optional[Recurrence]): Recurrence frequency

        Returns:
            Optional[Todo]: The created todo object if successful, None if title is empty
        """
        if not title or not title.strip():
            return None

        # Generate a new ID
        new_id = self.id_generator_skill.generate_next_id()

        # Create a new todo with the generated ID
        new_todo = Todo(
            id=new_id,
            title=title.strip(),
            description=description.strip() if description else None,
            priority=priority if priority else Priority.MEDIUM,
            tags=tags if tags else [],
            due_date=due_date,
            recurrence=recurrence if recurrence else Recurrence.NONE
        )

        # Add the todo to storage
        if self.storage_skill.add_todo(new_todo):
            return new_todo
        else:
            # If adding failed, we should decrement the ID counter
            # In a real implementation, we might need to handle this differently
            return None

    def update_task(self, todo_id: int, new_title: Optional[str] = None,
                  priority: Optional[Priority] = None, tags: Optional[list] = None,
                  due_date: Optional[str] = None, recurrence: Optional[Recurrence] = None) -> bool:
        """
        Update an existing todo's fields.

        Args:
            todo_id (int): The ID of the todo to update
            new_title (Optional[str]): The new title (None means keep existing)
            priority (Optional[Priority]): The new priority (None means keep existing)
            tags (Optional[list]): The new tags (None means keep existing)
            due_date (Optional[str]): The new due date (None means keep existing)
            recurrence (Optional[Recurrence]): The new recurrence (None means keep existing)

        Returns:
            bool: True if successful, False if todo not found or title is empty when changing
        """
        # Get the existing todo
        existing_todo = self.storage_skill.get_todo_by_id(todo_id)
        if not existing_todo:
            return False

        # If title is being updated, validate it
        if new_title is not None and (not new_title or not new_title.strip()):
            return False

        # Use existing values if new ones not provided
        final_title = new_title.strip() if new_title else existing_todo.title
        final_priority = priority if priority else existing_todo.priority
        final_tags = tags if tags is not None else existing_todo.tags
        final_due_date = due_date if due_date is not None else existing_todo.due_date
        final_recurrence = recurrence if recurrence is not None else existing_todo.recurrence

        # Create an updated todo with the same ID but new values
        updated_todo = Todo(
            id=existing_todo.id,
            title=final_title,
            description=existing_todo.description,
            complete=existing_todo.complete,
            deletion_metadata=existing_todo.deletion_metadata,
            priority=final_priority,
            tags=final_tags,
            due_date=final_due_date,
            recurrence=final_recurrence,
            parent_id=existing_todo.parent_id
        )

        # Update the todo in storage
        return self.storage_skill.update_todo_by_id(todo_id, updated_todo)
