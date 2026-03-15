from datetime import datetime

from pydantic import BaseModel


class SupplierCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    document_number: str


class SupplierResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    document_number: str
    created_at: datetime

    class Config:
        from_attributes = True
