from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.events.event_publisher import publish_event
from app.events.event_types import EventType
from app.models.work_order import WorkOrder
from app.models.work_order import WorkOrderStatus
from app.schemas.work_order_schema import WorkOrderCreate


def list_work_orders(db: Session) -> list[WorkOrder]:
    return db.query(WorkOrder).all()


def get_work_order_by_id(db: Session, work_order_id: int) -> WorkOrder:
    work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return work_order


def create_work_order(db: Session, payload: WorkOrderCreate) -> WorkOrder:
    work_order = WorkOrder(
        ticket_id=payload.ticket_id,
        assigned_user_id=payload.assigned_user_id,
        status=payload.status,
        started_at=payload.started_at,
        finished_at=payload.finished_at,
    )
    db.add(work_order)
    db.commit()
    db.refresh(work_order)

    payload_data = {
        "id": work_order.id,
        "ticket_id": work_order.ticket_id,
        "assigned_user_id": work_order.assigned_user_id,
        "status": work_order.status.value,
        "started_at": work_order.started_at.isoformat() if work_order.started_at else None,
        "finished_at": work_order.finished_at.isoformat() if work_order.finished_at else None,
    }

    publish_event(event_type=EventType.WORK_ORDER_CREATED, payload=payload_data, db=db)

    if work_order.status == WorkOrderStatus.STARTED:
        publish_event(event_type=EventType.WORK_ORDER_STARTED, payload=payload_data, db=db)

    if work_order.status == WorkOrderStatus.FINISHED:
        publish_event(event_type=EventType.WORK_ORDER_FINISHED, payload=payload_data, db=db)

    return work_order
