from typing import List

from openai import OpenAI

from app.config import settings


_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def embed_texts(texts: List[str], batch_size: int = 96) -> List[List[float]]:
    if not texts:
        return []

    embeddings: List[List[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = _client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=batch,
        )
        embeddings.extend([item.embedding for item in response.data])
    return embeddings
