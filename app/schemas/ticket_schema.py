from datetime import datetime

from pydantic import BaseModel

from app.models.ticket import TicketStatus


class TicketCreate(BaseModel):
    title: str
    description: str | None = None
    status: TicketStatus = TicketStatus.OPEN
    priority: str = "MEDIUM"
    customer_id: int


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TicketStatus
    priority: str
    customer_id: int
    created_at: datetime

    class Config:
        from_attributes = True
