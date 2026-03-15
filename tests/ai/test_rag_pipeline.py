import pytest


@pytest.mark.ai
def test_rag_pipeline_returns_mocked_answer_and_sources(test_db_session, monkeypatch):
    from app.ai.embedding_service import generate_embedding
    from app.ai import rag_service
    from app.models.knowledge_document import KnowledgeDocument

    primary = KnowledgeDocument(
        content="Router reset procedure: hold the reset button for ten seconds.",
        embedding=generate_embedding("router reset procedure"),
        metadata_json={"source": "kb/router-reset"},
    )
    secondary = KnowledgeDocument(
        content="Billing cycle closes on the last business day of the month.",
        embedding=generate_embedding("billing cycle information"),
        metadata_json={"source": "kb/billing-cycle"},
    )
    test_db_session.add_all([primary, secondary])
    test_db_session.commit()

    monkeypatch.setattr(
        rag_service,
        "_generate_answer_from_azure",
        lambda question, context: f"mocked answer for: {question}",
    )

    result = rag_service.answer_question("How do I reset the router?")

    assert result["answer"] == "mocked answer for: How do I reset the router?"
    assert result["sources"]
    assert any(source["metadata"]["source"] == "kb/router-reset" for source in result["sources"])


@pytest.mark.ai
@pytest.mark.asyncio
async def test_ai_endpoint_uses_overridden_rag_service(test_client, auth_token):
    from app.main import app
    from app.routers.ai_router import get_rag_answer_service

    def fake_rag_service(question: str) -> dict:
        return {
            "answer": f"stubbed answer for {question}",
            "sources": [{"id": 999, "content": "stub", "metadata": {"source": "test"}}],
        }

    app.dependency_overrides[get_rag_answer_service] = lambda: fake_rag_service
    try:
        response = await test_client.post(
            "/ai/ask",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"question": "Summarize the runbook"},
        )
    finally:
        app.dependency_overrides.pop(get_rag_answer_service, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "stubbed answer for Summarize the runbook"
    assert payload["sources"][0]["metadata"]["source"] == "test"
