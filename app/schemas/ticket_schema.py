from datetime import datetime

from pydantic import BaseModel, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)
