"""Render PDF pages and generate a Python script for LM Studio translation."""

import asyncio
from pathlib import Path
from typing import List, Tuple

from .renderer import render_pdf_sync
from .validation import validate_pdf_path

DEFAULT_MODEL = "google/gemma-4-12b"
DEFAULT_BASE_URL = "http://localhost:1234"
DEFAULT_PROMPT = (
    "Распознай весь текст на изображении страницы PDF и переведи его на русский язык. "
    "Сохрани структуру и абзацы. Верни только переведённый текст."
)


def _generate_script(
    image_paths: List[Path],
    model: str,
    base_url: str,
    prompt: str,
) -> str:
    images_repr = repr([str(p) for p in image_paths])
    return f'''#!/usr/bin/env python
"""Auto-generated: send rendered PDF pages to LM Studio for OCR + translation."""

import base64
import json
from pathlib import Path

import requests

BASE_URL = {base_url!r}
MODEL = {model!r}
PROMPT = {prompt!r}
IMAGES = {images_repr}


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def ask(image_path: str) -> str:
    b64 = encode_image(image_path)
    payload = {{
        "model": MODEL,
        "messages": [
            {{
                "role": "user",
                "content": [
                    {{"type": "text", "text": PROMPT}},
                    {{"type": "image_url", "image_url": {{"url": f"data:image/png;base64,{{b64}}"}}}},
                ],
            }}
        ],
        "temperature": 0.2,
        "max_tokens": 4096,
    }}
    response = requests.post(f"{{BASE_URL}}/v1/chat/completions", json=payload, timeout=300)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    results = {{}}
    for image in IMAGES:
        print(f"Processing {{image}} ...")
        try:
            text = ask(image)
        except Exception as exc:  # noqa: BLE001
            text = f"ERROR: {{exc}}"
        results[image] = text
        page_file = out_dir / (Path(image).stem + "_translation.txt")
        page_file.write_text(text, encoding="utf-8")
        print(f"  -> {{page_file}}")

    combined = out_dir / "translations.md"
    with combined.open("w", encoding="utf-8") as f:
        for image, text in results.items():
            f.write(f"# {{image}}\\n\\n{{text}}\\n\\n---\\n\\n")
    print(f"Done. Combined output: {{combined}}")


if __name__ == "__main__":
    main()
'''


def render_and_generate_script_sync(
    pdf_path: str,
    dpi: int = 150,
    page_from: int = 1,
    page_to: int | None = None,
    fmt: str = "png",
    output_dir: str | None = None,
    prompt: str | None = None,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
) -> Tuple[int, List[Path], Path, str]:
    path = validate_pdf_path(pdf_path)
    page_count, pages = render_pdf_sync(pdf_path, dpi=dpi, page_from=page_from, page_to=page_to, fmt=fmt)

    out_dir = Path(output_dir) if output_dir else path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    image_paths: List[Path] = []
    for page_number, data in pages:
        image_name = f"{path.stem}_page_{page_number:03d}.{fmt}"
        image_path = out_dir / image_name
        image_path.write_bytes(data)
        image_paths.append(image_path)

    prompt_text = prompt or DEFAULT_PROMPT
    script_content = _generate_script(image_paths, model, base_url, prompt_text)
    script_path = out_dir / f"{path.stem}_translate.py"
    script_path.write_text(script_content, encoding="utf-8")

    return page_count, image_paths, script_path, script_content


async def render_and_generate_script(
    pdf_path: str,
    dpi: int = 150,
    page_from: int = 1,
    page_to: int | None = None,
    fmt: str = "png",
    output_dir: str | None = None,
    prompt: str | None = None,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
) -> Tuple[int, List[Path], Path, str]:
    return await asyncio.to_thread(
        render_and_generate_script_sync,
        pdf_path,
        dpi,
        page_from,
        page_to,
        fmt,
        output_dir,
        prompt,
        model,
        base_url,
    )
