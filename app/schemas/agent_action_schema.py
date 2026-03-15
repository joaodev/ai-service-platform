from datetime import datetime

from pydantic import BaseModel


class AgentActionItem(BaseModel):
    id: int
    agent_name: str
    event_type: str
    decision: str
    actions: dict
    created_at: datetime

    class Config:
        from_attributes = True
