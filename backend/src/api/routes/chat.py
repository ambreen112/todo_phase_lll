"""Chat API route for AI agent conversations."""

from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ...api.deps import get_current_user, get_session
from ...core.security import TokenData
from ...models.conversation import Conversation, ChatMessage
from ...agents.main_agent import TodoAgent
from ...agents.message_preprocessor import preprocess_message
from ...agents.tool_executor import ToolExecutor

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class ToolCallInfo(BaseModel):
    """Tool call information."""
    tool_name: str
    input: dict
    output: Optional[dict] = None


class MessageInfo(BaseModel):
    """Message information for response."""
    role: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    """Chat response schema."""
    success: bool
    conversation_id: str
    agent_response: str
    tool_calls: List[ToolCallInfo] = []
    messages: List[MessageInfo] = []


class ChatErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error: str


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ChatErrorResponse},
        401: {"model": ChatErrorResponse},
        408: {"model": ChatErrorResponse},
        500: {"model": ChatErrorResponse},
    }
)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Process a chat message with the Todo AI Agent.

    - Fetches or creates conversation
    - Sends message to agent with history context
    - Returns agent response and tool calls
    """
    # Validate user_id matches authenticated user
    if str(current_user.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID mismatch"
        )

    try:
        # Get or create conversation
        conversation = None
        if request.conversation_id:
            try:
                conv_uuid = UUID(request.conversation_id)
                statement = select(Conversation).where(
                    Conversation.id == conv_uuid,
                    Conversation.user_id == current_user.user_id
                )
                conversation = session.exec(statement).first()
            except ValueError:
                pass

        if not conversation:
            conversation = Conversation(
                user_id=current_user.user_id,
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Fetch conversation history (last 20 messages)
        history_statement = select(ChatMessage).where(
            ChatMessage.conversation_id == conversation.id
        ).order_by(ChatMessage.created_at.desc()).limit(20)
        history_messages = list(session.exec(history_statement).all())
        history_messages.reverse()  # Oldest first

        # Build conversation history for agent
        conversation_history = []
        for msg in history_messages:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Save user message
        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        session.add(user_message)
        session.commit()

        # Preprocess message to detect patterns that AI might misinterpret
        processed_message, direct_action = preprocess_message(
            request.message,
            current_user.user_id,
            session
        )

        # If preprocessor detected a direct action (e.g., update by task name)
        if direct_action:
            # Execute the action directly using tool executor
            tool_executor = ToolExecutor(str(current_user.user_id))

            if direct_action["action"] == "update_task":
                # Build update arguments
                update_args = {
                    "task_id": direct_action["task_id"],
                    direct_action["field"]: direct_action["value"]
                }
                tool_result = tool_executor.execute("update_task", update_args)

                if "error" in tool_result:
                    response_content = f"Sorry, I couldn't update the task: {tool_result['error']}"
                else:
                    response_content = f"Done! I updated task '{direct_action['task_title']}' - set {direct_action['field']} to '{direct_action['value']}'."

                result = {
                    "content": response_content,
                    "tool_calls": [{
                        "function": {
                            "name": "update_task",
                            "arguments": update_args
                        },
                        "result": tool_result
                    }]
                }

            elif direct_action["action"] == "delete_task":
                # Build delete arguments
                delete_args = {
                    "task_id": direct_action["task_id"],
                    "reason": direct_action["reason"]
                }
                tool_result = tool_executor.execute("delete_task", delete_args)

                if "error" in tool_result:
                    response_content = f"Sorry, I couldn't delete the task: {tool_result['error']}"
                else:
                    response_content = f"Done! Task '{direct_action['task_title']}' has been deleted. Reason: {direct_action['reason']}"

                result = {
                    "content": response_content,
                    "tool_calls": [{
                        "function": {
                            "name": "delete_task",
                            "arguments": delete_args
                        },
                        "result": tool_result
                    }]
                }

            elif direct_action["action"] == "add_task":
                # Build add task arguments
                add_args = {
                    "title": direct_action["title"],
                    "priority": direct_action.get("priority", "MEDIUM"),
                }
                if direct_action.get("tags"):
                    add_args["tags"] = direct_action["tags"]
                if direct_action.get("due_date"):
                    add_args["due_date"] = direct_action["due_date"]

                tool_result = tool_executor.execute("add_task", add_args)

                if "error" in tool_result:
                    response_content = f"Sorry, I couldn't create the task: {tool_result['error']}"
                else:
                    response_content = f"Done! Created task '{direct_action['title']}' with {direct_action.get('priority', 'MEDIUM')} priority."
                    if direct_action.get("tags"):
                        response_content += f" Tags: {', '.join(direct_action['tags'])}."
                    if direct_action.get("due_date"):
                        response_content += f" Due: {direct_action['due_date']}."

                result = {
                    "content": response_content,
                    "tool_calls": [{
                        "function": {
                            "name": "add_task",
                            "arguments": add_args
                        },
                        "result": tool_result
                    }]
                }

            else:
                # Unknown action, fall through to AI
                direct_action = None

        # If no direct action, use the AI agent
        if not direct_action:
            # Initialize agent and process message
            agent = TodoAgent()
            result = agent.process_message(
                user_message=request.message,
                conversation_history=conversation_history if conversation_history else None,
                conversation_id=str(conversation.id),
                user_id=str(current_user.user_id)  # Inject user_id for tool execution
            )

        # Save assistant response
        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=result.get("content", "")
        )
        session.add(assistant_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        session.add(conversation)
        session.commit()

        # Build tool calls response
        tool_calls = []
        for tc in result.get("tool_calls", []):
            args = tc.get("function", {}).get("arguments", {})
            # Handle case where arguments might be a string (JSON) or already a dict
            if isinstance(args, str):
                try:
                    import json
                    args = json.loads(args)
                except (json.JSONDecodeError, TypeError):
                    args = {}
            tool_calls.append(ToolCallInfo(
                tool_name=tc.get("function", {}).get("name", ""),
                input=args if isinstance(args, dict) else {},
                output=tc.get("result") if "result" in tc else None
            ))

        # Get last 10 messages for response
        recent_statement = select(ChatMessage).where(
            ChatMessage.conversation_id == conversation.id
        ).order_by(ChatMessage.created_at.desc()).limit(10)
        recent_messages = list(session.exec(recent_statement).all())
        recent_messages.reverse()

        messages = [
            MessageInfo(
                role=msg.role,
                content=msg.content,
                timestamp=msg.created_at.isoformat()
            )
            for msg in recent_messages
        ]

        return ChatResponse(
            success=True,
            conversation_id=str(conversation.id),
            agent_response=result.get("content", ""),
            tool_calls=tool_calls,
            messages=messages
        )

    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Chat error: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"CHAT ERROR: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """List all conversations for a user."""
    if str(current_user.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID mismatch"
        )

    statement = select(Conversation).where(
        Conversation.user_id == current_user.user_id
    ).order_by(Conversation.updated_at.desc())
    conversations = session.exec(statement).all()

    return {
        "conversations": [
            {
                "id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]
    }


@router.get("/{user_id}/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    user_id: str,
    conversation_id: str,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """Get messages for a specific conversation."""
    if str(current_user.user_id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID mismatch"
        )

    try:
        conv_uuid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )

    # Verify conversation belongs to user
    conv_statement = select(Conversation).where(
        Conversation.id == conv_uuid,
        Conversation.user_id == current_user.user_id
    )
    conversation = session.exec(conv_statement).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get all messages
    messages_statement = select(ChatMessage).where(
        ChatMessage.conversation_id == conv_uuid
    ).order_by(ChatMessage.created_at.asc())
    messages = session.exec(messages_statement).all()

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }
