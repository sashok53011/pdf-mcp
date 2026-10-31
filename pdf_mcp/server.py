"""MCP server entry: registers the pdf_to_images tool."""

import logging
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.utilities.types import Image
from mcp.types import TextContent

from .config import DEFAULT_DPI, DEFAULT_FORMAT, DEFAULT_JPEG_QUALITY
from .renderer import render_pdf
from .text import extract_text
from .lmstudio import render_and_generate_script, run_script
from .validation import ValidationError

logger = logging.getLogger("pdf-mcp")

mcp = MCPServer("pdf-mcp")


@mcp.tool()
async def pdf_to_images(
    pdf_path: str,
    dpi: int = DEFAULT_DPI,
    page_from: int = 1,
    page_to: int | None = None,
    format: str = DEFAULT_FORMAT,
    jpeg_quality: int = DEFAULT_JPEG_QUALITY,
    include_metadata: bool = True,
) -> list:
    """Render selected pages of a PDF file to images.

    Args:
        pdf_path: Absolute or relative path to a local PDF file.
        dpi: Rendering resolution (50..300). Default 150.
        page_from: First page to render (1-based). Default 1.
        page_to: Last page to render (1-based, inclusive). None = to end (subject to limits).
        format: Output image format: "png" or "jpeg". Default "png".
        jpeg_quality: JPEG quality (1..100), used only for jpeg. Default 90.
        include_metadata: Prepend a short text summary. Default True.

    Returns:
        A list containing an optional text summary followed by one image per rendered page.
    """
    try:
        page_count, pages = await render_pdf(
            pdf_path=pdf_path,
            dpi=dpi,
            page_from=page_from,
            page_to=page_to,
            fmt=format,
            jpeg_quality=jpeg_quality,
        )
    except (ValidationError, ValueError) as exc:
        from mcp.server.mcpserver.exceptions import ToolError

        raise ToolError(str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to render PDF: %s", pdf_path)
        from mcp.server.mcpserver.exceptions import ToolError

        raise ToolError(f"Failed to render PDF: {exc}") from exc

    fmt_norm = "jpeg" if format.lower() in ("jpeg", "jpg") else "png"
    result: list = []
    if include_metadata:
        result.append(
            TextContent(
                type="text",
                text=(
                    f"Rendered {len(pages)} of {page_count} page(s) "
                    f"(dpi={dpi}, format={fmt_norm})"
                ),
            )
        )
    for page_number, data in pages:
        result.append(Image(data=data, format=fmt_norm))
    return result


@mcp.tool()
async def pdf_to_text(
    pdf_path: str,
    page_from: int = 1,
    page_to: int | None = None,
    layout: str = "blocks",
    include_metadata: bool = True,
) -> str:
    """Extract text from selected pages of a PDF file (Markdown output).

    Args:
        pdf_path: Absolute or relative path to a local PDF file.
        page_from: First page to extract (1-based). Default 1.
        page_to: Last page to extract (1-based, inclusive). None = to end (subject to limits).
        layout: "blocks" (preserve layout/columns) or "simple" (plain text order). Default "blocks".
        include_metadata: Prepend a short Markdown header. Default True.

    Returns:
        Markdown text with per-page sections.
    """
    if layout not in ("blocks", "simple"):
        from mcp.server.mcpserver.exceptions import ToolError

        raise ToolError("layout must be 'blocks' or 'simple'")
    try:
        page_count, pages = await extract_text(
            pdf_path=pdf_path,
            page_from=page_from,
            page_to=page_to,
            layout=layout,
        )
    except (ValidationError, ValueError) as exc:
        from mcp.server.mcpserver.exceptions import ToolError

        raise ToolError(str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to extract text from PDF: %s", pdf_path)
        from mcp.server.mcpserver.exceptions import ToolError

        raise ToolError(f"Failed to extract text from PDF: {exc}") from exc

    lines: list[str] = []
    if include_metadata:
        lines.append("# PDF Text Extraction")
        lines.append("")
        lines.append(f"- Pages: {len(pages)} of {page_count}")
        lines.append(f"- Layout: {layout}")
        lines.append("")
    for page_number, text in pages:
        lines.append(f"## Page {page_number}")
        lines.append("")
        lines.append(text if text else "_(no text)_")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


@mcp.tool()
async def pdf_to_lmstudio_script(
    pdf_path: str,
    dpi: int = 150,
    page_from: int = 1,
    page_to: int | None = None,
    format: str = "png",
    output_dir: str | None = None,
    prompt: str | None = None,
    model: str = "google/gemma-4-12b",
    base_url: str = "http://localhost:1234",
    auto_run: bool = True,
    run_timeout: int = 600,
    include_metadata: bool = True,
) -> str:
    """Render PDF pages to images next to the PDF and generate a Python script that
    sends each image to an LM Studio model (localhost:1234) for OCR + translation.

    Args:
        pdf_path: Absolute or relative path to a local PDF file.
        dpi: Rendering resolution (50..300). Default 150.
        page_from: First page to render (1-based). Default 1.
        page_to: Last page to render (1-based, inclusive). None = to end (subject to limits).
        format: Output image format: "png" or "jpeg". Default "png".
        output_dir: Directory to save images and script. Default: next to the PDF.
        prompt: Prompt sent to the model. Default: OCR + translate to Russian.
        model: LM Studio model id. Default "google/gemma-4-12b".
        base_url: LM Studio base URL. Default "http://localhost:1234".
        auto_run: Run the generated script immediately. Default True.
        run_timeout: Timeout in seconds when auto_run is True. Default 600.
        include_metadata: Prepend a short Markdown header. Default True.

    Returns:
        Markdown with saved file paths and the generated Python script.
    """
    fmt = "jpeg" if format.lower() in ("jpeg", "jpg") else "png"
    chunk_size = 50

    # Determine page count
    try:
        import pymupdf

        doc = pymupdf.open(pdf_path)
        total_pages = doc.page_count
        doc.close()
    except Exception as exc:  # pragma: no cover - defensive
        from mcp.server.mcpserver.exceptions import ToolError

        raise ToolError(f"Cannot open PDF: {exc}") from exc

    start = max(1, page_from)
    end = total_pages if page_to is None else min(page_to, total_pages)
    if start > end:
        from mcp.server.mcpserver.exceptions import ToolError

        raise ToolError("page_from exceeds document page count")

    chunks = list(range(start, end + 1, chunk_size))

    all_lines: list[str] = []
    if include_metadata:
        all_lines.append("# LM Studio translation script")
        all_lines.append("")
        all_lines.append(f"- Total pages: {end - start + 1} (chunks of {chunk_size})")
        all_lines.append(f"- Model: {model}")
        all_lines.append(f"- Base URL: {base_url}")
        all_lines.append(f"- Auto-run: {auto_run}")
        all_lines.append("")

    for idx, chunk_start in enumerate(chunks, 1):
        chunk_end = min(chunk_start + chunk_size - 1, end)
        script_filename = f"{Path(pdf_path).stem}_p{chunk_start:03d}-{chunk_end:03d}_translate.py"
        combined_filename = f"{Path(pdf_path).stem}_p{chunk_start:03d}-{chunk_end:03d}_translations.md"
        try:
            page_count, image_paths, script_path, script_content = await render_and_generate_script(
                pdf_path=pdf_path,
                dpi=dpi,
                page_from=chunk_start,
                page_to=chunk_end,
                fmt=fmt,
                output_dir=output_dir,
                prompt=prompt,
                model=model,
                base_url=base_url,
                script_filename=script_filename,
                combined_filename=combined_filename,
            )
        except (ValidationError, ValueError) as exc:
            from mcp.server.mcpserver.exceptions import ToolError

            raise ToolError(str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to generate LM Studio script for: %s", pdf_path)
            from mcp.server.mcpserver.exceptions import ToolError

            raise ToolError(f"Failed to generate script: {exc}") from exc

        if include_metadata:
            all_lines.append(f"## Chunk {idx}: pages {chunk_start}-{chunk_end}")
            all_lines.append("")
            all_lines.append(f"- Script: `{script_path}`")
            all_lines.append(f"- Combined: `{script_path.parent / combined_filename}`")
            all_lines.append("")
            if auto_run:
                try:
                    code, stdout, stderr, combined = await run_script(str(script_path), timeout=run_timeout)
                    all_lines.append(f"- Return code: {code}")
                    if combined.strip():
                        all_lines.append("")
                        all_lines.append("### Translations")
                        all_lines.append("")
                        all_lines.append(combined.strip())
                    if stderr.strip():
                        all_lines.append("")
                        all_lines.append("### stderr")
                        all_lines.append("")
                        all_lines.append("```")
                        all_lines.append(stderr.strip())
                        all_lines.append("```")
                except Exception as exc:  # pragma: no cover - defensive
                    all_lines.append(f"Failed to run script: {exc}")
            all_lines.append("")

    return "\n".join(all_lines).rstrip() + "\n"


@mcp.tool()
async def run_lmstudio_script(
    script_path: str,
    timeout: int = 600,
) -> str:
    """Run a previously generated LM Studio translation script and return its output.

    Args:
        script_path: Path to the generated *_translate.py script.
        timeout: Timeout in seconds. Default 600.

    Returns:
        Markdown with return code, stdout, stderr and translations.md contents.
    """
    try:
        code, stdout, stderr, combined = await run_script(script_path, timeout=timeout)
    except (FileNotFoundError, ValueError) as exc:
        from mcp.server.mcpserver.exceptions import ToolError

        raise ToolError(str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to run script: %s", script_path)
        from mcp.server.mcpserver.exceptions import ToolError

        raise ToolError(f"Failed to run script: {exc}") from exc

    lines: list[str] = []
    lines.append("# LM Studio script run")
    lines.append("")
    lines.append(f"- Script: `{script_path}`")
    lines.append(f"- Return code: {code}")
    lines.append("")
    if stdout.strip():
        lines.append("## stdout")
        lines.append("")
        lines.append("```")
        lines.append(stdout.strip())
        lines.append("```")
        lines.append("")
    if stderr.strip():
        lines.append("## stderr")
        lines.append("")
        lines.append("```")
        lines.append(stderr.strip())
        lines.append("```")
        lines.append("")
    if combined.strip():
        lines.append("## Translations")
        lines.append("")
        lines.append(combined.strip())
    return "\n".join(lines).rstrip() + "\n"
