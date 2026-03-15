from celery import Celery
from kombu import Queue

from app.core.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "ai_service_platform",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.task_queues = (
    Queue("default"),
    Queue("ai_tasks"),
    Queue("events"),
    Queue("webhooks"),
)

celery_app.conf.task_routes = {
    "app.workers.tasks.generate_embeddings_task": {"queue": "ai_tasks"},
    "app.workers.tasks.process_event_task": {"queue": "events"},
    "app.workers.tasks.evaluate_agents_task": {"queue": "ai_tasks"},
    "app.workers.tasks.send_webhook_task": {"queue": "webhooks"},
    "app.workers.tasks.ai_agent_execution_task": {"queue": "ai_tasks"},
}

celery_app.conf.task_default_queue = "default"
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

app = celery_app
