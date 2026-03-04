from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Chunk, Document
from app.dependencies import get_db
from app.schemas.policy import QueryRequest, QueryResponse, SourceChunk, UploadResponse
from app.services.chunking import chunk_pages
from app.services.document_loader import load_pdf, load_text
from app.services.embeddings import embed_texts
from app.services.rag import answer_with_context, retrieve_chunks, build_context

router = APIRouter(prefix="", tags=["policy"])


@router.post("/upload-doc", response_model=UploadResponse)
async def upload_doc(file: UploadFile = File(...), db: Session = Depends(get_db)) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    filename = file.filename
    extension = filename.split(".")[-1].lower()

    if extension == "pdf":
        pages = load_pdf(content)
    elif extension in {"txt", "md"}:
        pages = load_text(content)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    chunks_with_pages = chunk_pages(pages)
    if not chunks_with_pages:
        raise HTTPException(status_code=400, detail="No extractable text in document")

    document = Document(filename=filename)
    db.add(document)
    db.flush()

    chunk_texts = [chunk for chunk, _page in chunks_with_pages]
    embeddings = embed_texts(chunk_texts)

    chunk_rows: List[Chunk] = []
    for idx, ((chunk_text, page_number), embedding) in enumerate(zip(chunks_with_pages, embeddings)):
        chunk_rows.append(
            Chunk(
                document_id=document.id,
                content=chunk_text,
                page_number=page_number,
                chunk_index=idx,
                embedding=embedding,
            )
        )

    db.add_all(chunk_rows)
    db.commit()

    return UploadResponse(document_id=document.id, filename=filename, chunks_created=len(chunk_rows))


@router.post("/query", response_model=QueryResponse)
def query_policy(payload: QueryRequest, db: Session = Depends(get_db)) -> QueryResponse:
    top_k = payload.top_k or settings.TOP_K
    target_document_id = payload.document_id

    if target_document_id is None:
        latest_document = db.query(Document).order_by(Document.uploaded_at.desc()).first()
        if latest_document is None:
            return QueryResponse(answer="No documents found. Upload a document first.", confidence=0.0, sources=[])
        target_document_id = latest_document.id

    query_embedding = embed_texts([payload.query])[0]
    results = retrieve_chunks(db, query_embedding, top_k, document_id=target_document_id)

    if not results:
        return QueryResponse(answer="No relevant sources found.", confidence=0.0, sources=[])

    chunks = [chunk for chunk, _distance, _filename in results]
    context = build_context(chunks)

    answer = answer_with_context(payload.query, context)

    sources: List[SourceChunk] = []
    similarities = []
    for chunk, distance, filename in results:
        similarity = max(0.0, min(1.0, 1.0 - float(distance)))
        similarities.append(similarity)
        sources.append(
            SourceChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                filename=filename,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                similarity=similarity,
            )
        )

    confidence = max(similarities) if similarities else 0.0

    return QueryResponse(
        answer=answer,
        confidence=confidence,
        sources=sources if payload.include_sources else [],
    )


@router.get("/sources", response_model=List[SourceChunk])
def list_sources(document_id: str, db: Session = Depends(get_db)) -> List[SourceChunk]:
    chunks = (
        db.query(Chunk, Document.filename)
        .join(Document, Document.id == Chunk.document_id)
        .filter(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index)
        .all()
    )

    return [
        SourceChunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            filename=filename,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            similarity=0.0,
        )
        for chunk, filename in chunks
    ]
