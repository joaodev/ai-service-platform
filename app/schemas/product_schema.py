from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
