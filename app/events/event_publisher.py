from sqlalchemy.orm import Session

from app.events.event_service import log_event
from app.services.background_task_service import TASK_PENDING, create_task_record
from app.workers.celery_app import celery_app


def publish_event(event_type: str, payload: dict, db: Session) -> None:
    log_event(db=db, event_type=event_type, payload=payload)
    async_result = celery_app.send_task(
        "app.workers.tasks.process_event_task",
        kwargs={"event_type": event_type, "payload": payload},
        queue="events",
    )
    create_task_record(
        db=db,
        task_id=async_result.id,
        task_type="process_event",
        status=TASK_PENDING,
        payload={"event_type": event_type, "payload": payload},
    )

    agent_result = celery_app.send_task(
        "app.workers.tasks.evaluate_agents_task",
        kwargs={"event_type": event_type, "payload": payload},
        queue="ai_tasks",
    )
    create_task_record(
        db=db,
        task_id=agent_result.id,
        task_type="evaluate_agents",
        status=TASK_PENDING,
        payload={"event_type": event_type, "payload": payload},
    )
