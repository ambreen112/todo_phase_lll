"""
List/Search Subagent for handling displaying and querying todos.
"""

from typing import List, Optional
from src.models.todo import Todo, Priority
from src.skills.storage_skill import StorageSkill
from src.skills.formatter_skill import FormatterSkill


class ListSearchAgent:
    """
    Handles displaying and querying todos.
    """

    def __init__(self, storage_skill: StorageSkill, formatter_skill: FormatterSkill):
        """
        Initialize the List/Search agent with required skills.

        Args:
            storage_skill (StorageSkill): Skill for managing the todo list
            formatter_skill (FormatterSkill): Skill for formatting output
        """
        self.storage_skill = storage_skill
        self.formatter_skill = formatter_skill

    def list_all_todos(self, filter_priority: Optional[Priority] = None,
                      filter_tag: Optional[str] = None,
                      filter_status: Optional[str] = None,
                      sort_by: Optional[str] = None) -> str:
        """
        Get and format all todos for display with optional filtering and sorting.

        Args:
            filter_priority (Optional[Priority]): Filter by priority level
            filter_tag (Optional[str]): Filter by tag
            filter_status (Optional[str]): Filter by status (complete/incomplete)
            sort_by (Optional[str]): Sort order (id/priority/title/status)

        Returns:
            str: Formatted string of all todos
        """
        todos = self.storage_skill.get_all_todos()

        # Apply filters
        if filter_priority:
            todos = [t for t in todos if t.priority == filter_priority]
        if filter_tag:
            todos = [t for t in todos if filter_tag.lower() in [tag.lower() for tag in t.tags]]
        if filter_status:
            if filter_status == "complete":
                todos = [t for t in todos if t.complete]
            elif filter_status == "incomplete":
                todos = [t for t in todos if not t.complete]

        # Apply sorting
        if sort_by:
            todos = self.sort_todos(todos, sort_by)

        return self.formatter_skill.format_todo_list(todos)

    def sort_todos(self, todos: List[Todo], sort_by: str) -> List[Todo]:
        """
        Sort todos by specified field.

        Args:
            todos (List[Todo]): List of todos to sort
            sort_by (str): Sort field (id/priority/title/status)

        Returns:
            List[Todo]: Sorted list of todos
        """
        if sort_by == "id":
            return sorted(todos, key=lambda t: t.id)
        elif sort_by == "priority":
            # Priority order: HIGH → MEDIUM → LOW
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            return sorted(todos, key=lambda t: priority_order[t.priority])
        elif sort_by == "title":
            return sorted(todos, key=lambda t: t.title.lower())
        elif sort_by == "status":
            # Complete first, then incomplete
            return sorted(todos, key=lambda t: not t.complete)
        else:
            return todos  # No sorting

    def search_todos(self, query: str) -> str:
        """
        Find todos that match the search query.

        Args:
            query (str): The search query string

        Returns:
            str: Formatted string of matching todos
        """
        all_todos = self.storage_skill.get_all_todos()
        if not query:
            return self.formatter_skill.format_todo_list(all_todos)

        query_lower = query.lower()
        matching_todos = []

        for todo in all_todos:
            # Search in title, description, and tags
            if (query_lower in todo.title.lower() or
                (todo.description and query_lower in todo.description.lower()) or
                any(query_lower in tag.lower() for tag in todo.tags)):
                matching_todos.append(todo)

        if not matching_todos:
            return "No matching todos found."
        return self.formatter_skill.format_todo_list(matching_todos)

    def list_deleted_todos(self) -> str:
        """
        Get and format all deleted todos for display.

        Returns:
            str: Formatted string of all deleted todos with reasons
        """
        todos = self.storage_skill.get_deleted_todos()
        return self.formatter_skill.format_deleted_list(todos)

    def get_overdue_todos(self) -> List[Todo]:
        """
        Get all overdue todos.

        Returns:
            List[Todo]: List of overdue todo objects
        """
        return self.storage_skill.get_overdue_todos()

    def get_due_today_todos(self) -> List[Todo]:
        """
        Get all todos due today.

        Returns:
            List[Todo]: List of todos due today
        """
        return self.storage_skill.get_due_today_todos()
