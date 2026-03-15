from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WalletCreate(BaseModel):
    user_id: int


class WalletResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
