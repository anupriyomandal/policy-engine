from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_id: UUID
    filename: str
    chunks_created: int


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3)
    document_id: Optional[UUID] = None
    top_k: Optional[int] = None
    include_sources: bool = True


class SourceChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    filename: str
    page_number: Optional[int]
    chunk_index: int
    content: str
    similarity: float


class QueryResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[SourceChunk]
