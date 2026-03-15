# ai-service-platform

FastAPI backend foundation for a modular SaaS platform.

## Documentation

- API docs index: `docs/README.md`
- API overview: `docs/overview.md`
- Endpoint reference: `docs/api-reference.md`
- Authentication: `docs/authentication.md`
- Async workers/tasks: `docs/async-tasks.md`
- Postman quickstart: `docs/postman-guide.md`

## Requirements

- Python 3.11+
- Docker + Docker Compose

## 1) Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2) Install dependencies

```bash
pip install -r requirements.txt
```

## Testing and Quality

The project includes a full automated test stack with:

- `pytest` for unit, integration, and AI tests
- `testcontainers` for ephemeral PostgreSQL test databases
- `httpx` async API clients
- mocked AI boundaries so tests never call Azure OpenAI
- `black` and `ruff` for CI quality gates

### Run the Test Suite

```bash
pytest
```

### Run Only One Layer

```bash
pytest tests/unit
pytest tests/integration
pytest tests/ai
```

### Lint and Format Checks

```bash
black --check app tests scripts
ruff check app tests scripts
```

### Test Database Strategy

Tests use `testcontainers` to start an isolated `pgvector/pgvector:pg15` PostgreSQL container, apply Alembic migrations, and destroy the container after the suite finishes. This allows API, database, RAG, and event-driven tests to run against a real disposable database instead of the local development instance.

### GitHub Actions

CI runs automatically on every push and pull request through [.github/workflows/tests.yml](/home/joao/projects/ai-service-platform/.github/workflows/tests.yml). The pipeline installs dependencies, runs `black --check`, runs `ruff check`, and then executes `pytest`.

## 3) Start PostgreSQL and Redis with Docker Compose

```bash
docker compose up -d
```

## 4) Run initial migration

```bash
alembic upgrade head
```

## 5) Start FastAPI application

```bash
uvicorn app.main:app --reload
```

## 6) Start Celery worker

```bash
PYTHONPATH=. /home/joao/projects/ai-service-platform/.venv/bin/python -m celery -A app.workers.celery_app:celery_app worker -Q default,ai_tasks,events,webhooks --loglevel=info
```

### One-Command Local Startup (API + Worker + Infrastructure)

```bash
bash scripts/start_workers.sh
```

Runtime logs and PIDs are written under `.runtime/`.

### Stop Local API + Worker

```bash
bash scripts/stop_workers.sh
```

### Known Local Startup Issues

If `uvicorn` or `celery` exits with code `1`, check the following in order:

1. Infrastructure is up:

```bash
docker compose up -d
docker compose ps
```

2. Migrations are current:

```bash
/home/joao/projects/ai-service-platform/.venv/bin/python -m alembic upgrade head
```

3. API process error details:

```bash
PYTHONPATH=. /home/joao/projects/ai-service-platform/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. Worker process error details:

```bash
PYTHONPATH=. /home/joao/projects/ai-service-platform/.venv/bin/python -m celery -A app.workers.celery_app:celery_app worker -Q default,ai_tasks,events,webhooks --loglevel=info
```

5. Confirm required env vars (`DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, and AI settings) are set for the same shell session.

If you are using the helper scripts, inspect `.runtime/` logs after `bash scripts/start_workers.sh`.

## Access

- http://localhost:8000
- http://localhost:8000/docs

## Azure Deployment Readiness

This project is prepared for Azure Container Apps with separate containers for:

- API (`Dockerfile`)
- Worker (`Dockerfile.worker`)

### Required Environment Variables

- `DATABASE_URL`
- `REDIS_URL`
- `OPENAI_API_KEY`
- `JWT_SECRET`

Compatible aliases are supported:

- `AZURE_OPENAI_API_KEY` (fallback alias for `OPENAI_API_KEY`)
- `JWT_SECRET_KEY` (fallback alias for `JWT_SECRET`)

### Local Containerized Stack

```bash
docker compose up -d --build
```

### API Health Check

```bash
curl http://localhost:8000/health
```

Expected:

```json
{
	"status": "ok"
}
```

### Azure Container Apps Topology

- Deploy API container as one Container App (ingress enabled on port `8000`).
- Deploy worker container as a separate Container App (ingress disabled).
- Use Azure Database for PostgreSQL and Azure Cache for Redis in production.
- Send container stdout/stderr logs to Azure Monitor (JSON logs already enabled by app logging setup).

### Automated Azure Deployment Script

Script:

- `scripts/deploy_azure_container_apps.sh`
- `scripts/azure.env.example` (environment variables template)

Make executable:

```bash
chmod +x scripts/deploy_azure_container_apps.sh
```

Required environment variables before execution:

- `RESOURCE_GROUP`
- `LOCATION`
- `ACR_NAME`
- `CONTAINERAPPS_ENV`
- `API_APP_NAME`
- `WORKER_APP_NAME`
- `DATABASE_URL`
- `REDIS_URL`
- `OPENAI_API_KEY`
- `JWT_SECRET`

Optional overrides:

- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

Run deployment:

```bash
cp scripts/azure.env.example scripts/azure.env
# edit scripts/azure.env with your real values
source scripts/azure.env
bash scripts/deploy_azure_container_apps.sh
```

What it does:

- Ensures Resource Group, ACR, and Container Apps Environment exist.
- Builds and pushes API/Worker images to ACR.
- Creates or updates API Container App (external ingress, port 8000).
- Creates or updates Worker Container App (no ingress).

## Authentication Endpoints

- `POST /auth/login` to receive JWT token (public)
- `POST /users` to create a user (authenticated, ADMIN only)

## Quick API Payloads

Use these examples in `http://localhost:8000/docs`.

### Auth

`POST /users`

```json
{
	"name": "Admin User",
	"email": "admin@example.com",
	"password": "strong_password",
	"role_name": "ADMIN"
}
```

`POST /auth/login`

```json
{
	"email": "admin@example.com",
	"password": "strong_password"
}
```

### Customers and Suppliers

`POST /customers`

```json
{
	"name": "Acme Customer",
	"email": "customer@example.com",
	"phone": "+55 11 99999-0000",
	"document_number": "12345678901"
}
```

`POST /suppliers`

```json
{
	"name": "Global Supplier",
	"email": "supplier@example.com",
	"phone": "+55 11 98888-0000",
	"document_number": "10987654321"
}
```

### Catalog

`POST /products`

```json
{
	"name": "Router",
	"description": "Dual-band router",
	"price": 299.90
}
```

`POST /services`

```json
{
	"name": "Installation",
	"description": "On-site installation service",
	"base_price": 150.00
}
```

### Support and Operations

`POST /tickets`

```json
{
	"title": "Internet outage",
	"description": "No connection since morning",
	"status": "OPEN",
	"priority": "HIGH",
	"customer_id": 1
}
```

Authentication is required for all internal business and AI routes.

Public/bootstrap endpoints:

- `GET /`
- `GET /health`
- `POST /auth/login`

`POST /work-orders`

```json
{
	"ticket_id": 1,
	"assigned_user_id": 1,
	"status": "CREATED",
	"started_at": null,
	"finished_at": null
}
```

### Wallet and Ledger

`POST /wallets`

```json
{
	"user_id": 1
}
```

`POST /wallets/transactions`

```json
{
	"wallet_id": 1,
	"type": "DEPOSIT",
	"amount": 500.00,
	"description": "Initial credit"
}
```

### Finance

`POST /finance/accounts-payable`

```json
{
	"supplier_id": 1,
	"description": "Cloud invoice",
	"amount": 1200.00,
	"due_date": "2026-04-10",
	"status": "PENDING"
}
```

`POST /finance/accounts-receivable`

```json
{
	"customer_id": 1,
	"description": "Monthly subscription",
	"amount": 299.90,
	"due_date": "2026-04-05",
	"status": "PENDING"
}
```

## First-Run Test Flow

Use this order to validate dependencies between modules:

1. Seed admin user: `PYTHONPATH=. /home/joao/projects/ai-service-platform/.venv/bin/python scripts/seed_admin_user.py`
2. Login and copy token: `POST /auth/login`
3. Create customer and supplier: `POST /customers`, `POST /suppliers`
4. Create product and service: `POST /products`, `POST /services`
5. Create ticket for customer: `POST /tickets`
6. Create work order for ticket/user: `POST /work-orders`
7. Create wallet for user: `POST /wallets`
8. Add ledger transaction: `POST /wallets/transactions`
9. Create payable and receivable entries:
   - `POST /finance/accounts-payable`
   - `POST /finance/accounts-receivable`

Optional checks:

- Wallet balance: `GET /wallets/{wallet_id}/balance`
- List resources: `GET` endpoints for each module

## Autonomous Agent Orchestration

Domain events now trigger asynchronous autonomous agent evaluation.

Flow:

1. Domain action emits event (example: `POST /tickets`)
2. API enqueues `evaluate_agents_task` in Celery (`ai_tasks` queue)
3. Registered agents evaluate the event and propose actions
4. Safety rules filter/limit actions before execution
5. Executed decisions are persisted in `ai_agent_actions`

Current built-in agents:

- `TicketAgent` (ticket lifecycle events)
- `FinanceAgent` (payment/transaction events)
- `OperationsAgent` (work order events)
- `AutomationAgent` (service/knowledge events)

Safety controls (`.env`):

- `AGENT_MAX_ACTIONS_PER_EVENT` (default `3`)
- `AGENT_REQUIRE_APPROVAL_FOR_CRITICAL` (default `true`)

Monitoring endpoint (JWT required):

- `GET /ai/agent-actions?limit=20`
- Optional filters: `agent_name`, `event_type`

Examples:

- `GET /ai/agent-actions?limit=10&agent_name=TicketAgent`
- `GET /ai/agent-actions?limit=10&event_type=TICKET_CREATED`
- `GET /ai/agent-actions?limit=10&agent_name=TicketAgent&event_type=TICKET_CREATED`

## AI (RAG)

Protected endpoint:

- `POST /ai/ask`

Request body:

```json
{
	"question": "What is the status of ticket #1?"
}
```

Response:

```json
{
	"answer": "...",
	"sources": [
		{
			"id": 1,
			"content": "...",
			"metadata": {}
		}
	]
}
```

## AI Agent

Protected endpoint:

- `POST /ai/agent`

Request body:

```json
{
	"message": "Create a ticket for customer 42 because payment failed",
	"session_id": "admin-console"
}
```

Response:

```json
{
	"task_id": "uuid",
	"status": "PENDING"
}
```

Notes:

- Uses LangChain tool-calling over platform services.
- Keeps per-session conversation memory using `session_id`.
- Clients (`CLIENT` role) are blocked from administrative tools.
- Every interaction is audited in `ai_agent_logs`.
- Heavy operations run asynchronously via Celery workers.

Task monitoring endpoint:

- `GET /tasks/{task_id}`

### Live Smoke Test (`/auth/login` -> `/ai/agent`)

```bash
LOGIN_RESPONSE=$(curl -sS --max-time 10 -X POST http://localhost:8000/auth/login \
	-H 'Content-Type: application/json' \
	-d '{"email":"admin@platform.local","password":"Admin@123"}')

TOKEN=$(printf '%s' "$LOGIN_RESPONSE" | /home/joao/projects/ai-service-platform/.venv/bin/python -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')

curl -sS --max-time 15 -X POST http://localhost:8000/ai/agent \
	-H "Authorization: Bearer $TOKEN" \
	-H 'Content-Type: application/json' \
	-d '{"message":"List tickets","session_id":"smoke-readme"}'

# use returned task_id
curl -sS --max-time 10 http://localhost:8000/tasks/<task_id>
```

If Azure OpenAI is not configured yet, expected response is:

```json
{
	"id": "uuid",
	"task_type": "ai_agent_execution",
	"status": "SUCCESS",
	"result": {
		"agent_response": "AI agent is not configured. Please set Azure OpenAI environment variables.",
		"actions_executed": []
	}
}
```

### Tool Execution Smoke Test (Azure Configured)

After setting these variables in `.env` and restarting the API:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_CHAT_DEPLOYMENT`

Run:

```bash
LOGIN_RESPONSE=$(curl -sS --max-time 10 -X POST http://localhost:8000/auth/login \
	-H 'Content-Type: application/json' \
	-d '{"email":"admin@platform.local","password":"Admin@123"}')

TOKEN=$(printf '%s' "$LOGIN_RESPONSE" | /home/joao/projects/ai-service-platform/.venv/bin/python -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')

curl -sS --max-time 20 -X POST http://localhost:8000/ai/agent \
	-H "Authorization: Bearer $TOKEN" \
	-H 'Content-Type: application/json' \
	-d '{"message":"Create a ticket for customer 1 saying payment failed, priority HIGH","session_id":"smoke-tools"}'
```

Expected behavior:

- `POST /ai/agent` returns `task_id` and `PENDING`.
- `GET /tasks/{task_id}` eventually returns `SUCCESS` with tool execution details in `result`.

### Read-Only Smoke Test (Non-Admin Safe)

Use this to validate a permission-safe operation (for example a `CLIENT` user):

```bash
LOGIN_RESPONSE=$(curl -sS --max-time 10 -X POST http://localhost:8000/auth/login \
	-H 'Content-Type: application/json' \
	-d '{"email":"client@example.com","password":"Client@123"}')

TOKEN=$(printf '%s' "$LOGIN_RESPONSE" | /home/joao/projects/ai-service-platform/.venv/bin/python -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')

curl -sS --max-time 20 -X POST http://localhost:8000/ai/agent \
	-H "Authorization: Bearer $TOKEN" \
	-H 'Content-Type: application/json' \
	-d '{"message":"List tickets and summarize current status","session_id":"smoke-readonly"}'
```

Expected behavior:

- Agent task completes with read-only operations in task `result`.

Permission check example for non-admin users:

```bash
curl -sS --max-time 20 -X POST http://localhost:8000/ai/agent \
	-H "Authorization: Bearer $TOKEN" \
	-H 'Content-Type: application/json' \
	-d '{"message":"Create a new customer named Test User","session_id":"smoke-readonly"}'
```

Expected behavior:

- Agent should not execute administrative actions for `CLIENT` role.
- Response should indicate permission restriction and avoid privileged tool execution.

### Seed Admin User for Agent Testing

```bash
PYTHONPATH=. /home/joao/projects/ai-service-platform/.venv/bin/python scripts/seed_admin_user.py
```

Default credentials:

- email: `admin@platform.local`
- password: `Admin@123`

You can override with environment variables:

- `ADMIN_NAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

## Webhook automations (n8n)

Use webhook subscriptions to receive domain events in external automation tools.

### 1) Create a Webhook Subscription

`POST /webhooks`

```json
{
	"event_type": "TICKET_CREATED",
	"target_url": "https://n8n.your-domain.com/webhook/ai-platform-events",
	"active": true
}
```

### 2) List Subscriptions

`GET /webhooks`

### 3) Enable or Disable a Subscription

`PATCH /webhooks/{webhook_id}/active`

```json
{
	"active": false
}
```

### Optional: Seed Default Webhook Subscriptions

```bash
source .env && PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f scripts/seed_webhooks.sql
```

### Optional: Clear All Webhook Subscriptions

```bash
source .env && PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f scripts/clear_webhooks.sql
```

### Webhook Payload Sent to Automations

When an event is triggered (for example, `TICKET_CREATED`, `USER_CREATED`, `TRANSACTION_CREATED`), the platform sends:

```json
{
	"event_type": "TICKET_CREATED",
	"payload": {
		"id": 1,
		"title": "Internet outage",
		"status": "OPEN"
	},
	"timestamp": "2026-03-15T03:30:00+00:00"
}
```