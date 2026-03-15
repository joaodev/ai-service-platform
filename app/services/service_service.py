from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.events.event_publisher import publish_event
from app.events.event_types import EventType
from app.models.service import Service
from app.schemas.service_schema import ServiceCreate


def list_services(db: Session) -> list[Service]:
    return db.query(Service).all()


def get_service_by_id(db: Session, service_id: int) -> Service:
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service


def create_service(db: Session, payload: ServiceCreate) -> Service:
    service = Service(
        name=payload.name,
        description=payload.description,
        base_price=payload.base_price,
    )
    db.add(service)
    db.commit()
    db.refresh(service)

    publish_event(
        event_type=EventType.SERVICE_CREATED,
        payload={
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "base_price": float(service.base_price),
        },
        db=db,
    )

    return service
