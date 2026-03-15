from datetime import datetime

from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    document_number: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    document_number: str
    created_at: datetime

    class Config:
        from_attributes = True
