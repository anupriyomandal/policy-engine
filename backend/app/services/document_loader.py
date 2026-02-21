from io import BytesIO
from typing import List, Tuple

from pypdf import PdfReader


def load_pdf(content: bytes) -> List[Tuple[str, int]]:
    reader = PdfReader(BytesIO(content))
    pages: List[Tuple[str, int]] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append((text, index))
    return pages


def load_text(content: bytes) -> List[Tuple[str, int]]:
    text = content.decode("utf-8", errors="ignore")
    return [(text, 1)]
