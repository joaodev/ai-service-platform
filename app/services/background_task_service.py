from sqlalchemy.orm import Session

from app.models.background_task import BackgroundTask

TASK_PENDING = "PENDING"
TASK_RUNNING = "RUNNING"
TASK_SUCCESS = "SUCCESS"
TASK_FAILED = "FAILED"


def create_task_record(
    db: Session,
    task_id: str,
    task_type: str,
    status: str,
    payload: dict,
) -> BackgroundTask:
    task = BackgroundTask(
        id=task_id,
        task_type=task_type,
        status=status,
        payload=payload,
        result=None,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_record(db: Session, task_id: str) -> BackgroundTask | None:
    return db.query(BackgroundTask).filter(BackgroundTask.id == task_id).first()


def update_task_record(
    db: Session,
    task_id: str,
    status: str,
    result: dict | None = None,
) -> BackgroundTask | None:
    task = get_task_record(db, task_id)
    if not task:
        return None

    task.status = status
    task.result = result
    db.commit()
    db.refresh(task)
    return task
