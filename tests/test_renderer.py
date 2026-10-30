"""Tests for rendering."""

import pytest

from pdf_mcp.renderer import render_pdf_sync
from pdf_mcp.config import DEFAULT_DPI


def test_render_all_pages(sample_pdf):
    page_count, pages = render_pdf_sync(sample_pdf)
    assert page_count == 3
    assert len(pages) == 3
    for num, data in pages:
        assert isinstance(num, int)
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert len(data) > 100


def test_render_range(sample_pdf):
    page_count, pages = render_pdf_sync(sample_pdf, page_from=2, page_to=3)
    assert page_count == 3
    assert [n for n, _ in pages] == [2, 3]


def test_render_jpeg(sample_pdf):
    _, pages = render_pdf_sync(sample_pdf, fmt="jpeg", jpeg_quality=80)
    assert pages[0][1][:2] == b"\xff\xd8"


def test_render_dpi(sample_pdf):
    _, low = render_pdf_sync(sample_pdf, dpi=72)
    _, high = render_pdf_sync(sample_pdf, dpi=144)
    assert len(high[0][1]) > len(low[0][1])
