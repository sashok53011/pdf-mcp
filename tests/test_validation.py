"""Tests for validation."""

import pytest

from pdf_mcp.validation import (
    ValidationError,
    validate_pdf_path,
    validate_dpi,
    validate_format,
    validate_page_range,
    validate_jpeg_quality,
)
from pdf_mcp.config import MAX_PAGES_PER_CALL, MAX_DPI, MIN_DPI


def test_validate_pdf_path_missing(tmp_path):
    with pytest.raises(ValidationError):
        validate_pdf_path(str(tmp_path / "nope.pdf"))


def test_validate_pdf_path_not_pdf(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text("hi")
    with pytest.raises(ValidationError):
        validate_pdf_path(str(p))


def test_validate_pdf_path_empty(tmp_path):
    p = tmp_path / "empty.pdf"
    p.write_bytes(b"")
    with pytest.raises(ValidationError):
        validate_pdf_path(str(p))


def test_validate_dpi_range():
    with pytest.raises(ValidationError):
        validate_dpi(MIN_DPI - 1)
    with pytest.raises(ValidationError):
        validate_dpi(MAX_DPI + 1)
    assert validate_dpi(150) == 150


def test_validate_format():
    assert validate_format("PNG") == "png"
    assert validate_format("jpg") == "jpeg"
    with pytest.raises(ValidationError):
        validate_format("bmp")


def test_validate_page_range_exceeds():
    with pytest.raises(ValidationError):
        validate_page_range(1, MAX_PAGES_PER_CALL + 1, MAX_PAGES_PER_CALL + 5)


def test_validate_page_range_invalid():
    with pytest.raises(ValidationError):
        validate_page_range(0, None, 3)
    with pytest.raises(ValidationError):
        validate_page_range(2, 1, 3)
    with pytest.raises(ValidationError):
        validate_page_range(5, None, 3)


def test_validate_jpeg_quality():
    with pytest.raises(ValidationError):
        validate_jpeg_quality(0)
    with pytest.raises(ValidationError):
        validate_jpeg_quality(101)
    assert validate_jpeg_quality(90) == 90
