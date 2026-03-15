from pydantic import BaseModel, ConfigDict, HttpUrl

from app.events.event_types import EventType


class WebhookConfigCreate(BaseModel):
    event_type: EventType
    target_url: HttpUrl
    active: bool = True


class WebhookConfigUpdate(BaseModel):
    active: bool


class WebhookConfigResponse(BaseModel):
    id: int
    event_type: str
    target_url: str
    active: bool

    model_config = ConfigDict(from_attributes=True)
