import json
from urllib import request

from app.ai.vector_search import search_similar_documents
from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_CHAT_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)


def _build_context(sources: list[dict]) -> str:
    if not sources:
        return "No relevant internal documents found."
    return "\n\n".join([f"[doc:{item['id']}] {item['content']}" for item in sources])


def _generate_answer_from_azure(question: str, context: str) -> str:
    if not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY and AZURE_OPENAI_CHAT_DEPLOYMENT):
        return f"Based on retrieved documents, here is the best answer: {context[:500]}"

    endpoint = AZURE_OPENAI_ENDPOINT.rstrip("/")
    url = (
        f"{endpoint}/openai/deployments/{AZURE_OPENAI_CHAT_DEPLOYMENT}/chat/completions"
        f"?api-version={AZURE_OPENAI_API_VERSION}"
    )
    prompt = (
        "You are an assistant for an internal service platform. "
        "Answer only using the provided context. "
        f"\n\nContext:\n{context}\n\nQuestion:\n{question}"
    )
    body = {
        "messages": [
            {"role": "system", "content": "You answer based on internal platform data."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    http_request = request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_API_KEY,
        },
    )

    try:
        with request.urlopen(http_request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"]
    except Exception:
        return f"Based on retrieved documents, here is the best answer: {context[:500]}"


def answer_question(question: str) -> dict:
    documents = search_similar_documents(query=question, top_k=5)
    sources = [
        {
            "id": document.id,
            "content": document.content,
            "metadata": document.metadata_json,
        }
        for document in documents
    ]
    context = _build_context(sources)
    answer = _generate_answer_from_azure(question=question, context=context)
    return {"answer": answer, "sources": sources}
