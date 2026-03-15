from datetime import datetime

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)
