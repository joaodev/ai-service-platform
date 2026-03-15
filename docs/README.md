# API Documentation

This folder describes how the `ai-service-platform` API is structured and how to consume it.

## Contents

- [Overview](overview.md): architecture, request lifecycle, and main modules.
- [API Reference](api-reference.md): endpoint groups, methods, and auth requirements.
- [Authentication](authentication.md): JWT flow and protected routes.
- [Async Tasks](async-tasks.md): Celery queues, task lifecycle, and polling strategy.
- [Postman Guide](postman-guide.md): import, auth token capture, and end-to-end request flow.

## Live API Docs

When the API is running locally:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
