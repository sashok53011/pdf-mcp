"""Tests for LM Studio script generation."""

import os
import tempfile

import pymupdf
import pytest

from pdf_mcp.lmstudio import render_and_generate_script_sync


@pytest.fixture
def sample_pdf(tmp_path):
    path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    for i in range(2):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i + 1}")
    doc.save(str(path))
    doc.close()
    return str(path)


def test_generates_script_and_images(sample_pdf):
    page_count, image_paths, script_path, script_content = render_and_generate_script_sync(
        sample_pdf, page_to=2
    )
    assert page_count == 2
    assert len(image_paths) == 2
    for p in image_paths:
        assert os.path.isfile(p)
        assert os.path.getsize(p) > 0
    assert os.path.isfile(script_path)
    assert "localhost:1234" in script_content
    assert "google/gemma-4-12b" in script_content
    assert "urlopen" in script_content


def test_output_dir(sample_pdf, tmp_path):
    out = tmp_path / "out"
    page_count, image_paths, script_path, _ = render_and_generate_script_sync(
        sample_pdf, output_dir=str(out)
    )
    assert out.exists()
    assert all(str(out) in str(p) for p in image_paths)
    assert str(out) in str(script_path)
