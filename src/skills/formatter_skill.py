"""
Formatter Skill for pretty-printing todo lists.
"""

from typing import List
from src.models.todo import Todo, Priority, Recurrence
from datetime import datetime


class FormatterSkill:
    """
    Formats todo lists and individual todos for display.
    """

    def format_todo_list(self, todos: List[Todo]) -> str:
        """
        Format a list of todos for display.

        Args:
            todos (List[Todo]): List of todo objects to format

        Returns:
            str: Formatted string showing all todos in a table format
        """
        if not todos:
            return "No todos found."

        # Create table header
        header = f"{'ID':<3} | {'Pri':<4} | {'Title':<20} | {'Tags':<15} | {'Due':<12} | {'Status':<9}"
        separator = "-" * len(header)
        result = [header, separator]

        # Add each todo as a row
        for todo in todos:
            # Priority indicator
            pri_sym = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}.get(todo.priority, "")
            pri_str = f"{pri_sym} {str(todo.priority)[:2]}" if pri_sym else str(todo.priority)[:3]

            # Title (truncated)
            title = todo.title[:17] + "..." if len(todo.title) > 20 else todo.title

            # Tags (comma-separated, truncated)
            tags_str = ", ".join(todo.tags)[:13] + "..." if todo.tags and len(", ".join(todo.tags)) > 15 else (", ".join(todo.tags) or "")

            # Due date with urgency indicators
            due_str = ""
            if todo.due_date:
                try:
                    due = datetime.fromisoformat(todo.due_date)
                    now = datetime.now()
                    today_start = datetime(now.year, now.month, now.day)
                    today_end = datetime(now.year, now.month, now.day, 23, 59, 59)

                    if due < now:
                        due_str = f"⚠ {todo.due_date[:10]}"
                    elif today_start <= due <= today_end:
                        due_str = f"⏰ {todo.due_date[:10]}"
                    else:
                        due_str = todo.due_date[:10]
                except ValueError:
                    due_str = todo.due_date[:10] if len(todo.due_date) > 12 else todo.due_date

            # Status with recurrence indicator
            recur_sym = "🔄" if todo.recurrence and todo.recurrence != Recurrence.NONE else ""
            status = "Complete" if todo.complete else "Incomplete"
            status_str = f"{recur_sym} {status[:8]}" if recur_sym else status

            row = f"{todo.id:<3} | {pri_str:<4} | {title:<20} | {tags_str:<15} | {due_str:<12} | {status_str:<9}"
            result.append(row)

        return "\n".join(result)

    def format_single_todo(self, todo: Todo) -> str:
        """
        Format a single todo for display.

        Args:
            todo (Todo): The todo object to format

        Returns:
            str: Formatted string showing the todo
        """
        status = "Complete" if todo.complete else "Incomplete"
        desc = todo.description if todo.description else "No description"
        tags_str = ", ".join(todo.tags) if todo.tags else "No tags"
        due_str = f", Due: {todo.due_date}" if todo.due_date else ""
        recur_str = f", Recurring: {todo.recurrence}" if todo.recurrence and todo.recurrence != Recurrence.NONE else ""
        return f"ID: {todo.id}, Title: {todo.title}, Description: {desc}, Tags: {tags_str}, Priority: {todo.priority}{due_str}{recur_str}, Status: {status}"

    def format_deleted_list(self, todos: List[Todo]) -> str:
        """
        Format a list of deleted todos for display with reasons.

        Args:
            todos (List[Todo]): List of deleted todo objects to format

        Returns:
            str: Formatted string showing deleted todos with reasons
        """
        if not todos:
            return "No deleted todos found."

        # Create table header with reason column
        header = f"{'ID':<3} | {'Pri':<4} | {'Title':<20} | {'Reason':<20}"
        separator = "-" * len(header)
        result = [header, separator]

        # Add each deleted todo as a row
        for todo in todos:
            # Priority indicator
            pri_sym = {Priority.HIGH: "🔴", Priority.MEDIUM: "🟡", Priority.LOW: "🟢"}.get(todo.priority, "")
            pri_str = f"{pri_sym} {str(todo.priority)[:2]}" if pri_sym else str(todo.priority)[:3]

            # Title (truncated)
            title = todo.title[:17] + "..." if len(todo.title) > 20 else todo.title

            # Reason (truncated)
            reason = todo.deletion_metadata.get("reason", "")
            reason_display = reason[:17] + "..." if len(reason) > 20 else reason

            row = f"{todo.id:<3} | {pri_str:<4} | {title:<20} | {reason_display:<20}"
            result.append(row)

        return "\n".join(result)
