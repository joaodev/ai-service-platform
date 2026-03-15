# Async Tasks and Workers

## Why async tasks exist

The API offloads long-running operations (AI agent execution, embeddings, event fanout, webhook delivery) to Celery workers so HTTP requests remain fast.

## Queues

Defined queues:

- `default`
- `ai_tasks`
- `events`
- `webhooks`

Task routing is configured in `app/workers/celery_app.py`.

## Task lifecycle

Background tasks are tracked in the database using statuses:

- `PENDING`
- `RUNNING`
- `SUCCESS`
- `FAILED`

Lifecycle pattern inside worker tasks:

1. Mark task as `RUNNING`.
2. Execute business operation.
3. Persist result and mark `SUCCESS`.
4. On error, persist error payload and mark `FAILED`.

## Client polling contract

For async endpoints (example: `POST /ai/agent`):

1. Call endpoint and capture returned `task_id`.
2. Poll `GET /tasks/{task_id}`.
3. Stop polling when status is terminal (`SUCCESS` or `FAILED`).

Suggested polling interval: 1–3 seconds with timeout/retry policy on client side.

## Running workers locally

```bash
PYTHONPATH=. /home/joao/projects/ai-service-platform/.venv/bin/python -m celery -A app.workers.celery_app:celery_app worker -Q default,ai_tasks,events,webhooks --loglevel=info
```

Or use:

```bash
bash scripts/start_workers.sh
```
