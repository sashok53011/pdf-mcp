"""PDF text extraction using PyMuPDF."""

import asyncio
from typing import List, Tuple

import pymupdf

from .validation import validate_pdf_path, validate_page_range


def _blocks_to_markdown(blocks: list) -> str:
    # blocks: list of (x0, y0, x1, y1, text, block_no, block_type)
    text_blocks = [b for b in blocks if b[6] == 0 and str(b[4]).strip()]
    # sort by vertical position then horizontal
    text_blocks.sort(key=lambda b: (round(b[1]), b[0]))
    parts = []
    for b in text_blocks:
        txt = str(b[4]).strip()
        if txt:
            parts.append(txt)
    return "\n\n".join(parts)


def extract_text_sync(
    pdf_path: str,
    page_from: int = 1,
    page_to: int | None = None,
    layout: str = "blocks",
) -> Tuple[int, List[Tuple[int, str]]]:
    """Extract text from selected PDF pages.

    Returns (page_count, list of (1-based page number, text)).
    """
    path = validate_pdf_path(pdf_path)
    doc = pymupdf.open(str(path))
    try:
        page_count = doc.page_count
        if page_count == 0:
            raise ValueError("PDF has no pages")
        page_from, page_to = validate_page_range(page_from, page_to, page_count)

        result: List[Tuple[int, str]] = []
        for i in range(page_from - 1, page_to):
            page = doc[i]
            if layout == "simple":
                text = page.get_text().strip()
            else:
                blocks = page.get_text("blocks")
                text = _blocks_to_markdown(blocks)
            result.append((i + 1, text))
        return page_count, result
    finally:
        doc.close()


async def extract_text(
    pdf_path: str,
    page_from: int = 1,
    page_to: int | None = None,
    layout: str = "blocks",
) -> Tuple[int, List[Tuple[int, str]]]:
    return await asyncio.to_thread(
        extract_text_sync, pdf_path, page_from, page_to, layout
    )
