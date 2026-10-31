# pdf-mcp

Languages: English | [Русский](README.ru.md) | [Deutsch](README.de.md)

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

### `pdf_to_lmstudio_script`

Renders PDF pages to images next to the PDF and generates a Python script that sends
each image to an LM Studio model (`http://localhost:1234`, default model `google/gemma-4-12b`)
for OCR + translation to Russian. If `page_to` is omitted, the whole document is
processed in chunks of 50 pages. The script runs automatically by default.

| Param | Type | Default | Description |
|---|---|---|---|
| `pdf_path` | string | required | Path to a local PDF file |
| `dpi` | int | 150 | Render resolution (50..300) |
| `page_from` | int | 1 | First page (1-based) |
| `page_to` | int \| null | null | Last page (inclusive); null = to end (subject to limits) |
| `format` | string | "png" | "png" or "jpeg" |
| `output_dir` | string \| null | null | Directory to save images and script (default: next to PDF) |
| `prompt` | string \| null | null | Prompt sent to the model (default: OCR + translate to Russian) |
| `model` | string | "google/gemma-4-12b" | LM Studio model id |
| `base_url` | string | "http://localhost:1234" | LM Studio base URL |
| `auto_run` | bool | true | Run the generated script immediately |
| `run_timeout` | int | 600 | Timeout in seconds when auto_run is True |
| `include_metadata` | bool | true | Prepend a short Markdown header |

### `run_lmstudio_script`

Run a previously generated LM Studio translation script and return its output.

| Param | Type | Default | Description |
|---|---|---|---|
| `script_path` | string | required | Path to the generated `*_translate.py` script |
| `timeout` | int | 600 | Timeout in seconds |

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
