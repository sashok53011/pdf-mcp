"""PDF page rendering using PyMuPDF."""

import asyncio
from typing import List, Tuple

import pymupdf

from .config import DEFAULT_DPI, DEFAULT_FORMAT
from .validation import validate_pdf_path, validate_dpi, validate_format, validate_page_range, validate_jpeg_quality


def render_pdf_sync(
    pdf_path: str,
    dpi: int = DEFAULT_DPI,
    page_from: int = 1,
    page_to: int | None = None,
    fmt: str = DEFAULT_FORMAT,
    jpeg_quality: int = 90,
) -> Tuple[int, List[Tuple[int, bytes]]]:
    """Render selected PDF pages to images.

    Returns (page_count, list of (1-based page number, image bytes)).
    """
    path = validate_pdf_path(pdf_path)
    dpi = validate_dpi(dpi)
    fmt = validate_format(fmt)
    if fmt == "jpeg":
        jpeg_quality = validate_jpeg_quality(jpeg_quality)

    doc = pymupdf.open(str(path))
    try:
        page_count = doc.page_count
        if page_count == 0:
            raise ValueError("PDF has no pages")
        page_from, page_to = validate_page_range(page_from, page_to, page_count)

        zoom = dpi / 72.0
        matrix = pymupdf.Matrix(zoom, zoom)
        result: List[Tuple[int, bytes]] = []
        for i in range(page_from - 1, page_to):
            page = doc[i]
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            if fmt == "png":
                data = pix.tobytes("png")
            else:
                data = pix.tobytes("jpeg", jpg_quality=jpeg_quality)
            result.append((i + 1, data))
        return page_count, result
    finally:
        doc.close()


async def render_pdf(
    pdf_path: str,
    dpi: int = DEFAULT_DPI,
    page_from: int = 1,
    page_to: int | None = None,
    fmt: str = DEFAULT_FORMAT,
    jpeg_quality: int = 90,
) -> Tuple[int, List[Tuple[int, bytes]]]:
    return await asyncio.to_thread(
        render_pdf_sync, pdf_path, dpi, page_from, page_to, fmt, jpeg_quality
    )
