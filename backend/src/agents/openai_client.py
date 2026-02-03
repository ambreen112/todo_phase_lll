"""OpenAI client configuration for OpenRouter integration."""

from typing import Optional
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_message_tool_call_param import Function
import logging

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI client configured for OpenRouter with Claude models."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenAI client for OpenRouter.

        Args:
            api_key: OpenRouter API key (defaults to settings)
            base_url: OpenRouter base URL (defaults to settings)
        """
        settings = get_settings()

        self.api_key = api_key or settings.openai_api_key
        self.base_url = base_url or settings.openai_base_url

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        self.model = settings.openai_model
        self.max_tokens = 4000
        self.temperature = 0.1

        logger.info(f"OpenAI client initialized with base URL: {self.base_url}")

    def create_chat_completion(
        self,
        messages: list[ChatCompletionMessageParam],
        tools: Optional[list[Function]] = None,
        max_turns: int = 5,
        **kwargs
    ):
        """
        Create a chat completion.

        Args:
            messages: List of messages in conversation
            tools: List of tool definitions
            max_turns: Maximum number of tool calls allowed
            **kwargs: Additional parameters for chat completion

        Returns:
            OpenAI chat completion response
        """
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }

        if tools:
            params["tools"] = tools
            params["max_tokens"] = 8000  # Increase for tool calls

        try:
            response = self.client.chat.completions.create(**params)
            return response
        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}")
            raise

    def create_simple_chat(
        self,
        system_prompt: str,
        user_message: str,
        **kwargs
    ):
        """
        Create a simple chat with system and user messages.

        Args:
            system_prompt: System message content
            user_message: User message content
            **kwargs: Additional parameters

        Returns:
            Response content as string
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.create_chat_completion(messages, **kwargs)

        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content

        return ""

    def get_available_models(self) -> list[str]:
        """
        Get list of available models from OpenRouter.

        Returns:
            List of model names
        """
        try:
            models_response = self.client.models.list()
            return [model.id for model in models_response.data]
        except Exception as e:
            logger.warning(f"Failed to fetch models: {str(e)}")
            # Return default Claude models
            return [
                "claude-3.5-sonnet-20241022",
                "claude-3-haiku-20240307",
                "claude-3-opus-20240229"
            ]


# Singleton instance
_client_instance: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """Get singleton OpenAI client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAIClient()
    return _client_instance