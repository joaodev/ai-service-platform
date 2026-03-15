from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.event_log import EventLog
from app.models.webhook_config import WebhookConfig


def log_event(db: Session, event_type: str, payload: dict) -> EventLog:
    event_log = EventLog(event_type=event_type, payload=payload)
    db.add(event_log)
    db.commit()
    db.refresh(event_log)
    return event_log


def get_active_webhook_targets(db: Session, event_type: str) -> list[str]:
    targets = (
        db.query(WebhookConfig)
        .filter(WebhookConfig.event_type == event_type, WebhookConfig.active.is_(True))
        .all()
    )
    return [target.target_url for target in targets]


def build_event_message(event_type: str, payload: dict) -> dict:
    return {
        "event_type": event_type,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def list_webhook_configs(db: Session) -> list[WebhookConfig]:
    return db.query(WebhookConfig).all()


def create_webhook_config(
    db: Session,
    event_type: str,
    target_url: str,
    active: bool = True,
) -> WebhookConfig:
    webhook = WebhookConfig(event_type=event_type, target_url=target_url, active=active)
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return webhook


def update_webhook_status(db: Session, webhook_id: int, active: bool) -> WebhookConfig:
    webhook = db.query(WebhookConfig).filter(WebhookConfig.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook config not found",
        )

    webhook.active = active
    db.commit()
    db.refresh(webhook)
    return webhook
