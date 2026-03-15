# API Overview

## What this service does

`ai-service-platform` is a FastAPI backend that combines:

- core business domains (customers, suppliers, products, services)
- operations and support domains (tickets, work orders, wallets, finance)
- AI capabilities (RAG Q&A and agent execution)
- event/webhook and background-task processing

## Runtime architecture

The platform runs with these components:

- **FastAPI app** (`app/main.py`): receives HTTP requests and exposes REST endpoints.
- **PostgreSQL**: stores domain data, users, tasks, logs, and AI metadata.
- **Redis**: Celery broker/result backend.
- **Celery worker** (`app/workers/celery_app.py` + `app/workers/tasks.py`): executes async jobs.

## Request lifecycle

Typical synchronous request:

1. Request enters a router under `app/routers/` or `app/ai/agent_router.py`.
2. FastAPI dependencies inject DB session (`get_db`) and optional auth checks.
3. Router calls service-layer functions under `app/services/` (or AI/event modules).
4. SQLAlchemy models are queried/updated.
5. Response schemas are returned to client.

Typical async request (`POST /ai/agent`):

1. Endpoint validates JWT and resolves current user.
2. A Celery task is enqueued (`ai_agent_execution_task`) on queue `ai_tasks`.
3. A task record is persisted with status `PENDING`.
4. Client polls `GET /tasks/{task_id}` until completion.

## Main modules

- `app/routers/`: domain and integration endpoints.
- `app/core/security.py`: password hashing, JWT creation/validation, auth dependencies.
- `app/ai/`: RAG and agent orchestration utilities.
- `app/events/`: event message and webhook orchestration.
- `app/workers/`: Celery app and background task definitions.
