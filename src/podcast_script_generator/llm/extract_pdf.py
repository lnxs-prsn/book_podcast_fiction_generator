"""Section 2: extract_pdf — extract all text from a PDF as a single string."""

import fitz  # pymupdf


def _ocr_page(doc: fitz.Document, page_idx: int) -> str:
    """OCR a single image-based page via pytesseract."""
    try:
        import io
        import pytesseract
        from PIL import Image

        pix = doc[page_idx].get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def extract_pdf(pdf_path: str) -> str:
    """Return all page text from pdf_path joined with double newlines.

    Falls back to OCR (pytesseract) for image-only / scanned pages.
    Raises ValueError if the file cannot be opened or yields no text at all.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError(f"Cannot open PDF: {pdf_path}") from e

    try:
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if not text:
                text = _ocr_page(doc, i)
            pages.append(text)
    finally:
        doc.close()

    pdf_text = "\n\n".join(pages)

    if not pdf_text.strip():
        raise ValueError(f"No extractable text in PDF: {pdf_path}")

    return pdf_text
