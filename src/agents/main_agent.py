"""
Main Agent for handling user input, command parsing, and delegation to subagents.
"""

from typing import Optional
from datetime import datetime, timedelta
from src.agents.add_update_agent import AddUpdateAgent
from src.agents.list_search_agent import ListSearchAgent
from src.agents.delete_complete_agent import DeleteCompleteAgent
from src.models.todo import Priority, Recurrence


class MainAgent:
    """
    Main agent that handles the input loop, command parsing, and delegation to subagents.
    """

    def __init__(
        self,
        add_update_agent: AddUpdateAgent,
        list_search_agent: ListSearchAgent,
        delete_complete_agent: DeleteCompleteAgent
    ):
        """
        Initialize the Main agent with required subagents.

        Args:
            add_update_agent (AddUpdateAgent): Agent for adding and updating todos
            list_search_agent (ListSearchAgent): Agent for listing and searching todos
            delete_complete_agent (DeleteCompleteAgent): Agent for deleting and completing todos
        """
        self.add_update_agent = add_update_agent
        self.list_search_agent = list_search_agent
        self.delete_complete_agent = delete_complete_agent

    def run(self):
        """
        Main loop that displays the prompt and processes user input.
        """
        print("Welcome to the Todo App!")
        print("Type 'help' for available commands or 'exit' to quit.")

        # Show startup alerts
        self._show_startup_alerts()

        while True:
            try:
                user_input = input("Todo> ").strip()
                if not user_input:
                    continue

                result = self.parse_command(user_input)

                if result == "EXIT":
                    print("Goodbye!")
                    break
                elif result is not None:
                    print(result)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break

    def _show_startup_alerts(self):
        """
        Show alerts for overdue and due today tasks on startup.
        """
        overdue = self.list_search_agent.get_overdue_todos()
        due_today = self.list_search_agent.get_due_today_todos()

        if overdue or due_today:
            print("\n" + "="*50)
            if overdue:
                print(f"⚠  You have {len(overdue)} overdue task(s):")
                for todo in overdue:
                    print(f"   - {todo.id}: {todo.title}")
            if due_today:
                print(f"⏰  Tasks due today ({len(due_today)}):")
                for todo in due_today:
                    print(f"   - {todo.id}: {todo.title}")
            print("="*50 + "\n")

    def parse_command(self, user_input: str) -> Optional[str]:
        """
        Parses user commands and arguments.

        Args:
            user_input (str): The raw user input

        Returns:
            Optional[str]: The result of the command execution, or "EXIT" to quit
        """
        parts = user_input.split()
        if not parts:
            return "Invalid command. Type 'help' for available commands."

        command = parts[0].lower()
        args = parts[1:]

        # Handle different commands
        if command == "help":
            return self._help_command()
        elif command == "add":
            return self._add_command(args)
        elif command == "list":
            return self._list_command(args)
        elif command == "search":
            return self._search_command(args)
        elif command == "delete":
            return self._delete_command(args)
        elif command == "list-deleted":
            return self._list_deleted_command(args)
        elif command == "restore":
            return self._restore_command(args)
        elif command == "update":
            return self._update_command(args)
        elif command == "complete":
            return self._complete_command(args)
        elif command == "incomplete":
            return self._incomplete_command(args)
        elif command == "remind":
            return self._remind_command(args)
        elif command == "stop-recur":
            return self._stop_recur_command(args)
        elif command == "exit":
            return "EXIT"
        else:
            return f"Unknown command: {command}. Type 'help' for available commands."

    def _help_command(self) -> str:
        """
        Handle the help command to show available commands.

        Returns:
            str: Help text with available commands
        """
        help_text = """
Available commands:
  add <title> --desc <desc> --priority <high/med/low> --tag <tag1,tag2> --due <YYYY-MM-DD> --recur <daily/weekly/monthly>
                          - Add a new todo with optional fields
  list [--priority <val>] [--tag <tag>] [--status <complete/incomplete>] [--sort <id/priority/title/status>] [--due <overdue/today>]
                          - List todos with optional filters and sorting
  search <keyword> --priority <val> --tag <tag> --status <complete/incomplete> --sort <field>
                          - Search todos by keyword with optional filters
  delete <id> <reason>                          - Soft delete a todo with reason
  list-deleted                                     - List all deleted todos with reasons
  restore <id>                                    - Restore a deleted todo
  update <id> --title <new> --priority <val> --tag <tags> --due <date> --recur <freq>
                          - Update todo fields by ID
  complete <id>                                     - Mark a todo as complete by ID
  incomplete <id>                                   - Mark a todo as incomplete by ID
  remind                                            - Show overdue and due today tasks
  stop-recur <id>                                  - Stop recurrence for a todo
  help                                              - Show this help message
  exit                                              - Exit the application
        """.strip()
        return help_text

    def _parse_flags(self, args: list) -> dict:
        """
        Parse flags from command arguments.

        Args:
            args (list): Command arguments

        Returns:
            dict: Parsed flags and values
        """
        flags = {
            "title": None,
            "description": None,
            "priority": None,
            "tags": None,
            "due_date": None,
            "recurrence": None,
            "filter_priority": None,
            "filter_tag": None,
            "filter_status": None,
            "sort_by": None,
            "filter_due": None
        }

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "--desc" or arg == "--description":
                if i + 1 < len(args):
                    flags["description"] = args[i + 1]
                    i += 1
            elif arg == "--priority" or arg == "--pri":
                if i + 1 < len(args):
                    pri_str = args[i + 1].lower()
                    try:
                        # Map common abbreviations or full names
                        if pri_str.startswith("h"):
                            flags["priority"] = Priority.HIGH
                        elif pri_str.startswith("m"):
                            flags["priority"] = Priority.MEDIUM
                        elif pri_str.startswith("l"):
                            flags["priority"] = Priority.LOW
                        else:
                            flags["priority"] = Priority(pri_str)
                    except ValueError:
                        flags["priority"] = Priority.MEDIUM
                    i += 1
            elif arg == "--tag" or arg == "--tags":
                if i + 1 < len(args):
                    tags_str = args[i + 1]
                    flags["tags"] = [t.strip() for t in tags_str.split(",")]
                    i += 1
            elif arg == "--due":
                if i + 1 < len(args):
                    due_str = args[i + 1]
                    if due_str.lower() in ["none", "remove", "delete"]:
                        flags["due_date"] = None
                    else:
                        flags["due_date"] = due_str
                    i += 1
            elif arg == "--recur" or arg == "--recurrence":
                if i + 1 < len(args):
                    recur_str = args[i + 1].lower()
                    try:
                        flags["recurrence"] = Recurrence(recur_str[:7])
                    except ValueError:
                        flags["recurrence"] = Recurrence.NONE
                    i += 1
            elif arg == "--title":
                if i + 1 < len(args):
                    flags["title"] = args[i + 1]
                    i += 1
            elif arg == "--sort":
                if i + 1 < len(args):
                    sort_val = args[i + 1].lower()
                    if sort_val in ["id", "priority", "title", "status"]:
                        flags["sort_by"] = sort_val
                    i += 1
            elif arg == "--status":
                if i + 1 < len(args):
                    status_val = args[i + 1].lower()
                    if status_val in ["complete", "incomplete"]:
                        flags["filter_status"] = status_val
                    i += 1
            elif arg == "--due-overdue" or arg == "--due-over":
                flags["filter_due"] = "overdue"
            elif arg == "--due-today" or arg == "--due-t":
                flags["filter_due"] = "today"
            i += 1

        return flags

    def _add_command(self, args: list) -> str:
        """
        Handle the add command.

        Args:
            args (list): Arguments for the add command

        Returns:
            str: Result of the add operation
        """
        # Parse flags
        flags = self._parse_flags(args)

        # Extract title (first non-flag argument)
        title_parts = []
        for arg in args:
            if arg.startswith("--"):
                break
            title_parts.append(arg)
        title = " ".join(title_parts) if title_parts else flags.get("title")

        if not title or not title.strip():
            return "Usage: add <title> --desc <desc> --priority <high/med/low> --tag <tags> --due <date> --recur <freq>"

        result = self.add_update_agent.add_task(
            title=title.strip(),
            description=flags.get("description"),
            priority=flags.get("priority"),
            tags=flags.get("tags"),
            due_date=flags.get("due_date"),
            recurrence=flags.get("recurrence")
        )

        if result:
            parts = []
            parts.append(f"Title '{result.title}'")
            if result.description:
                parts.append(f"Description: '{result.description}'")
            if result.priority != Priority.MEDIUM:
                parts.append(f"Priority: {result.priority}")
            if result.tags:
                parts.append(f"Tags: {', '.join(result.tags)}")
            if result.due_date:
                parts.append(f"Due: {result.due_date}")
            if result.recurrence != Recurrence.NONE:
                parts.append(f"Recurring: {result.recurrence}")
            return f"Added todo: {', '.join(parts)} with ID {result.id}"
        else:
            return "Error: Title cannot be empty."

    def _list_command(self, args: list) -> str:
        """
        Handle the list command.

        Args:
            args (list): Arguments for the list command

        Returns:
            str: Result of the list operation
        """
        flags = self._parse_flags(args)

        # Parse priority filter
        filter_priority = None
        pri_str = flags.get("filter_priority")
        if pri_str:
            try:
                filter_priority = Priority(pri_str.lower()[:3])
            except ValueError:
                pass

        # Parse status filter
        filter_status = flags.get("filter_status")

        # Parse due filter
        if flags["filter_due"] == "overdue":
            overdue = self.list_search_agent.get_overdue_todos()
            return self.list_search_agent.formatter_skill.format_todo_list(overdue)
        elif flags["filter_due"] == "today":
            due_today = self.list_search_agent.get_due_today_todos()
            return self.list_search_agent.formatter_skill.format_todo_list(due_today)

        return self.list_search_agent.list_all_todos(
            filter_priority=filter_priority,
            filter_tag=flags.get("filter_tag"),
            filter_status=filter_status,
            sort_by=flags.get("sort_by")
        )

    def _search_command(self, args: list) -> str:
        """
        Handle the search command.

        Args:
            args (list): Arguments for the search command

        Returns:
            str: Result of the search operation
        """
        if not args:
            return "Usage: search <keyword> [filters]"

        # Get search keyword (first non-flag argument)
        keyword_parts = []
        for arg in args:
            if arg.startswith("--"):
                break
            keyword_parts.append(arg)
        keyword = " ".join(keyword_parts)

        # Parse flags for filters
        flags = self._parse_flags(args)

        # Parse priority filter
        filter_priority = None
        pri_str = flags.get("filter_priority")
        if pri_str:
            try:
                filter_priority = Priority(pri_str.lower()[:3])
            except ValueError:
                pass

        filter_status = flags.get("filter_status")
        sort_by = flags.get("sort_by")

        # Get all todos and apply filters
        todos = self.list_search_agent.storage_skill.get_all_todos()

        # Apply filters
        if filter_priority:
            todos = [t for t in todos if t.priority == filter_priority]
        if flags["filter_tag"]:
            tag = flags["filter_tag"].lower()
            todos = [t for t in todos if tag in [tg.lower() for tg in t.tags]]
        if filter_status:
            if filter_status == "complete":
                todos = [t for t in todos if t.complete]
            elif filter_status == "incomplete":
                todos = [t for t in todos if not t.complete]

        # Apply search
        if keyword:
            keyword_lower = keyword.lower()
            todos = [t for t in todos if
                    keyword_lower in t.title.lower() or
                    (t.description and keyword_lower in t.description.lower()) or
                    any(keyword_lower in tag.lower() for tag in t.tags)]

        # Apply sorting
        if sort_by == "id":
            todos = sorted(todos, key=lambda t: t.id)
        elif sort_by == "priority":
            from src.models.todo import Priority
            priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
            todos = sorted(todos, key=lambda t: priority_order[t.priority])
        elif sort_by == "title":
            todos = sorted(todos, key=lambda t: t.title.lower())
        elif sort_by == "status":
            todos = sorted(todos, key=lambda t: not t.complete)

        if not todos:
            return "No matching todos found."

        return self.list_search_agent.formatter_skill.format_todo_list(todos)

    def _delete_command(self, args: list) -> str:
        """
        Handle delete command with required reason.

        Args:
            args (list): Arguments for delete command

        Returns:
            str: Result of delete operation
        """
        if len(args) < 2:
            return "Usage: delete <id> <reason>"

        try:
            todo_id = int(args[0])
        except ValueError:
            return "Error: ID must be a number."

        reason = " ".join(args[1:])
        reason = reason.strip()

        if not reason:
            return "Error: Deletion reason cannot be empty."

        if len(reason) > 500:
            return "Error: Deletion reason must be 500 characters or less."

        success = self.delete_complete_agent.delete_todo(todo_id, reason)

        if success:
            return f"Todo {todo_id} deleted successfully."
        else:
            return f"Error: Todo with ID {todo_id} not found."

    def _list_deleted_command(self, args: list) -> str:
        """
        Handle list-deleted command.

        Args:
            args (list): Arguments for list-deleted command

        Returns:
            str: Result of list-deleted operation
        """
        if len(args) > 0:
            return "Usage: list-deleted (no arguments required)"

        return self.list_search_agent.list_deleted_todos()

    def _restore_command(self, args: list) -> str:
        """
        Handle restore command.

        Args:
            args (list): Arguments for restore command

        Returns:
            str: Result of restore operation
        """
        if len(args) != 1:
            return "Usage: restore <id>"

        try:
            todo_id = int(args[0])
        except ValueError:
            return "Error: ID must be a number."

        success = self.delete_complete_agent.restore_todo(todo_id)

        if success:
            return f"Todo {todo_id} restored successfully."
        else:
            return f"Error: Todo with ID {todo_id} not found or is not deleted."

    def _update_command(self, args: list) -> str:
        """
        Handle the update command.

        Args:
            args (list): Arguments for the update command

        Returns:
            str: Result of the update operation
        """
        if len(args) < 1:
            return "Usage: update <id> [options]"

        try:
            todo_id = int(args[0])
        except ValueError:
            return "Error: ID must be a number."

        flags = self._parse_flags(args[1:])

        success = self.add_update_agent.update_task(
            todo_id=todo_id,
            new_title=flags.get("title"),
            priority=flags.get("priority"),
            tags=flags.get("tags"),
            due_date=flags.get("due_date"),
            recurrence=flags.get("recurrence")
        )

        if success:
            return f"Todo {todo_id} updated successfully."
        else:
            return f"Error: Todo with ID {todo_id} not found or invalid input."

    def _complete_command(self, args: list) -> str:
        """
        Handle the complete command.

        Args:
            args (list): Arguments for the complete command

        Returns:
            str: Result of the complete operation
        """
        if len(args) != 1:
            return "Usage: complete <id>"

        try:
            todo_id = int(args[0])
        except ValueError:
            return "Error: ID must be a number."

        success = self.delete_complete_agent.complete_todo(todo_id)

        if success:
            return f"Todo {todo_id} marked as complete."
        else:
            return f"Error: Todo with ID {todo_id} not found."

    def _incomplete_command(self, args: list) -> str:
        """
        Handle the incomplete command.

        Args:
            args (list): Arguments for the incomplete command

        Returns:
            str: Result of the incomplete operation
        """
        if len(args) != 1:
            return "Usage: incomplete <id>"

        try:
            todo_id = int(args[0])
        except ValueError:
            return "Error: ID must be a number."

        success = self.delete_complete_agent.incomplete_todo(todo_id)

        if success:
            return f"Todo {todo_id} marked as incomplete."
        else:
            return f"Error: Todo with ID {todo_id} not found."

    def _remind_command(self, args: list) -> str:
        """
        Handle the remind command.

        Args:
            args (list): Arguments for the remind command

        Returns:
            str: Result of the remind operation
        """
        if len(args) > 0:
            return "Usage: remind (no arguments required)"

        overdue = self.list_search_agent.get_overdue_todos()
        due_today = self.list_search_agent.get_due_today_todos()

        if not overdue and not due_today:
            return "No overdue or due today tasks."

        result = []
        if overdue:
            result.append(f"⚠  Overdue tasks ({len(overdue)}):")
            for todo in overdue:
                result.append(f"   - {todo.id}: {todo.title}")
        if due_today:
            result.append(f"⏰  Tasks due today ({len(due_today)}):")
            for todo in due_today:
                result.append(f"   - {todo.id}: {todo.title}")

        return "\n".join(result)

    def _stop_recur_command(self, args: list) -> str:
        """
        Handle the stop-recur command.

        Args:
            args (list): Arguments for the stop-recur command

        Returns:
            str: Result of the stop-recur operation
        """
        if len(args) != 1:
            return "Usage: stop-recur <id>"

        try:
            todo_id = int(args[0])
        except ValueError:
            return "Error: ID must be a number."

        success = self.add_update_agent.update_task(todo_id, recurrence=Recurrence.NONE)

        if success:
            return f"Todo {todo_id} recurrence stopped."
        else:
            return f"Error: Todo with ID {todo_id} not found."
