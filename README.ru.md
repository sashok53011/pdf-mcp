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

### `pdf_to_lmstudio_script`

Рендерит страницы PDF в изображения рядом с PDF и генерирует Python-скрипт, который
отправляет каждое изображение в модель LM Studio (`http://localhost:1234`, по умолчанию
`google/gemma-4-12b`) для OCR + перевода на русский.

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `pdf_path` | string | обязательно | Путь к локальному PDF-файлу |
| `dpi` | int | 150 | Разрешение рендера (50..300) |
| `page_from` | int | 1 | Первая страница (с 1) |
| `page_to` | int \| null | null | Последняя страница (включительно); null = до конца (с учётом лимитов) |
| `format` | string | "png" | "png" или "jpeg" |
| `output_dir` | string \| null | null | Папка для сохранения изображений и скрипта (по умолчанию рядом с PDF) |
| `prompt` | string \| null | null | Промпт для модели (по умолчанию OCR + перевод на русский) |
| `model` | string | "google/gemma-4-12b" | Идентификатор модели LM Studio |
| `base_url` | string | "http://localhost:1234" | Базовый URL LM Studio |
| `auto_run` | bool | true | Запустить сгенерированный скрипт сразу |
| `run_timeout` | int | 600 | Таймаут в секундах при auto_run=True |
| `include_metadata` | bool | true | Добавить краткую текстовую сводку |

### `run_lmstudio_script`

Запустить ранее сгенерированный скрипт перевода LM Studio и вернуть его вывод.

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `script_path` | string | обязательно | Путь к сгенерированному скрипту `*_translate.py` |
| `timeout` | int | 600 | Таймаут в секундах |

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
