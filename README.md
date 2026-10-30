# pdf-mcp

MCP server for working with local PDF files:
- `pdf_to_images`: render selected pages to PNG/JPEG images.
- `pdf_to_text`: extract text from selected pages as Markdown (layout-preserving).

## Install

```bash
cd E:\mcp\pdf-mcp
pip install -e .
```

## Run (stdio)

```bash
python -m pdf_mcp
```

## Tools

### `pdf_to_images`

| Param | Type | Default | Description |
|---|---|---|---|
| `pdf_path` | string | required | Path to a local PDF file |
| `dpi` | int | 150 | Render resolution (50..300) |
| `page_from` | int | 1 | First page (1-based) |
| `page_to` | int \| null | null | Last page (inclusive); null = to end (subject to limits) |
| `format` | string | "png" | "png" or "jpeg" |
| `jpeg_quality` | int | 90 | JPEG quality (1..100) |
| `include_metadata` | bool | true | Prepend a short text summary |

### `pdf_to_text`

| Param | Type | Default | Description |
|---|---|---|---|
| `pdf_path` | string | required | Path to a local PDF file |
| `page_from` | int | 1 | First page (1-based) |
| `page_to` | int \| null | null | Last page (inclusive); null = to end (subject to limits) |
| `layout` | string | "blocks" | "blocks" (preserve layout/columns) or "simple" |
| `include_metadata` | bool | true | Prepend a Markdown header |

Limits: max 50 pages per call, max 300 DPI, max 100 MB PDF.

## OpenCode / Claude Desktop / LM Studio config example

```json
{
  "mcpServers": {
    "pdf-mcp": {
      "command": "python",
      "args": ["-m", "pdf_mcp"],
      "cwd": "E:/mcp/pdf-mcp"
    }
  }
}
```

## Tests

```bash
pytest -q
```
