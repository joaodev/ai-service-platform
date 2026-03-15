from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import require_current_user
from app.database.session import get_db
from app.schemas.ticket_schema import TicketCreate, TicketResponse
from app.services.ticket_service import create_ticket, get_ticket_by_id, list_tickets

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("", response_model=list[TicketResponse])
def list_tickets_endpoint(db: Session = Depends(get_db)) -> list[TicketResponse]:
    return list_tickets(db)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_endpoint(ticket_id: int, db: Session = Depends(get_db)) -> TicketResponse:
    return get_ticket_by_id(db, ticket_id)


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_endpoint(
    payload: TicketCreate,
    _: object = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> TicketResponse:
    return create_ticket(db, payload)
