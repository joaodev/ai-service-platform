# Authentication

## Auth model

The API uses JWT bearer tokens signed with `HS256`.

- Secret source: `JWT_SECRET_KEY` (fallback alias: `JWT_SECRET`)
- Token subject (`sub`): user email
- Expiration: `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60)

## Login flow

1. Create user with `POST /users`.
2. Authenticate with `POST /auth/login`.
3. Receive token payload:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

4. Send token in header:

```http
Authorization: Bearer <jwt>
```

## Dependency behavior

- `require_authenticated_subject`
  - Decodes token and validates `sub`.
  - Returns `401` for missing/invalid/expired tokens.
- `require_current_user`
  - Resolves token subject to a persisted user.
  - Returns `401` if user no longer exists.

## Endpoints requiring JWT (current implementation)

- `POST /ai/ask`
- `POST /ai/agent`
- `GET /ai/agent-actions`
- `POST /tickets`
- `POST /work-orders`
- `POST /wallets`
- `POST /wallets/transactions`

## Security recommendations

- Set a strong `JWT_SECRET_KEY` in all non-local environments.
- Rotate secrets periodically.
- Consider adding auth guards to currently public mutable endpoints.
