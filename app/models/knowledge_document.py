from sqlalchemy import Column, DateTime, Integer, JSON, Text
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database.base import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    metadata_json = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
