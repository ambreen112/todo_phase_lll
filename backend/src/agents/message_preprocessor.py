"""Message preprocessor for handling complex natural language patterns.

This module intercepts user messages and detects patterns that the AI model
might misinterpret, converting them to explicit tool calls or reformatted
messages that are easier for the model to process correctly.
"""

import re
import logging
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID

from sqlmodel import Session, select

from ..models.task import Task

logger = logging.getLogger(__name__)


class MessagePreprocessor:
    """Preprocesses user messages to handle complex intent patterns."""

    def __init__(self, user_id: UUID, session: Session):
        """
        Initialize preprocessor with user context.

        Args:
            user_id: The authenticated user's UUID
            session: Database session for task lookups
        """
        self.user_id = user_id
        self.session = session

    def preprocess(self, message: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Preprocess a user message.

        Args:
            message: The original user message

        Returns:
            Tuple of (processed_message, direct_action)
            - processed_message: Reformatted message for the AI
            - direct_action: If not None, execute this action directly instead of AI
        """
        message_lower = message.lower().strip()

        # Check for "add [field] to/in task [name]" patterns (UPDATE, not CREATE)
        update_action = self._detect_update_by_name(message, message_lower)
        if update_action:
            return message, update_action

        # Check for "change/set [field] of/for task [name]" patterns
        change_action = self._detect_change_field(message, message_lower)
        if change_action:
            return message, change_action

        # Check for "delete [task name] with reason [reason]" patterns
        delete_action = self._detect_delete_by_name(message, message_lower)
        if delete_action:
            return message, delete_action

        # Check for "add task [title] with [priority/tags/due date]" patterns (CREATE)
        create_action = self._detect_create_task(message, message_lower)
        if create_action:
            return message, create_action

        # No preprocessing needed
        return message, None

    def _detect_update_by_name(self, message: str, message_lower: str) -> Optional[Dict[str, Any]]:
        """
        Detect "add [field] to/in task [name]" patterns.

        These should UPDATE an existing task, not CREATE a new one.
        """
        # Patterns for adding a field to an existing task
        patterns = [
            # "add description [value] to/in task [name]"
            r"add\s+description\s+(.+?)\s+(?:to|in|for|on)\s+(?:task[s]?\s+)?(.+?)(?:\s+task[s]?)?$",
            # "add description to/in task [name] [value]"
            r"add\s+description\s+(?:to|in|for|on)\s+(?:task[s]?\s+)?(.+?)\s+(.+)$",
            # "add [value] description to/in [name] task"
            r"add\s+(.+?)\s+description\s+(?:to|in|for|on)\s+(.+?)\s+task[s]?$",
        ]

        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                groups = match.groups()
                # Determine which group is description and which is task name
                # Usually the longer text is the description
                if len(groups) == 2:
                    # Try to find which one matches a task
                    task1 = self._find_task_by_name(groups[0])
                    task2 = self._find_task_by_name(groups[1])

                    if task2 and not task1:
                        # groups[1] is the task name, groups[0] is the description
                        return self._create_update_action(task2, "description", groups[0].strip())
                    elif task1 and not task2:
                        # groups[0] is the task name, groups[1] is the description
                        return self._create_update_action(task1, "description", groups[1].strip())
                    elif task1 and task2:
                        # Both match, use the second one as task (common pattern)
                        return self._create_update_action(task2, "description", groups[0].strip())

        # Simpler pattern: "add description in tasks [name] [value]"
        simple_pattern = r"add\s+description\s+(?:to|in|for|on)?\s*(?:task[s]?)?\s*(\w+)\s+(.+)$"
        match = re.search(simple_pattern, message_lower)
        if match:
            task_name = match.group(1).strip()
            description = match.group(2).strip()
            task = self._find_task_by_name(task_name)
            if task:
                return self._create_update_action(task, "description", description)

        return None

    def _detect_delete_by_name(self, message: str, message_lower: str) -> Optional[Dict[str, Any]]:
        """
        Detect "delete [task name] with reason [reason]" patterns.
        """
        # Patterns for deleting a task by name with reason
        patterns = [
            # "delete [name] task with reason [reason]"
            r"delete\s+(?:my\s+)?(.+?)\s+task[s]?\s+(?:with\s+)?reason\s+(.+)$",
            # "delete task [name] with reason [reason]"
            r"delete\s+(?:my\s+)?task[s]?\s+(.+?)\s+(?:with\s+)?reason\s+(.+)$",
            # "delete [name] with reason [reason]"
            r"delete\s+(?:my\s+)?(.+?)\s+(?:with\s+)?reason\s+(.+)$",
            # "remove [name] task because [reason]"
            r"(?:remove|delete)\s+(?:my\s+)?(.+?)\s+task[s]?\s+(?:because|due to|for)\s+(.+)$",
        ]

        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                task_name = match.group(1).strip()
                reason = match.group(2).strip()

                # Clean up task name - remove "with description X" parts
                if "with description" in task_name:
                    task_name = task_name.split("with description")[0].strip()

                task = self._find_task_by_name(task_name)
                if task:
                    # If user mentioned "with description X", find the task that has that description
                    if "with description" in message_lower:
                        desc_match = re.search(r"with\s+description\s+(.+?)(?:\s+(?:with\s+)?reason|$)", message_lower)
                        if desc_match:
                            target_desc = desc_match.group(1).strip()
                            # Find task with matching description
                            task = self._find_task_by_name_and_description(task_name, target_desc)

                    if task:
                        return self._create_delete_action(task, reason)

        return None

    def _find_task_by_name_and_description(self, name: str, description: str) -> Optional[Task]:
        """
        Find a task by name and description.
        """
        name = name.strip().lower()
        description = description.strip().lower()

        query = select(Task).where(
            Task.owner_id == self.user_id,
            Task.deleted_at.is_(None)
        )
        tasks = self.session.exec(query).all()

        for task in tasks:
            task_title_lower = task.title.lower()
            task_desc_lower = (task.description or "").lower()

            if name in task_title_lower or task_title_lower in name:
                if description in task_desc_lower:
                    return task

        return None

    def _create_delete_action(self, task: Task, reason: str) -> Dict[str, Any]:
        """
        Create a direct delete action.
        """
        logger.info(f"Preprocessor: Creating delete action for task '{task.title}' - reason: {reason}")

        return {
            "action": "delete_task",
            "task_id": str(task.id),
            "task_title": task.title,
            "reason": reason,
            "confirm_message": f"Delete task '{task.title}' with reason '{reason}'?"
        }

    def _detect_create_task(self, message: str, message_lower: str) -> Optional[Dict[str, Any]]:
        """
        Detect "add task [title] with [attributes]" patterns for CREATE.
        """
        # Patterns for creating a new task
        patterns = [
            # "add task [title] with [priority] priority"
            r"add\s+task[s]?\s+(?:with\s+title\s+)?(.+?)\s+with\s+(high|medium|low)\s+priority",
            # "add task [title] [priority] priority"
            r"add\s+task[s]?\s+(?:with\s+title\s+)?(.+?)\s+(high|medium|low)\s+priority",
            # "add [priority] priority task [title]"
            r"add\s+(high|medium|low)\s+priority\s+task[s]?\s+(.+?)$",
            # "add task [title]"
            r"add\s+task[s]?\s+(?:with\s+title\s+)?([^with]+?)(?:\s*$|\s+with\s+)",
            # "create task [title]"
            r"create\s+(?:a\s+)?task[s]?\s+(?:called\s+|named\s+)?(.+?)(?:\s*$|\s+with\s+)",
            # "new task [title]"
            r"new\s+task[s]?[:\s]+(.+?)(?:\s*$|\s+with\s+)",
        ]

        title = None
        priority = "MEDIUM"
        tags = []
        due_date = None

        for i, pattern in enumerate(patterns):
            match = re.search(pattern, message_lower)
            if match:
                groups = match.groups()

                if i == 0:  # "add task [title] with [priority] priority"
                    title = groups[0].strip()
                    priority = groups[1].upper()
                elif i == 1:  # "add task [title] [priority] priority"
                    title = groups[0].strip()
                    priority = groups[1].upper()
                elif i == 2:  # "add [priority] priority task [title]"
                    priority = groups[0].upper()
                    title = groups[1].strip()
                else:  # Simple patterns
                    title = groups[0].strip() if groups[0] else None

                break

        if not title:
            return None

        # Clean up the title - remove trailing words like "priority", "with", etc.
        title = re.sub(r'\s+(high|medium|low|with|priority).*$', '', title, flags=re.IGNORECASE).strip()

        # Don't process if title looks like it's referencing an existing task field
        if any(word in title.lower() for word in ['description', 'to task', 'in task', 'for task']):
            return None

        if not title or len(title) < 2:
            return None

        # Extract priority if mentioned later in the message
        priority_match = re.search(r'(high|medium|low)\s+priority', message_lower)
        if priority_match:
            priority = priority_match.group(1).upper()

        # Extract tags if mentioned
        tags_match = re.search(r'(?:with\s+)?tags?\s+(.+?)(?:\s+(?:due|on|priority)|$)', message_lower)
        if tags_match:
            tags_str = tags_match.group(1)
            tags = [t.strip() for t in re.split(r'[,\s]+', tags_str) if t.strip() and t.strip() not in ['and', 'or']]

        # Extract due date if mentioned
        due_match = re.search(r'(?:due|on)\s+(\d{4}-\d{2}-\d{2})', message_lower)
        if due_match:
            due_date = due_match.group(1)

        logger.info(f"Preprocessor: Creating add_task action - title: {title}, priority: {priority}")

        return {
            "action": "add_task",
            "title": title,
            "priority": priority,
            "tags": tags if tags else None,
            "due_date": due_date
        }

    def _detect_change_field(self, message: str, message_lower: str) -> Optional[Dict[str, Any]]:
        """
        Detect "change/set [field] of/for task [name]" patterns.
        """
        # Pattern: "change priority of [name] task from X to Y"
        priority_pattern = r"(?:change|set|update)\s+priority\s+(?:of|for)\s+(.+?)\s+(?:task[s]?)?\s*(?:from\s+\w+\s+)?to\s+(\w+)"
        match = re.search(priority_pattern, message_lower)
        if match:
            task_name = match.group(1).strip()
            new_priority = match.group(2).strip().upper()
            task = self._find_task_by_name(task_name)
            if task and new_priority in ["HIGH", "MEDIUM", "LOW"]:
                return self._create_update_action(task, "priority", new_priority)

        # Pattern: "change [name] task priority to Y"
        priority_pattern2 = r"(?:change|set|update)\s+(.+?)\s+(?:task[s]?)?\s*priority\s+(?:from\s+\w+\s+)?to\s+(\w+)"
        match = re.search(priority_pattern2, message_lower)
        if match:
            task_name = match.group(1).strip()
            new_priority = match.group(2).strip().upper()
            task = self._find_task_by_name(task_name)
            if task and new_priority in ["HIGH", "MEDIUM", "LOW"]:
                return self._create_update_action(task, "priority", new_priority)

        return None

    def _find_task_by_name(self, name: str) -> Optional[Task]:
        """
        Find a task by name/title (case-insensitive partial match).

        Args:
            name: Task name to search for

        Returns:
            Task if found, None otherwise
        """
        name = name.strip().lower()
        if not name:
            return None

        # Remove common words that aren't part of the task name
        noise_words = ["my", "the", "a", "an", "task", "tasks"]
        name_parts = [w for w in name.split() if w not in noise_words]
        if not name_parts:
            return None

        clean_name = " ".join(name_parts)

        # Query for active tasks matching the name
        query = select(Task).where(
            Task.owner_id == self.user_id,
            Task.deleted_at.is_(None)
        )
        tasks = self.session.exec(query).all()

        # Find best match
        for task in tasks:
            task_title_lower = task.title.lower()
            # Exact match
            if task_title_lower == clean_name:
                return task
            # Partial match (task name contains search term or vice versa)
            if clean_name in task_title_lower or task_title_lower in clean_name:
                return task
            # Word-based match
            if any(word in task_title_lower for word in name_parts):
                return task

        return None

    def _create_update_action(self, task: Task, field: str, value: Any) -> Dict[str, Any]:
        """
        Create a direct update action.

        Args:
            task: The task to update
            field: Field name to update
            value: New value for the field

        Returns:
            Action dict with tool name and arguments
        """
        logger.info(f"Preprocessor: Creating update action for task '{task.title}' - {field}={value}")

        return {
            "action": "update_task",
            "task_id": str(task.id),
            "task_title": task.title,
            "field": field,
            "value": value,
            "confirm_message": f"Update task '{task.title}' - set {field} to '{value}'?"
        }


def preprocess_message(message: str, user_id: UUID, session: Session) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Convenience function to preprocess a message.

    Args:
        message: User message
        user_id: User's UUID
        session: Database session

    Returns:
        Tuple of (processed_message, direct_action)
    """
    preprocessor = MessagePreprocessor(user_id, session)
    return preprocessor.preprocess(message)
