"""Tool registry for Todo AI Agent."""

import json
import logging
from typing import Dict, Any, List, Optional
from openai.types.chat.chat_completion_message_tool_call_param import Function

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for MCP tool schemas."""

    def __init__(self):
        self._tools: Dict[str, dict] = {}
        self._load_tool_schemas()

    def _load_tool_schemas(self) -> None:
        """Load tool schemas from specification."""
        # These are placeholder schemas based on specs/agents/tools.md
        # Actual implementations will be in backend/src/api/routes/mcp/
        self._tools = {
            "list_tasks": {
                "name": "list_tasks",
                "description": "List tasks owned by the authenticated user with optional filters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filters": {
                            "type": "object",
                            "description": "Optional filters for tasks",
                            "properties": {
                                "completed": {
                                    "type": "boolean",
                                    "description": "Filter by completion status"
                                },
                                "deleted": {
                                    "type": "boolean",
                                    "description": "Filter by deletion status"
                                },
                                "priority": {
                                    "type": "string",
                                    "enum": ["HIGH", "MEDIUM", "LOW"],
                                    "description": "Filter by priority"
                                },
                                "search": {
                                    "type": "string",
                                    "description": "Search keyword to match in task title or description (case-insensitive). Use this for keyword searches like 'search sun' or 'find meeting'."
                                },
                                "tag": {
                                    "type": "string",
                                    "description": "Filter by exact tag/label. ONLY use when user explicitly says 'tag' or 'label' (e.g., 'tasks with tag work', 'show label urgent')."
                                },
                                "due_before": {
                                    "type": "string",
                                    "format": "date",
                                    "description": "Filter tasks due before this date (YYYY-MM-DD format)"
                                },
                                "due_after": {
                                    "type": "string",
                                    "format": "date",
                                    "description": "Filter tasks due after this date (YYYY-MM-DD format)"
                                },
                                "due_today": {
                                    "type": "boolean",
                                    "description": "Filter tasks due today"
                                },
                                "due_this_week": {
                                    "type": "boolean",
                                    "description": "Filter tasks due within the current week (Monday to Sunday)"
                                },
                                "overdue": {
                                    "type": "boolean",
                                    "description": "Filter tasks that are past their due date and not completed"
                                }
                            }
                        }
                    }
                },
                "returns": {
                    "type": "array",
                    "description": "Array of task objects",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "completed": {"type": "boolean"},
                            "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                            "due_date": {"type": "string", "format": "date-time", "nullable": True}
                        }
                    }
                }
            },
            "get_task": {
                "name": "get_task",
                "description": "Fetch one task by ID",
                "parameters": {
                    "type": "object",
                    "required": ["task_id"],
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID of the task to fetch"
                        }
                    }
                },
                "returns": {
                    "type": "object",
                    "description": "Task object or error if not found",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "completed": {"type": "boolean"},
                        "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                        "due_date": {"type": "string", "format": "date-time", "nullable": True}
                    }
                }
            },
            "add_task": {
                "name": "add_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (1-256 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["HIGH", "MEDIUM", "LOW"],
                            "description": "Task priority",
                            "default": "MEDIUM"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of tags/labels for the task (e.g., ['work', 'urgent'])"
                        },
                        "due_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Optional due date in YYYY-MM-DD format (e.g., '2024-03-15')",
                            "nullable": True
                        }
                    }
                },
                "returns": {
                    "type": "object",
                    "description": "Created task object",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "completed": {"type": "boolean"},
                        "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                        "due_date": {"type": "string", "format": "date-time", "nullable": True}
                    }
                }
            },
            "update_task": {
                "name": "update_task",
                "description": "Update fields for one task",
                "parameters": {
                    "type": "object",
                    "required": ["task_id"],
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["HIGH", "MEDIUM", "LOW"],
                            "description": "New priority"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "New list of tags/labels for the task"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Completion status"
                        },
                        "due_date": {
                            "type": "string",
                            "format": "date",
                            "description": "New due date in YYYY-MM-DD format",
                            "nullable": True
                        }
                    }
                },
                "returns": {
                    "type": "object",
                    "description": "Updated task object",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "completed": {"type": "boolean"},
                        "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                        "due_date": {"type": "string", "format": "date-time", "nullable": True}
                    }
                }
            },
            "delete_task": {
                "name": "delete_task",
                "description": "Soft delete a task. IMPORTANT: You must first call list_tasks to find the task_id by searching for the task name. Never guess or invent task IDs.",
                "parameters": {
                    "type": "object",
                    "required": ["task_id", "reason"],
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID of the task to soft delete. Must be obtained from list_tasks results."
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for deleting the task (required). Ask user for reason if not provided."
                        }
                    }
                },
                "returns": {
                    "type": "object",
                    "description": "Soft deleted task object",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "title": {"type": "string"},
                        "deleted_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "restore_task": {
                "name": "restore_task",
                "description": "Restore a soft-deleted task",
                "parameters": {
                    "type": "object",
                    "required": ["task_id"],
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID of the task to restore"
                        }
                    }
                },
                "returns": {
                    "type": "object",
                    "description": "Restored task object",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "title": {"type": "string"},
                        "deleted_at": {"type": "null"}
                    }
                }
            },
            "complete_task": {
                "name": "complete_task",
                "description": "Toggle completion status of a task",
                "parameters": {
                    "type": "object",
                    "required": ["task_id"],
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "UUID of the task to toggle completion"
                        }
                    }
                },
                "returns": {
                    "type": "object",
                    "description": "Task with updated completion status",
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "title": {"type": "string"},
                        "completed": {"type": "boolean"}
                    }
                }
            }
        }

        logger.info(f"Loaded {len(self._tools)} tool schemas")

    def get_tool_schemas(self) -> List[dict]:
        """Get all tool schemas."""
        return list(self._tools.values())

    def get_tool_schema(self, tool_name: str) -> Optional[dict]:
        """Get schema for specific tool."""
        return self._tools.get(tool_name)

    def get_openai_tool_definitions(self) -> List[Function]:
        """Get tool definitions in OpenAI format."""
        tools = []
        for tool_name, schema in self._tools.items():
            tool_def = {
                "type": "function",
                "function": {
                    "name": schema["name"],
                    "description": schema["description"],
                    "parameters": schema["parameters"]
                }
            }
            tools.append(tool_def)
        return tools

    def validate_tool_input(self, tool_name: str, input_data: Dict[str, Any]) -> bool:
        """
        Validate tool input against schema.

        Args:
            tool_name: Name of the tool
            input_data: Input parameters to validate

        Returns:
            True if valid, False otherwise
        """
        schema = self.get_tool_schema(tool_name)
        if not schema:
            logger.warning(f"Unknown tool: {tool_name}")
            return False

        # Basic validation - check required parameters
        required_params = schema.get("parameters", {}).get("required", [])
        for param in required_params:
            if param not in input_data:
                logger.warning(f"Missing required parameter: {param}")
                return False

        return True

    def generate_tool_response_example(self, tool_name: str) -> Dict[str, Any]:
        """Generate example response for a tool."""
        examples = {
            "list_tasks": {
                "tasks": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "priority": "MEDIUM",
                        "due_date": "2024-01-01T12:00:00Z"
                    }
                ]
            },
            "get_task": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "MEDIUM",
                "due_date": "2024-01-01T12:00:00Z"
            },
            "add_task": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "title": "New task",
                "description": "Task description",
                "completed": False,
                "priority": "MEDIUM",
                "due_date": None
            },
            "update_task": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Updated title",
                "description": "Updated description",
                "completed": True,
                "priority": "HIGH",
                "due_date": "2024-01-02T12:00:00Z"
            },
            "delete_task": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Deleted task",
                "deleted_at": "2024-01-01T12:00:00Z"
            },
            "restore_task": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Restored task",
                "deleted_at": None
            },
            "complete_task": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Completed task",
                "completed": True
            }
        }

        return examples.get(tool_name, {})


# Singleton instance
_registry_instance: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get singleton tool registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ToolRegistry()
    return _registry_instance