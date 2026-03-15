from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import AIMessage, BaseMessage
from sqlalchemy.orm import Session

from app.ai.agent_tools import get_agent_tools
from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)
from app.models.ai_agent_log import AIAgentLog
from app.models.user import User

_MEMORY_STORE: dict[str, list[dict[str, str]]] = {}


def _get_or_create_memory(memory_key: str) -> list[dict[str, str]]:
    memory = _MEMORY_STORE.get(memory_key)
    if memory is None:
        memory = []
        _MEMORY_STORE[memory_key] = memory
    return memory


def _extract_actions(messages: list[BaseMessage]) -> list[dict]:
    actions: list[dict] = []
    for message in messages:
        if isinstance(message, AIMessage) and getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                actions.append(
                    {
                        "tool": call.get("name"),
                        "tool_input": call.get("args", {}),
                    }
                )
    return actions


def _build_agent(db: Session, user: User):
    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        deployment_name=AZURE_OPENAI_CHAT_DEPLOYMENT,
        temperature=0.1,
    )

    tools = get_agent_tools(db=db, user=user)
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are an administrative assistant for a service platform. "
            "Use tools when needed. Respect permissions and do not execute "
            "administrative operations for client users."
        ),
    )
    return agent


def log_agent_action(
    db: Session,
    user_id: int,
    input_message: str,
    actions_taken: list[dict],
    response: str,
) -> AIAgentLog:
    log = AIAgentLog(
        user_id=user_id,
        input_message=input_message,
        actions_taken=actions_taken,
        response=response,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def run_agent(db: Session, user: User, message: str, session_id: str | None = None) -> dict:
    if not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY and AZURE_OPENAI_CHAT_DEPLOYMENT):
        fallback = "AI agent is not configured. Please set Azure OpenAI environment variables."
        log_agent_action(db, user.id, message, [], fallback)
        return {"agent_response": fallback, "actions_executed": []}

    memory_key = f"{user.id}:{session_id or 'default'}"
    history = _get_or_create_memory(memory_key)
    agent = _build_agent(db=db, user=user)
    payload_messages = [*history, {"role": "user", "content": message}]
    result = agent.invoke({"messages": payload_messages})
    result_messages = result.get("messages", [])
    actions_executed = _extract_actions(result_messages)

    response_text = ""
    for response_message in reversed(result_messages):
        if isinstance(response_message, AIMessage) and response_message.content:
            response_text = str(response_message.content)
            break

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response_text})

    log_agent_action(
        db=db,
        user_id=user.id,
        input_message=message,
        actions_taken=actions_executed,
        response=response_text,
    )

    return {
        "agent_response": response_text,
        "actions_executed": actions_executed,
    }
