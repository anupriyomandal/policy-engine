from typing import Iterable, List, Tuple

import tiktoken

from app.config import settings


def _tokenize(text: str, encoding_name: str = "cl100k_base") -> List[int]:
    encoding = tiktoken.get_encoding(encoding_name)
    return encoding.encode(text)


def _detokenize(tokens: List[int], encoding_name: str = "cl100k_base") -> str:
    encoding = tiktoken.get_encoding(encoding_name)
    return encoding.decode(tokens)


def chunk_text(text: str) -> List[str]:
    tokens = _tokenize(text)
    if not tokens:
        return []

    size = settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP

    chunks: List[str] = []
    start = 0
    while start < len(tokens):
        end = min(start + size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(_detokenize(chunk_tokens))
        if end == len(tokens):
            break
        start = end - overlap
    return chunks


def chunk_pages(pages: Iterable[Tuple[str, int]]) -> List[Tuple[str, int]]:
    chunks: List[Tuple[str, int]] = []
    for text, page_number in pages:
        for chunk in chunk_text(text):
            cleaned = chunk.strip()
            if cleaned:
                chunks.append((cleaned, page_number))
    return chunks
