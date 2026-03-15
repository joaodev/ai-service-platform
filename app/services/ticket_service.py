from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.events.event_publisher import publish_event
from app.events.event_types import EventType
from app.models.ticket import Ticket
from app.schemas.ticket_schema import TicketCreate


def list_tickets(db: Session) -> list[Ticket]:
    return db.query(Ticket).all()


def get_ticket_by_id(db: Session, ticket_id: int) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def create_ticket(db: Session, payload: TicketCreate) -> Ticket:
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        customer_id=payload.customer_id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    publish_event(
        event_type=EventType.TICKET_CREATED,
        payload={
            "id": ticket.id,
            "title": ticket.title,
            "status": ticket.status.value,
            "priority": ticket.priority,
            "customer_id": ticket.customer_id,
        },
        db=db,
    )

    return ticket
