from typing import List, Tuple

from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Chunk, Document


_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def retrieve_chunks(db: Session, query_embedding: List[float], top_k: int) -> List[Tuple[Chunk, float, str]]:
    distance = Chunk.embedding.cosine_distance(query_embedding)
    results = (
        db.query(Chunk, distance.label("distance"), Document.filename)
        .join(Document, Document.id == Chunk.document_id)
        .order_by(distance)
        .limit(top_k)
        .all()
    )
    return [(row[0], row[1], row[2]) for row in results]


def build_context(chunks: List[Chunk]) -> str:
    sections = []
    for chunk in chunks:
        header = f"[Source {chunk.id} | Page {chunk.page_number or 'N/A'}]"
        sections.append(f"{header}\n{chunk.content}")
    return "\n\n".join(sections)


def answer_with_context(query: str, context: str) -> str:
    prompt = (
        "You are a policy intelligence assistant. Answer the question using only the sources. "
        "If the answer is not contained in the sources, say you don't have enough information. "
        "Return a short Markdown response with a 1-line title and 4-8 bullet points. "
        "Each bullet should be a crisp statement. "
        "Do not include source IDs or citations in the answer."
        "Do not write long paragraphs."
    )
    response = _client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Question: {query}\n\nSources:\n{context}"},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()
