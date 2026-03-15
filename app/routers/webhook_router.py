from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.events.event_service import (
    create_webhook_config,
    list_webhook_configs,
    update_webhook_status,
)
from app.schemas.webhook_schema import (
    WebhookConfigCreate,
    WebhookConfigResponse,
    WebhookConfigUpdate,
)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.get("", response_model=list[WebhookConfigResponse])
def list_webhooks_endpoint(db: Session = Depends(get_db)) -> list[WebhookConfigResponse]:
    return list_webhook_configs(db)


@router.post("", response_model=WebhookConfigResponse, status_code=status.HTTP_201_CREATED)
def create_webhook_endpoint(
    payload: WebhookConfigCreate,
    db: Session = Depends(get_db),
) -> WebhookConfigResponse:
    return create_webhook_config(
        db=db,
        event_type=payload.event_type,
        target_url=str(payload.target_url),
        active=payload.active,
    )


@router.patch("/{webhook_id}/active", response_model=WebhookConfigResponse)
def update_webhook_active_endpoint(
    webhook_id: int,
    payload: WebhookConfigUpdate,
    db: Session = Depends(get_db),
) -> WebhookConfigResponse:
    return update_webhook_status(db=db, webhook_id=webhook_id, active=payload.active)
