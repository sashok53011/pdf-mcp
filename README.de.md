# pdf-mcp

MCP-Server für die Arbeit mit lokalen PDF-Dateien:
- `pdf_to_images`: rendert ausgewählte Seiten als PNG/JPEG-Bilder.
- `pdf_to_text`: extrahiert Text aus ausgewählten Seiten als Markdown (layout-erhaltend).

Sprachen: [English](README.md) | [Русский](README.ru.md) | Deutsch

## Installation

```bash
cd E:\mcp\pdf-mcp
pip install -e .
```

## Start (stdio)

```bash
python -m pdf_mcp
```

## Werkzeuge

### `pdf_to_images`

| Parameter | Typ | Standard | Beschreibung |
|---|---|---|---|
| `pdf_path` | string | erforderlich | Pfad zu einer lokalen PDF-Datei |
| `dpi` | int | 150 | Render-Auflösung (50..300) |
| `page_from` | int | 1 | Erste Seite (1-basiert) |
| `page_to` | int \| null | null | Letzte Seite (inklusive); null = bis Ende (unter Beachtung der Limits) |
| `format` | string | "png" | "png" oder "jpeg" |
| `jpeg_quality` | int | 90 | JPEG-Qualität (1..100) |
| `include_metadata` | bool | true | Kurze Textzusammenfassung voranstellen |

### `pdf_to_text`

| Parameter | Typ | Standard | Beschreibung |
|---|---|---|---|
| `pdf_path` | string | erforderlich | Pfad zu einer lokalen PDF-Datei |
| `page_from` | int | 1 | Erste Seite (1-basiert) |
| `page_to` | int \| null | null | Letzte Seite (inklusive); null = bis Ende (unter Beachtung der Limits) |
| `layout` | string | "blocks" | "blocks" (Layout/Spalten erhalten) oder "simple" |
| `include_metadata` | bool | true | Markdown-Header voranstellen |

Limits: maximal 50 Seiten pro Aufruf, maximal 300 DPI, PDF maximal 100 MB.

### `pdf_to_lmstudio_script`

Rendert PDF-Seiten als Bilder neben der PDF und erzeugt ein Python-Skript, das jedes
Bild an ein LM-Studio-Modell sendet (`http://localhost:1234`, Standardmodell
`google/gemma-4-12b`) für OCR + Übersetzung ins Russische.

| Parameter | Typ | Standard | Beschreibung |
|---|---|---|---|
| `pdf_path` | string | erforderlich | Pfad zu einer lokalen PDF-Datei |
| `dpi` | int | 150 | Render-Auflösung (50..300) |
| `page_from` | int | 1 | Erste Seite (1-basiert) |
| `page_to` | int \| null | null | Letzte Seite (inklusive); null = bis Ende (unter Beachtung der Limits) |
| `format` | string | "png" | "png" oder "jpeg" |
| `output_dir` | string \| null | null | Ordner für Bilder und Skript (Standard: neben der PDF) |
| `prompt` | string \| null | null | Prompt für das Modell (Standard: OCR + Übersetzung ins Russische) |
| `model` | string | "google/gemma-4-12b" | LM-Studio-Modell-ID |
| `base_url` | string | "http://localhost:1234" | LM-Studio-Basis-URL |
| `auto_run` | bool | true | Erzeugtes Skript sofort ausführen |
| `run_timeout` | int | 600 | Timeout in Sekunden bei auto_run=True |
| `include_metadata` | bool | true | Kurze Textzusammenfassung voranstellen |

### `run_lmstudio_script`

Ein zuvor erzeugtes LM-Studio-Übersetzungsskript ausführen und dessen Ausgabe zurückgeben.

| Parameter | Typ | Standard | Beschreibung |
|---|---|---|---|
| `script_path` | string | erforderlich | Pfad zum erzeugten `*_translate.py`-Skript |
| `timeout` | int | 600 | Timeout in Sekunden |

## Beispielkonfiguration (OpenCode / Claude Desktop / LM Studio)

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
