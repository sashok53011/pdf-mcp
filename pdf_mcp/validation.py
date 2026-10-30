"""Validation helpers for pdf-mcp."""

from pathlib import Path

from .config import (
    MAX_DPI,
    MIN_DPI,
    MAX_PDF_SIZE_BYTES,
    ALLOWED_FORMATS,
    MAX_PAGES_PER_CALL,
    MIN_JPEG_QUALITY,
    MAX_JPEG_QUALITY,
)


class ValidationError(ValueError):
    """Raised when input validation fails."""


def validate_pdf_path(pdf_path: str) -> Path:
    if not pdf_path or not isinstance(pdf_path, str):
        raise ValidationError("pdf_path must be a non-empty string")
    path = Path(pdf_path).expanduser()
    if not path.is_file():
        raise ValidationError(f"PDF file not found: {pdf_path}")
    if path.suffix.lower() != ".pdf":
        raise ValidationError(f"File is not a PDF: {pdf_path}")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValidationError(f"Cannot read file: {pdf_path}") from exc
    if size == 0:
        raise ValidationError(f"PDF file is empty: {pdf_path}")
    if size > MAX_PDF_SIZE_BYTES:
        raise ValidationError(
            f"PDF file is too large ({size} bytes); limit is {MAX_PDF_SIZE_BYTES} bytes"
        )
    return path


def validate_dpi(dpi: int) -> int:
    if not isinstance(dpi, int) or isinstance(dpi, bool):
        raise ValidationError("dpi must be an integer")
    if dpi < MIN_DPI or dpi > MAX_DPI:
        raise ValidationError(f"dpi must be between {MIN_DPI} and {MAX_DPI}, got {dpi}")
    return dpi


def validate_format(fmt: str) -> str:
    if not isinstance(fmt, str):
        raise ValidationError("format must be a string")
    fmt = fmt.lower().strip()
    if fmt not in ALLOWED_FORMATS:
        raise ValidationError(
            f"Unsupported format '{fmt}'; allowed: {sorted(ALLOWED_FORMATS)}"
        )
    if fmt == "jpg":
        fmt = "jpeg"
    return fmt


def validate_page_range(page_from: int, page_to: int | None, page_count: int) -> tuple[int, int]:
    if not isinstance(page_from, int) or isinstance(page_from, bool):
        raise ValidationError("page_from must be an integer")
    if page_from < 1:
        raise ValidationError(f"page_from must be >= 1, got {page_from}")
    if page_to is not None:
        if not isinstance(page_to, int) or isinstance(page_to, bool):
            raise ValidationError("page_to must be an integer or None")
        if page_to < page_from:
            raise ValidationError(
                f"page_to ({page_to}) must be >= page_from ({page_from})"
            )
    last = page_count if page_to is None else min(page_to, page_count)
    if page_from > page_count:
        raise ValidationError(
            f"page_from ({page_from}) exceeds document page count ({page_count})"
        )
    total = last - page_from + 1
    if total > MAX_PAGES_PER_CALL:
        raise ValidationError(
            f"Requested {total} pages exceeds limit of {MAX_PAGES_PER_CALL} per call"
        )
    if total < 1:
        raise ValidationError("No pages to render")
    return page_from, last


def validate_jpeg_quality(quality: int) -> int:
    if not isinstance(quality, int) or isinstance(quality, bool):
        raise ValidationError("jpeg_quality must be an integer")
    if quality < MIN_JPEG_QUALITY or quality > MAX_JPEG_QUALITY:
        raise ValidationError(
            f"jpeg_quality must be between {MIN_JPEG_QUALITY} and {MAX_JPEG_QUALITY}, got {quality}"
        )
    return quality
