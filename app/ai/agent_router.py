from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.agent_schema import AgentRequest, AgentResponse
from app.services.background_task_service import TASK_PENDING, create_task_record
from app.workers.celery_app import celery_app

router = APIRouter(prefix="/ai", tags=["AI Agent"])


@router.post("/agent", response_model=AgentResponse)
def ai_agent_endpoint(
    payload: AgentRequest,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> AgentResponse:
    async_result = celery_app.send_task(
        "app.workers.tasks.ai_agent_execution_task",
        kwargs={
            "user_id": current_user.id,
            "message": payload.message,
            "session_id": payload.session_id,
        },
        queue="ai_tasks",
    )
    create_task_record(
        db=db,
        task_id=async_result.id,
        task_type="ai_agent_execution",
        status=TASK_PENDING,
        payload={
            "user_id": current_user.id,
            "message": payload.message,
            "session_id": payload.session_id,
        },
    )
    return AgentResponse(task_id=async_result.id, status=TASK_PENDING)
