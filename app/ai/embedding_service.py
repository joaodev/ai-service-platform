import hashlib
import json
from urllib import request

from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
)

EMBEDDING_DIMENSION = 1536


def _fallback_embedding(text: str) -> list[float]:
    seed = text.encode("utf-8")
    values: list[float] = []
    counter = 0
    while len(values) < EMBEDDING_DIMENSION:
        digest = hashlib.sha256(seed + counter.to_bytes(4, "little")).digest()
        for byte in digest:
            values.append((byte / 255.0) * 2 - 1)
            if len(values) == EMBEDDING_DIMENSION:
                break
        counter += 1
    return values


def generate_embedding(text: str) -> list[float]:
    if not text:
        return _fallback_embedding("")

    if not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY and AZURE_OPENAI_EMBEDDING_DEPLOYMENT):
        return _fallback_embedding(text)

    endpoint = AZURE_OPENAI_ENDPOINT.rstrip("/")
    url = (
        f"{endpoint}/openai/deployments/{AZURE_OPENAI_EMBEDDING_DEPLOYMENT}/embeddings"
        f"?api-version={AZURE_OPENAI_API_VERSION}"
    )
    body = json.dumps({"input": text}).encode("utf-8")
    http_request = request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_API_KEY,
        },
    )

    try:
        with request.urlopen(http_request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload["data"][0]["embedding"]
    except Exception:
        return _fallback_embedding(text)
