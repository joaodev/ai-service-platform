# Postman Guide

This guide shows how to use the existing Postman assets in `postman/` for local, staging, and production testing.

## Available files

- Collection: `postman/ai-service-platform.postman_collection.json`
- Local environment: `postman/ai-service-platform.local.postman_environment.json`
- Staging environment: `postman/ai-service-platform.staging.postman_environment.json`
- Production environment: `postman/ai-service-platform.production.postman_environment.json`

## Import into Postman

1. Open Postman.
2. Import the collection file.
3. Import one environment file (start with local).
4. Select the imported environment in the top-right environment selector.

## Recommended execution flow

Run requests in this order:

1. `Platform > Health`
2. `Authentication > Create User` (skip if user already exists)
3. `Authentication > Login`
4. Protected endpoints such as:
   - `AI > Ask AI`
   - `AI > Execute Agent`
   - `Tickets > Create Ticket`
   - `Work Orders > Create Work Order`
   - `Wallets > Create Wallet`

## Token handling

The collection includes test scripts that automatically store:

- `accessToken` from `Authentication > Login`
- IDs like `userId`, `customerId`, `ticketId`, `walletId`, etc., from create responses

Protected requests use `Authorization: Bearer {{accessToken}}`.

If a protected request returns `401`:

- rerun `Authentication > Login`
- verify `accessToken` is populated in the active environment/collection variables

## Task polling flow (AI Agent)

1. Run `AI > Execute Agent` (or equivalent `POST /ai/agent` request).
2. Copy/set returned `task_id` into `taskId`.
3. Run `Tasks > Get Task Status` (`GET /tasks/{{taskId}}`) until status is `SUCCESS` or `FAILED`.

## Environment tips

- `baseUrl` must match the API host (local default: `http://localhost:8000`).
- Keep production tokens in Postman secret variables only.
- Prefer separate environments for local/staging/prod to avoid accidental cross-target calls.

## Troubleshooting

- **`Platform > Health` fails or returns connection error**
   - Confirm API is running and reachable at `{{baseUrl}}`.
   - For local usage, verify `baseUrl` is `http://localhost:8000`.

- **Protected endpoints return `401 Invalid or expired token`**
   - Rerun `Authentication > Login` to refresh `accessToken`.
   - Confirm the request is sending `Authorization: Bearer {{accessToken}}`.
   - Ensure the same environment is selected where `accessToken` was saved.

- **Create User fails because email already exists**
   - Skip `Create User` and use `Login` with an existing account.
   - Or change the email in the create payload to a new value.

- **`GET /tasks/{{taskId}}` returns `404 Task not found`**
   - Re-run the async request (`POST /ai/agent`) and copy the new `task_id`.
   - Verify `taskId` variable is set in the active environment.

- **Task remains `PENDING` for too long**
   - Check if Celery worker is running and connected to Redis.
   - Start/restart worker queues used by the project: `default,ai_tasks,events,webhooks`.

