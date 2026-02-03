"""Main Todo AI Agent implementation."""

import json
import logging
import re
from typing import Dict, Any, Optional, List
from openai.types.chat import ChatCompletionMessageParam

from .openai_client import get_openai_client
from .system_prompt import get_system_prompt
from .tool_registry import get_tool_registry
from .tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


def clean_response_content(content: str) -> str:
    """
    Remove any JSON blocks or raw function calls from the response content.

    This ensures the user only sees natural language responses.
    """
    if not content:
        return content

    # Remove JSON code blocks (```json ... ```)
    content = re.sub(r'```json\s*\n?.*?\n?```', '', content, flags=re.DOTALL)

    # Remove generic code blocks that contain JSON
    content = re.sub(r'```\s*\n?\{.*?\}\s*\n?```', '', content, flags=re.DOTALL)

    # Remove standalone JSON objects that look like function calls
    # Pattern: {"type": "function", ...} or {"name": "...", "arguments": ...}
    json_pattern = r'\{\s*"(?:type|name)":\s*"(?:function|add_task|list_tasks|get_task|update_task|delete_task|restore_task|complete_task)"[^}]*(?:\{[^}]*\}[^}]*)?\}'
    content = re.sub(json_pattern, '', content, flags=re.DOTALL)

    # Remove any remaining JSON-like structures at the start of the response
    # This catches cases where the LLM outputs JSON before natural language
    lines = content.split('\n')
    cleaned_lines = []
    skip_json = False

    for line in lines:
        stripped = line.strip()
        # Skip lines that are just JSON
        if stripped.startswith('{') and stripped.endswith('}'):
            try:
                json.loads(stripped)
                continue  # Skip valid JSON lines
            except json.JSONDecodeError:
                pass
        # Skip lines that look like they're part of a JSON block
        if stripped == '{' or stripped == '}':
            skip_json = not skip_json if stripped == '{' else False
            continue
        if skip_json:
            continue
        cleaned_lines.append(line)

    content = '\n'.join(cleaned_lines)

    # Clean up extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()

    return content


class TodoAgent:
    """Main Todo AI Agent class."""

    def __init__(self, max_turns: int = 5):
        """
        Initialize Todo AI Agent.

        Args:
            max_turns: Maximum number of tool calls per conversation turn
        """
        self.max_turns = max_turns
        self.client = get_openai_client()
        self.model = self.client.model  # Use model from client config
        self.system_prompt = get_system_prompt()
        self.tool_registry = get_tool_registry()

        logger.info(f"TodoAgent initialized with model: {self.model}, max_turns: {self.max_turns}")

    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatCompletionMessageParam]] = None,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate agent response.

        Args:
            user_message: User's input message
            conversation_history: Previous conversation messages
            conversation_id: ID for conversation tracking
            user_id: User ID for tool execution (required for tool calls)

        Returns:
            Dictionary containing response and metadata
        """
        logger.info(f"Processing message for conversation: {conversation_id}, user: {user_id}")

        # Build messages array with system prompt and conversation history
        messages = self._build_messages(user_message, conversation_history)

        # Get tool definitions
        tools = self.tool_registry.get_openai_tool_definitions()

        # Initialize tool executor if user_id provided
        tool_executor = ToolExecutor(user_id) if user_id else None

        try:
            # Agentic loop: keep processing until no more tool calls
            all_tool_calls = []
            turn_count = 0

            while turn_count < self.max_turns:
                turn_count += 1
                logger.info(f"Agent turn {turn_count}/{self.max_turns}")

                response = self.client.create_chat_completion(
                    messages=messages,
                    tools=tools
                )

                if not response.choices:
                    raise ValueError("No response choices returned from LLM")

                message = response.choices[0].message

                # Log what the LLM returned
                logger.info(f"LLM response - content: {message.content[:200] if message.content else 'None'}...")
                logger.info(f"LLM response - tool_calls: {message.tool_calls}")

                # Check if there are tool calls to execute
                if message.tool_calls and tool_executor:
                    # Add assistant message with tool calls to conversation
                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in message.tool_calls
                        ]
                    })

                    # Execute each tool call and collect results
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}

                        logger.info(f"Executing tool: {tool_name}")

                        # Execute the tool
                        tool_result = tool_executor.execute(tool_name, arguments)

                        # Track tool calls for response
                        all_tool_calls.append({
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": arguments
                            },
                            "result": tool_result
                        })

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result)
                        })

                    # Continue loop to get LLM's response to tool results
                    continue

                # No tool calls - we have final response
                # Clean the response to remove any JSON artifacts
                cleaned_content = clean_response_content(message.content or "")

                result = {
                    "content": cleaned_content,
                    "role": message.role,
                    "tool_calls": all_tool_calls,
                    "conversation_id": conversation_id,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }

                logger.info(f"Agent response generated successfully after {turn_count} turns")
                return result

            # Max turns reached
            logger.warning(f"Max turns ({self.max_turns}) reached")
            return {
                "content": "I completed the requested actions. Is there anything else you'd like me to help with?",
                "role": "assistant",
                "tool_calls": all_tool_calls,
                "conversation_id": conversation_id,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }

        except Exception as e:
            logger.error(f"Agent processing failed: {str(e)}")
            return self._create_error_response(str(e), conversation_id)

    def _build_messages(
        self,
        user_message: str,
        conversation_history: Optional[List[ChatCompletionMessageParam]]
    ) -> List[ChatCompletionMessageParam]:
        """Build messages array for OpenAI API."""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _process_response(self, response, messages: List[ChatCompletionMessageParam]) -> Dict[str, Any]:
        """Process OpenAI response and extract relevant information."""
        if not response.choices:
            raise ValueError("No response choices returned from OpenAI")

        message = response.choices[0].message

        result = {
            "content": message.content or "",
            "role": message.role,
            "tool_calls": [],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        }

        # Extract tool calls if present
        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                }
                for call in message.tool_calls
            ]

        return result

    def _create_error_response(self, error_message: str, conversation_id: Optional[str]) -> Dict[str, Any]:
        """Create error response for failed processing."""
        return {
            "content": f"I encountered an error while processing your request: {error_message}"
                     "\n\nPlease try again or contact support if the issue persists.",
            "role": "assistant",
            "tool_calls": [],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "conversation_id": conversation_id,
            "error": True
        }

    def validate_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """Validate tool call before execution."""
        return self.tool_registry.validate_tool_input(tool_name, arguments)

    def get_supported_tools(self) -> List[str]:
        """Get list of supported tool names."""
        return list(self.tool_registry.get_tool_registry()._tools.keys())

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent configuration information."""
        return {
            "model": self.model,
            "max_turns": self.max_turns,
            "supported_tools": self.get_supported_tools(),
            "system_prompt_length": len(self.system_prompt)
        }


# Singleton instance
_agent_instance: Optional[TodoAgent] = None


def get_todo_agent(max_turns: int = 5) -> TodoAgent:
    """Get singleton TodoAgent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TodoAgent(max_turns=max_turns)
    return _agent_instance


def reset_agent() -> None:
    """Reset the singleton agent instance."""
    global _agent_instance
    _agent_instance = None