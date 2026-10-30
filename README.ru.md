# pdf-mcp

MCP-сервер для работы с локальными PDF-файлами:
- `pdf_to_images`: рендер выбранных страниц в изображения PNG/JPEG.
- `pdf_to_text`: извлечение текста со страниц в Markdown (с сохранением разметки).

Языки: [English](README.md) | Русский | [Deutsch](README.de.md)

## Установка

```bash
cd E:\mcp\pdf-mcp
pip install -e .
```

## Запуск (stdio)

```bash
python -m pdf_mcp
```

## Инструменты

### `pdf_to_images`

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `pdf_path` | string | обязательно | Путь к локальному PDF-файлу |
| `dpi` | int | 150 | Разрешение рендера (50..300) |
| `page_from` | int | 1 | Первая страница (с 1) |
| `page_to` | int \| null | null | Последняя страница (включительно); null = до конца (с учётом лимитов) |
| `format` | string | "png" | "png" или "jpeg" |
| `jpeg_quality` | int | 90 | Качество JPEG (1..100) |
| `include_metadata` | bool | true | Добавить краткую текстовую сводку |

### `pdf_to_text`

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `pdf_path` | string | обязательно | Путь к локальному PDF-файлу |
| `page_from` | int | 1 | Первая страница (с 1) |
| `page_to` | int \| null | null | Последняя страница (включительно); null = до конца (с учётом лимитов) |
| `layout` | string | "blocks" | "blocks" (сохранять разметку/колонки) или "simple" |
| `include_metadata` | bool | true | Добавить заголовок Markdown |

Лимиты: не более 50 страниц за вызов, не более 300 DPI, PDF не более 100 МБ.

## Пример конфигурации (OpenCode / Claude Desktop / LM Studio)

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

## Тесты

```bash
pytest -q
```
