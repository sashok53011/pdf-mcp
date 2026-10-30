"""Tests for text extraction."""

import pytest

from pdf_mcp.text import extract_text_sync


def test_extract_all_pages(sample_pdf):
    page_count, pages = extract_text_sync(sample_pdf)
    assert page_count == 3
    assert len(pages) == 3
    for num, text in pages:
        assert isinstance(num, int)
        assert f"Page {num}" in text


def test_extract_range(sample_pdf):
    page_count, pages = extract_text_sync(sample_pdf, page_from=2, page_to=3)
    assert page_count == 3
    assert [n for n, _ in pages] == [2, 3]


def test_extract_simple(sample_pdf):
    _, pages = extract_text_sync(sample_pdf, layout="simple")
    assert "Page 1" in pages[0][1]
