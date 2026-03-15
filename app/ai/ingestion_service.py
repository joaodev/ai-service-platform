from sqlalchemy.orm import Session

from app.ai.embedding_service import generate_embedding
from app.database.session import SessionLocal
from app.events.event_types import EventType
from app.models.knowledge_document import KnowledgeDocument


def store_knowledge_document(db: Session, content: str, metadata: dict) -> KnowledgeDocument:
    embedding = generate_embedding(content)
    document = KnowledgeDocument(content=content, embedding=embedding, metadata_json=metadata)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def _content_from_event(event_type: str, payload: dict) -> str | None:
    if event_type == EventType.TICKET_CREATED:
        return f"Ticket: {payload.get('title', '')}. Status: {payload.get('status', '')}. Priority: {payload.get('priority', '')}."
    if event_type == EventType.SERVICE_CREATED:
        return (
            f"Service: {payload.get('name', '')}. "
            f"Description: {payload.get('description', '')}. "
            f"Base price: {payload.get('base_price', '')}."
        )
    if event_type == EventType.KNOWLEDGE_ARTICLE_CREATED:
        return payload.get("content")
    return None


def process_event_for_ingestion(event_type: str, payload: dict) -> None:
    content = _content_from_event(event_type=event_type, payload=payload)
    if not content:
        return

    db = SessionLocal()
    try:
        store_knowledge_document(
            db=db,
            content=content,
            metadata={
                "source_event": event_type,
                "source_payload": payload,
            },
        )
    finally:
        db.close()
