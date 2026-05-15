"""Text extraction for PDFs and images.

Two paths:

1. **Digital PDFs** — :mod:`pymupdf` extracts the embedded text layer.
   ~90 % of archive PDFs have one, and this is two orders of magnitude
   faster than OCR (~30 ms vs ~10 s per page).
2. **Scanned PDFs / images** — :func:`pytesseract.image_to_string` runs
   Tesseract over rendered pages or raw image bytes.

The fallback trigger is "embedded text is sparse" — if PyMuPDF gives us
fewer than :data:`MIN_EMBEDDED_TEXT_CHARS` characters across the whole
PDF, we re-render and OCR.

Tesseract is configured with ``lang="uzb+uzb_cyrl+rus+eng"`` to handle the
script soup typical of Ministry archives. The container in
``Dockerfile.worker`` ships all four language packs.

Public surface: :func:`extract_text` (sync, CPU-bound; callers from async
code should ``run_in_executor`` it).
"""
from __future__ import annotations

import io
import logging
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image

log = logging.getLogger("ocr")


# Below this character count we assume the PDF is scanned (no usable text
# layer) and fall back to Tesseract. 100 is conservative — most empty PDFs
# still ship a few dozen bytes of metadata-like noise; a real text layer
# starts in the thousands.
MIN_EMBEDDED_TEXT_CHARS = 100

# Render scanned PDFs at this DPI before passing to Tesseract. 300 is the
# standard sweet spot — lower hurts accuracy on small fonts; higher costs
# CPU/RAM without measurable gains for archive scans.
PDF_RENDER_DPI = 300

# Languages handed to Tesseract. Order matters slightly for ambiguous
# glyphs; Uzbek Latin first because most modern Ministry docs use it.
TESSERACT_LANGS = "uzb+uzb_cyrl+rus+eng"

PDF_SUFFIXES = {".pdf"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def extract_text(file_path: str | Path) -> str:
    """Extract plain-text content from ``file_path``.

    Returns an empty string on unknown formats or unrecoverable errors —
    callers decide whether that means "skipped" or "failed" based on the
    file extension. Exceptions never propagate.
    """
    path = Path(file_path)
    if not path.exists():
        log.warning("extract_text: missing %s", path)
        return ""

    suffix = path.suffix.lower()
    try:
        if suffix in PDF_SUFFIXES:
            return _extract_from_pdf(path)
        if suffix in IMAGE_SUFFIXES:
            return _ocr_image_path(path)
        log.info("extract_text: unsupported suffix %s — skipped", suffix)
        return ""
    except Exception:  # noqa: BLE001 — log + return empty, never raise
        log.exception("extract_text: %s", path)
        return ""


def _extract_from_pdf(path: Path) -> str:
    """Fast path via embedded text; falls through to Tesseract when sparse."""
    with fitz.open(path) as doc:
        pages = [page.get_text() for page in doc]
    embedded = "\n".join(pages).strip()
    if len(embedded) >= MIN_EMBEDDED_TEXT_CHARS:
        log.debug("pdf %s: embedded text %d chars", path.name, len(embedded))
        return embedded

    log.info("pdf %s: embedded text sparse (%d chars) — OCR fallback", path.name, len(embedded))
    images = convert_from_path(str(path), dpi=PDF_RENDER_DPI)
    return _ocr_images(images)


def _ocr_image_path(path: Path) -> str:
    with Image.open(path) as img:
        return _ocr_images([img])


def _ocr_images(images: list[Image.Image]) -> str:
    """Run Tesseract over every image and return concatenated text."""
    chunks: list[str] = []
    for i, img in enumerate(images):
        try:
            text = pytesseract.image_to_string(img, lang=TESSERACT_LANGS)
        except pytesseract.TesseractError:
            log.exception("tesseract failed on page %d", i + 1)
            continue
        if text.strip():
            chunks.append(text)
    return "\n".join(chunks).strip()
