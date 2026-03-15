from collections.abc import Callable

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.ai.rag_service import answer_question
from app.core.security import require_authenticated_subject
from app.database.session import get_db
from app.models.ai_agent_action import AIAgentAction
from app.schemas.agent_action_schema import AgentActionItem
from app.schemas.ai_schema import AskRequest, AskResponse

router = APIRouter(prefix="/ai", tags=["AI"])


def get_rag_answer_service() -> Callable[[str], dict]:
    return answer_question


@router.post("/ask", response_model=AskResponse)
def ask_ai_endpoint(
    payload: AskRequest,
    rag_answer_service: Callable[[str], dict] = Depends(get_rag_answer_service),
    _: str = Depends(require_authenticated_subject),
) -> AskResponse:
    result = rag_answer_service(payload.question)
    return AskResponse(answer=result["answer"], sources=result["sources"])


@router.get("/agent-actions", response_model=list[AgentActionItem])
def list_agent_actions_endpoint(
    limit: int = Query(default=20, ge=1, le=100),
    agent_name: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    _: str = Depends(require_authenticated_subject),
    db: Session = Depends(get_db),
) -> list[AgentActionItem]:
    query = db.query(AIAgentAction)
    if agent_name:
        query = query.filter(AIAgentAction.agent_name == agent_name)
    if event_type:
        query = query.filter(AIAgentAction.event_type == event_type)
    return query.order_by(AIAgentAction.created_at.desc()).limit(limit).all()
