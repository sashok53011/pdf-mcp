"""MCP server entry: registers the pdf_to_images tool."""

import logging

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.utilities.types import Image
from mcp.types import TextContent

from .config import DEFAULT_DPI, DEFAULT_FORMAT, DEFAULT_JPEG_QUALITY
from .renderer import render_pdf
from .text import extract_text
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
