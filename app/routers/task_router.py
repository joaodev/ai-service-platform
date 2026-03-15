from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.task_schema import TaskStatusResponse
from app.services.background_task_service import get_task_record

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])


@router.get("/{task_id}", response_model=TaskStatusResponse)
def get_task_status_endpoint(task_id: str, db: Session = Depends(get_db)) -> TaskStatusResponse:
    task = get_task_record(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskStatusResponse.model_validate(task)
