"""System prompt loader for Todo AI Agent."""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SystemPromptLoader:
    """Loads and combines constitution and specification as system prompt."""

    def __init__(self, constitution_path: Optional[str] = None, spec_path: Optional[str] = None):
        """
        Initialize with paths to constitution and spec files.

        Args:
            constitution_path: Path to constitution.md file
            spec_path: Path to specification.md file
        """
        self.constitution_path = constitution_path or self._find_constitution_path()
        self.spec_path = spec_path or self._find_spec_path()

        logger.info(f"Constitution path: {self.constitution_path}")
        logger.info(f"Specification path: {self.spec_path}")

    def _find_constitution_path(self) -> str:
        """Find the constitution file path."""
        possible_paths = [
            "specs/agents/todo-agent.constitution.md",
            "../specs/agents/todo-agent.constitution.md",
            "/mnt/d/todo_phase_ll/phase1_todo/specs/agents/todo-agent.constitution.md"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Try to find any constitution file
        for root, dirs, files in os.walk("."):
            for file in files:
                if "constitution" in file.lower() and file.endswith(".md"):
                    return os.path.join(root, file)

        raise FileNotFoundError(
            "Could not find constitution file. "
            "Expected: specs/agents/todo-agent.constitution.md"
        )

    def _find_spec_path(self) -> str:
        """Find the specification file path."""
        possible_paths = [
            "specs/agents/todo-agent.spec.md",
            "../specs/agents/todo-agent.spec.md",
            "/mnt/d/todo_phase_ll/phase1_todo/specs/agents/todo-agent.spec.md"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # Try to find any spec file
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".spec.md"):
                    return os.path.join(root, file)

        raise FileNotFoundError(
            "Could not find specification file. "
            "Expected: specs/agents/todo-agent.spec.md"
        )

    def load_constitution(self) -> str:
        """Load and return constitution content."""
        try:
            with open(self.constitution_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            logger.info(f"Loaded constitution from {self.constitution_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to load constitution: {str(e)}")
            raise

    def load_specification(self) -> str:
        """Load and return specification content."""
        try:
            with open(self.spec_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            logger.info(f"Loaded specification from {self.spec_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to load specification: {str(e)}")
            raise

    def create_system_prompt(self) -> str:
        """
        Create combined system prompt from constitution and spec.

        Returns:
            Formatted system prompt string
        """
        constitution = self.load_constitution()
        specification = self.load_specification()

        prompt = f"""# Todo AI Agent System Prompt

## CONSTITUTION (Core Rules)
{constitution}

## SPECIFICATION (Agent Behavior)
{specification}

## CRITICAL INSTRUCTIONS

### Response Format
1. ALWAYS respond in natural, conversational language.
2. NEVER output raw JSON, function calls, or tool schemas to the user.
3. After executing tools, summarize results in plain English.

### Tool Usage
1. You MUST use MCP tools for ALL task operations.
2. Execute tools silently - show only the results to users.
3. For mutations (create/update/delete), ask confirmation first.

### Date Handling
1. "due today" → use `due_today: true` filter
2. "due this week" → use `due_this_week: true` filter
3. "overdue" → use `overdue: true` filter (past due + not completed)
4. When creating tasks, convert dates to YYYY-MM-DD format.

### Priority Handling
1. Priority (HIGH/MEDIUM/LOW) is a user-defined importance level.
2. Priority is INDEPENDENT of due dates.
3. "high priority tasks" → filter by `priority: 'HIGH'`
4. "urgent" without "tag" → treat as HIGH priority, not a tag search.

### Tags Handling
1. Tags are arrays of labels attached to tasks.
2. When creating: `tags: ['work', 'urgent']` (as array)
3. Only filter by tag when user says "tag" or "label" explicitly.

### Add vs Update Intent (CRITICAL)
**Distinguish between CREATE (new task) and UPDATE (modify existing task):**

1. **CREATE new task** (use `add_task`):
   - "add task [title]" → create task with that title
   - "add '[title]'" → create task with that title
   - "new task: [title]" → create task with that title

2. **UPDATE existing task** (use `update_task`):
   - "add description to task [name]" → FIND task by name, then UPDATE its description
   - "add description in task [name]" → FIND task by name, then UPDATE its description
   - "set [field] for task [name]" → FIND task by name, then UPDATE that field

3. **Detection rules:**
   - If user mentions "task [name]" or "[name] task" and wants to add/modify a field → UPDATE
   - Look for patterns: "to task", "in task", "for task", "on task" → UPDATE intent
   - If user says just "add [title]" without referencing existing task → CREATE

4. **Workflow for UPDATE by name:**
   a. Call `list_tasks(filters: {{"search": "[name]"}})` to find the task
   b. Get the task_id from result
   c. Call `update_task(task_id: found_id, field: value)`

**Example**: "add description in tasks clothes we are buyer"
- This means: UPDATE the existing task "clothes" with description "we are buyer"
- Step 1: `list_tasks(filters: {{"search": "clothes"}})` to find task ID
- Step 2: `update_task(task_id: found_id, description: "we are buyer")`
- NOT: create a new task

### Example Good Responses
- "Here are your 3 high priority tasks: 1. Buy groceries (due tomorrow) 2. Call mom 3. Finish report"
- "I created the task 'Buy milk' with HIGH priority, tagged with 'food' and 'weekly', due March 15, 2024."
- "You have 2 tasks due this week: 1. Submit report (due Monday) 2. Team meeting (due Friday)"

Remember: You only manage todo tasks. Be helpful and conversational.
"""

        logger.info("System prompt created successfully")
        logger.debug(f"System prompt length: {len(prompt)} characters")

        return prompt

    def get_truncated_prompt(self, max_length: int = 32000) -> str:
        """
        Get system prompt truncated to specified length.

        Args:
            max_length: Maximum character length

        Returns:
            Truncated system prompt
        """
        prompt = self.create_system_prompt()
        if len(prompt) > max_length:
            logger.warning(f"System prompt truncated from {len(prompt)} to {max_length} characters")
            # Try to keep constitution complete, truncate spec if needed
            constitution = self.load_constitution()
            available_space = max_length - len(constitution) - 500  # Buffer for headers
            spec = self.load_specification()
            if len(spec) > available_space:
                spec = spec[:available_space] + "\n\n[Specification truncated...]"

            prompt = f"""# Todo AI Agent System Prompt (Truncated)

## CONSTITUTION (Core Rules)
{constitution}

## SPECIFICATION (Agent Behavior) - TRUNCATED
{spec}

[Prompt truncated due to length constraints. Full spec available at {self.spec_path}]
"""
        return prompt[:max_length]


# Singleton instance
_loader_instance: Optional[SystemPromptLoader] = None


def get_system_prompt_loader() -> SystemPromptLoader:
    """Get singleton system prompt loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = SystemPromptLoader()
    return _loader_instance


def get_system_prompt(truncate: bool = True, max_length: int = 32000) -> str:
    """Get system prompt, optionally truncated."""
    loader = get_system_prompt_loader()
    if truncate:
        return loader.get_truncated_prompt(max_length)
    return loader.create_system_prompt()


def refresh_system_prompt() -> str:
    """Force refresh and return new system prompt."""
    global _loader_instance
    _loader_instance = SystemPromptLoader()
    return _loader_instance.create_system_prompt()