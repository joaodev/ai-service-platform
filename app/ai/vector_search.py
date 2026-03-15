from app.ai.embedding_service import generate_embedding
from app.database.session import SessionLocal
from app.models.knowledge_document import KnowledgeDocument


def search_similar_documents(query: str, top_k: int = 5) -> list[KnowledgeDocument]:
    query_embedding = generate_embedding(query)
    db = SessionLocal()
    try:
        return (
            db.query(KnowledgeDocument)
            .order_by(KnowledgeDocument.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )
    finally:
        db.close()
