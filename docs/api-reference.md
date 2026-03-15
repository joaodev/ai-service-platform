# API Reference

## Base endpoints

- `GET /` → health message (`{"message": "API running"}`)
- `GET /health` → service health (`{"status": "ok"}`)

## Authentication

- `POST /users` → create user (returns user + role)
- `POST /auth/login` → returns JWT bearer token

## AI

- `POST /ai/ask` *(JWT required)*
  - Runs RAG question answering and returns `answer` + `sources`.
- `POST /ai/agent` *(JWT required)*
  - Enqueues async AI agent execution; returns `task_id` and `PENDING` status.
- `GET /ai/agent-actions` *(JWT required)*
  - Lists AI agent actions with optional filters:
    - `limit` (1..100, default 20)
    - `agent_name`
    - `event_type`

## Domain resources

### Customers

- `GET /customers`
- `GET /customers/{customer_id}`
- `POST /customers`

### Suppliers

- `GET /suppliers`
- `GET /suppliers/{supplier_id}`
- `POST /suppliers`

### Products

- `GET /products`
- `GET /products/{product_id}`
- `POST /products`

### Services

- `GET /services`
- `GET /services/{service_id}`
- `POST /services`

### Tickets

- `GET /tickets`
- `GET /tickets/{ticket_id}`
- `POST /tickets` *(JWT required)*

### Work Orders

- `GET /work-orders`
- `GET /work-orders/{work_order_id}`
- `POST /work-orders` *(JWT required)*

### Wallets & Transactions

- `GET /wallets`
- `GET /wallets/{wallet_id}`
- `POST /wallets` *(JWT required)*
- `GET /wallets/{wallet_id}/balance`
- `GET /wallets/transactions`
- `GET /wallets/transactions/{transaction_id}`
- `POST /wallets/transactions` *(JWT required)*

### Finance

- `GET /finance/accounts-payable`
- `GET /finance/accounts-payable/{payable_id}`
- `POST /finance/accounts-payable`
- `GET /finance/accounts-receivable`
- `GET /finance/accounts-receivable/{receivable_id}`
- `POST /finance/accounts-receivable`

### Webhooks

- `GET /webhooks`
- `POST /webhooks`
- `PATCH /webhooks/{webhook_id}/active`

### Background tasks

- `GET /tasks/{task_id}` → returns stored task status/result.

## Notes

- Canonical request/response schemas are in Swagger (`/docs`) and `app/schemas/`.
- Some domains currently expose public read/write endpoints without auth guards.
  If you want stricter access control, add `Depends(require_current_user)` at router level.
