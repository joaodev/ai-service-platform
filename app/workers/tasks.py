from app.ai.agent import run_agent
from app.ai.ingestion_service import process_event_for_ingestion, store_knowledge_document
from app.agents.agent_runner import run_agents_for_event
from app.database.session import SessionLocal
from app.events.event_service import build_event_message, get_active_webhook_targets
from app.integrations.webhook_dispatcher import dispatch_webhook
from app.models.user import User
from app.services.background_task_service import (
    TASK_FAILED,
    TASK_PENDING,
    TASK_RUNNING,
    TASK_SUCCESS,
    create_task_record,
    update_task_record,
)
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.generate_embeddings_task", bind=True)
def generate_embeddings_task(self, content: str, metadata: dict) -> dict:
    db = SessionLocal()
    try:
        update_task_record(db, self.request.id, TASK_RUNNING)
        document = store_knowledge_document(db=db, content=content, metadata=metadata)
        result = {"knowledge_document_id": document.id}
        update_task_record(db, self.request.id, TASK_SUCCESS, result)
        return result
    except Exception as exc:
        update_task_record(db, self.request.id, TASK_FAILED, {"error": str(exc)})
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.process_event_task", bind=True)
def process_event_task(self, event_type: str, payload: dict) -> dict:
    db = SessionLocal()
    try:
        update_task_record(db, self.request.id, TASK_RUNNING)

        process_event_for_ingestion(event_type=event_type, payload=payload)
        target_urls = get_active_webhook_targets(db=db, event_type=event_type)

        dispatched_task_ids: list[str] = []
        if target_urls:
            event_message = build_event_message(event_type=event_type, payload=payload)
            for target_url in target_urls:
                webhook_task = send_webhook_task.apply_async(
                    kwargs={"target_url": target_url, "event_message": event_message},
                    queue="webhooks",
                )
                create_task_record(
                    db=db,
                    task_id=webhook_task.id,
                    task_type="send_webhook",
                    status=TASK_PENDING,
                    payload={"target_url": target_url, "event_type": event_type},
                )
                dispatched_task_ids.append(webhook_task.id)

        result = {
            "event_type": event_type,
            "webhooks_dispatched": len(target_urls),
            "webhook_task_ids": dispatched_task_ids,
        }
        update_task_record(db, self.request.id, TASK_SUCCESS, result)
        return result
    except Exception as exc:
        update_task_record(db, self.request.id, TASK_FAILED, {"error": str(exc)})
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.evaluate_agents_task", bind=True)
def evaluate_agents_task(self, event_type: str, payload: dict) -> dict:
    db = SessionLocal()
    try:
        update_task_record(db, self.request.id, TASK_RUNNING)
        result = run_agents_for_event(db=db, event_type=event_type, payload=payload)
        update_task_record(db, self.request.id, TASK_SUCCESS, result)
        return result
    except Exception as exc:
        update_task_record(db, self.request.id, TASK_FAILED, {"error": str(exc)})
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.send_webhook_task", bind=True)
def send_webhook_task(self, target_url: str, event_message: dict) -> dict:
    db = SessionLocal()
    try:
        update_task_record(db, self.request.id, TASK_RUNNING)
        dispatch_webhook(target_url=target_url, event_message=event_message)
        result = {"target_url": target_url, "dispatched": True}
        update_task_record(db, self.request.id, TASK_SUCCESS, result)
        return result
    except Exception as exc:
        update_task_record(db, self.request.id, TASK_FAILED, {"error": str(exc)})
        raise
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.ai_agent_execution_task", bind=True)
def ai_agent_execution_task(
    self, user_id: int, message: str, session_id: str | None = None
) -> dict:
    db = SessionLocal()
    try:
        update_task_record(db, self.request.id, TASK_RUNNING)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            result = {"error": "User not found"}
            update_task_record(db, self.request.id, TASK_FAILED, result)
            return result

        response = run_agent(db=db, user=user, message=message, session_id=session_id)
        update_task_record(db, self.request.id, TASK_SUCCESS, response)
        return response
    except Exception as exc:
        update_task_record(db, self.request.id, TASK_FAILED, {"error": str(exc)})
        raise
    finally:
        db.close()
