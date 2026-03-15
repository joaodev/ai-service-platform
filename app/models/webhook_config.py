from sqlalchemy import Boolean, Column, Integer, String

from app.database.base import Base


class WebhookConfig(Base):
    __tablename__ = "webhook_configs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    target_url = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
