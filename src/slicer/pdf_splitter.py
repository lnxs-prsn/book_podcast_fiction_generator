#!/usr/bin/env python3
"""
PDF Chapter Splitter — Orchestration-ready CLI tool.

Core API: run_splitter(...)
CLI entry: main()
"""

from __future__ import annotations

import argparse
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import os
import re
import sys
import time
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from llm.exceptions import LLMConfigError
from llm.exceptions import LLMError
from llm.protocol import LLMClient

try:
    import ocrmypdf
    _OCRMYPDF_AVAILABLE = True
except ImportError:
    _OCRMYPDF_AVAILABLE = False

# --- Defaults ---
DEFAULT_TOC_PAGE = 8
DEFAULT_LEVEL = 1
DEFAULT_OUTPUT_DIR = "split_chapters"
DEFAULT_PREFIX = "chapter"
# ----------------

# Type alias for TOC entries: (level, title, start_page)
TocEntry = Tuple[int, str, int]


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')


def get_toc_from_bookmarks(pdf_path: str, target_level: int) -> Optional[List[TocEntry]]:
    """Stage 1: Try to get TOC from PDF's internal bookmarks.

    Detects when bookmarks store printed page numbers instead of PDF page
    positions and corrects them using the PDF's page label ranges.
    """
    try:
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        offset = 0
        for label in doc.get_page_labels():
            if label.get('style') == 'D' and label.get('firstpagenum', 1) == 1:
                offset = label['startpage']
                break
        doc.close()
        if toc:
            chapters = [
                (level, title.strip(), int(page))
                for level, title, page in toc
                if level == target_level
            ]
            if chapters and offset > 0:
                min_page = min(p for _, _, p in chapters)
                if min_page < offset + 1:
                    chapters = [(lvl, t, p + offset) for lvl, t, p in chapters]
                    logging.info(f"Stage 1: applied page label offset +{offset} (bookmarks used printed page numbers).")
            if chapters:
                logging.info(f"Stage 1: Found {len(chapters)} top-level bookmarks.")
                return chapters
    except Exception as e:
        logging.warning(f"Stage 1 failed: {e}")
    return None


def get_text_from_toc_page(pdf_path: str, page_num: int) -> Optional[str]:
    """Stage 2: Extract raw text from a specific PDF page using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        if page_num - 1 < len(doc):
            text = doc.load_page(page_num - 1).get_text()
            doc.close()
            if text and text.strip():
                return text.strip()
        doc.close()
    except Exception as e:
        logging.warning(f"Stage 2 text extraction failed: {e}")
    return None


def get_ocr_text_from_toc_page(pdf_path: str, page_num: int, use_text: bool = False) -> Optional[str]:
    """Stage 3: Use OCR to extract text from image-based pages.

    When use_text=True the PDF already has an embedded text layer; OCR adds
    nothing that Stage 2 did not already try, so return None immediately.
    """
    if use_text:
        return None
    try:
        images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num, dpi=300)
        if images:
            text = pytesseract.image_to_string(images[0])
            if text and text.strip():
                return text.strip()
    except Exception as e:
        logging.warning(f"Stage 3 OCR failed: {e}")
    return None


def parse_toc_from_text(toc_text: str) -> List[TocEntry]:
    """Stage 2/3 parsing: Extract chapter titles and start pages from TOC text."""
    chapters: List[TocEntry] = []
    lines = toc_text.splitlines()
    
    pattern_dots = re.compile(
        r'^(?:Chapter\s+)?(\d+|[A-Z][a-z]+)\s*[:\-]?\s*(.*?)\s+\.+\s+(\d+)$',
        re.IGNORECASE
    )
    pattern_spaces = re.compile(
        r'^(?:Chapter\s+)?(\d+|[A-Z][a-z]+)\s*[:\-]?\s*(.*?)\s{3,}(\d+)$',
        re.IGNORECASE
    )
    pattern_simple = re.compile(
        r'^(\d+)\s*[\.\)]\s+(.*?)\s+(\d+)$',
        re.IGNORECASE
    )

    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = (pattern_dots.match(line) or 
                 pattern_spaces.match(line) or 
                 pattern_simple.match(line))
        if match:
            chap_num, title, page_num = match.groups()
            title = title.strip()
            if not title:
                title = f"Chapter {chap_num}"
            chapters.append((1, title, int(page_num)))
    
    if chapters:
        logging.info(f"Stage 2/3: Parsed {len(chapters)} chapters from text.")
    return chapters


def _ocr_pages_text(pdf_path: str, first_page: int, last_page: int, dpi: int = 200) -> str:
    """OCR a range of pages and return combined text with [PDF PAGE N] markers."""
    images = convert_from_path(pdf_path, first_page=first_page, last_page=last_page, dpi=dpi)
    parts = []
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img)
        parts.append(f"[PDF PAGE {first_page + i}]\n{text.strip()}")
    return "\n\n".join(parts)


def _get_total_pages(pdf_path: str) -> int:
    try:
        doc = fitz.open(pdf_path)
        n = len(doc)
        doc.close()
        return n
    except Exception:
        return 0


def _detect_page_offset(sample_text: str, total_pages: int) -> Optional[int]:
    """
    Infer PDF_page minus printed_page from OCR'd sample pages.

    Each block is prefixed [PDF PAGE N]. Scans headers/footers (first/last
    two lines of each block) for standalone arabic numerals that are smaller
    than the PDF page index — those are printed page numbers. Returns the
    median difference, or None if no reliable signal is found.
    """
    offsets = []
    blocks = re.split(r'\[PDF PAGE (\d+)\]', sample_text)
    i = 1
    while i + 1 < len(blocks):
        try:
            pdf_page = int(blocks[i])
        except ValueError:
            i += 2
            continue
        text = blocks[i + 1]
        i += 2
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        candidates = lines[:2] + (lines[-2:] if len(lines) > 4 else [])
        for line in candidates:
            if re.match(r'^[ivxlcdmIVXLCDM]+$', line, re.IGNORECASE):
                continue  # roman numerals are front matter, not useful
            if re.match(r'^\d+$', line):
                printed = int(line)
                if 1 <= printed < pdf_page:
                    offsets.append(pdf_page - printed)
                    break
            m = re.match(r'^(\d+)\s', line) or re.search(r'\s(\d+)$', line)
            if m:
                printed = int(m.group(1))
                if 1 <= printed < pdf_page:
                    offsets.append(pdf_page - printed)
                    break
    if not offsets:
        return None
    offsets.sort()
    median = offsets[len(offsets) // 2]
    logging.debug(f"Stage 4: offset candidates {offsets}, using {median}")
    return median


def _validate_toc(toc: List[TocEntry], total_pages: int) -> bool:
    """
    Return True if TOC entries are spread plausibly across the PDF.

    Fails when:
    - All entries cluster within 5 % of total pages (LLM returned printed page
      numbers instead of PDF positions), OR
    - Entries concentrate on too few unique pages (LLM returned the PDF page
      of each TOC list row rather than the actual content start page).
    """
    if not toc or total_pages < 10:
        return bool(toc)
    pages = [page for _, _, page in toc]
    span = max(pages) - min(pages)
    if span < max(total_pages * 0.05, 5):
        return False
    # If many entries share very few unique pages, the LLM mapped TOC row
    # positions instead of content positions.
    unique_pages = len(set(pages))
    if len(toc) >= 5 and unique_pages < max(len(toc) * 0.25, 4):
        return False
    return True


def get_toc_from_llm(
    pdf_path: str,
    llm: LLMClient | None = None,
    use_text: bool = False,
) -> Optional[List[TocEntry]]:
    """Stage 4: send front matter + page samples to the LLM to identify structure.

    When use_text=True the PDF has an embedded text layer; fitz text extraction
    is used instead of OCR, which is faster and more reliable.
    """
    if llm is None:
        return None

    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
    except Exception as e:
        logging.warning(f"Stage 4: cannot open PDF: {e}")
        return None

    scan_end = min(20, total_pages)
    sample_pages = sorted({max(1, int(total_pages * f)) for f in (0.2, 0.35, 0.5)})

    if use_text:
        logging.info(f"Stage 4: extracting text from pages 1–{scan_end} for LLM analysis...")
        doc = fitz.open(pdf_path)
        front_text = "\n\n".join(
            f"[PDF PAGE {p}]\n{doc[p - 1].get_text().strip()}"
            for p in range(1, scan_end + 1)
        )
        logging.info(f"Stage 4: extracting sample pages {sample_pages} for offset detection...")
        sample_text = "\n\n".join(
            f"[PDF PAGE {p}]\n{doc[p - 1].get_text().strip()}"
            for p in sample_pages
        )
        doc.close()
    else:
        logging.info(f"Stage 4: OCR-ing pages 1–{scan_end} for LLM analysis...")
        front_text = _ocr_pages_text(pdf_path, 1, scan_end, dpi=200)
        logging.info(f"Stage 4: OCR-ing sample pages {sample_pages} for offset detection...")
        sample_text = "\n\n".join(
            _ocr_pages_text(pdf_path, p, p, dpi=150) for p in sample_pages
        )

    prompt = f"""\
You are analyzing a scanned book PDF to extract its structure for automated splitting.

You are given:
1. OCR text from the first {scan_end} PDF pages (front matter and table of contents).
2. OCR samples from three pages deeper in the book, each marked [PDF PAGE N].

Your task — follow these steps exactly:

STEP 1 — Find the Table of Contents in the front matter text.
STEP 2 — For each top-level division (PART, Chapter, or equivalent major section), read the
          PRINTED page number listed next to it in the TOC (e.g. "Chapter 2 ..... 47" → printed page 47).
STEP 3 — Compute the page offset using the sample pages:
          offset = [PDF PAGE N] − (printed page number visible on that sample page).
          Use the most consistent offset across all samples.
STEP 4 — Convert: PDF_PAGE = printed_page_from_TOC + offset.
STEP 5 — Output one line per top-level division.

CRITICAL RULES:
- NEVER output the [PDF PAGE N] of the TOC row itself. Those are where entries are LISTED,
  not where the content STARTS. The content starts pages later.
- Use only the printed page numbers from the TOC entries, then add the offset.
- Skip front matter (cover, copyright, preface, foreword).
- Aim for major structural divisions only (PARTs or numbered Chapters), not subsections.

Output format — ONLY these lines, no explanation:
ENTRY: <title> | PDF_PAGE: <number>

=== FRONT MATTER + TOC (PDF pages 1–{scan_end}) ===
{front_text}

=== SAMPLE PAGES (for offset detection) ===
{sample_text}
"""

    logging.info("Stage 4: calling LLM...")
    try:
        response = llm.call(prompt=prompt)
    except LLMError as e:
        logging.warning(f"Stage 4: LLM call failed: {e}")
        return None

    toc: List[TocEntry] = []
    for line in response.splitlines():
        # re.search handles leading markdown (**, -, etc); separator tolerates |, -, /
        m = re.search(
            r"ENTRY:\s*(.+?)\s*[|\-/]\s*PDF_PAGE:\s*(\d+)",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            title = m.group(1).strip().strip("*_")
            page = int(m.group(2))
            if 1 <= page <= total_pages:
                toc.append((1, title, page))

    if not toc:
        logging.warning("Stage 4: LLM response had no parseable ENTRY lines.")
        logging.debug(f"Stage 4 raw response:\n{response}")
        return None

    # Sort by page and deduplicate (same title+page)
    toc.sort(key=lambda x: x[2])
    seen: set = set()
    deduped: List[TocEntry] = []
    for entry in toc:
        key = (entry[1], entry[2])
        if key not in seen:
            seen.add(key)
            deduped.append(entry)
    toc = deduped

    # Option 2: if entries cluster in a small page range the LLM likely returned
    # printed page numbers rather than PDF positions. Compute offset from the
    # sample pages and re-apply it; if that passes validation, use the result.
    if not _validate_toc(toc, total_pages):
        offset = _detect_page_offset(sample_text, total_pages)
        if offset is not None and offset > 0:
            adjusted = [
                (level, title, page + offset)
                for level, title, page in toc
                if 1 <= page + offset <= total_pages
            ]
            if adjusted and _validate_toc(adjusted, total_pages):
                logging.info(f"Stage 4: offset +{offset} corrected entries to span PDF correctly.")
                toc = adjusted

    logging.info(f"Stage 4: LLM identified {len(toc)} sections.")
    return toc


def get_toc_from_content_scan(
    pdf_path: str,
    use_text: bool = False,
    skip_before: int = 0,
) -> Optional[List[TocEntry]]:
    """Stage 5: scan page content for part/chapter headings.

    skip_before: 0-based page index; scanning starts here, skipping front
    matter (cover, TOC, etc.) so they cannot produce false positives.

    use_text: when True the PDF has an embedded text layer — use get_text()
    instead of rendering and OCR-ing each page.
    """
    import io

    if not use_text:
        try:
            from PIL import Image
        except ImportError:
            logging.warning("Stage 5: Pillow not available — skipping.")
            return None

    heading_re = re.compile(
        r'^((?:PART|CHAPTER|SECTION)\s+(?:[IVXLCDM]+|\d+)\b[^\n]*)',
        re.IGNORECASE,
    )

    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
    except Exception as e:
        logging.warning(f"Stage 5: cannot open PDF: {e}")
        return None

    scan_pages = total_pages - skip_before
    if use_text:
        logging.info(f"Stage 5: scanning {scan_pages} pages for headings (text extraction)...")
    else:
        logging.info(
            f"Stage 5: scanning {scan_pages} pages for headings "
            f"(top-of-page crop, 1.5× zoom — may take a moment)..."
        )

    found: List[TocEntry] = []
    mat = fitz.Matrix(1.5, 1.5)

    for i in range(skip_before, total_pages):
        try:
            page = doc[i]
            if use_text:
                text = page.get_text()
            else:
                r = page.rect
                clip = fitz.Rect(r.x0, r.y0, r.x1, r.y0 + r.height * 0.25)
                pix = page.get_pixmap(matrix=mat, clip=clip)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                text = pytesseract.image_to_string(img)
        except Exception:
            continue
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for line in lines[:6]:
            m = heading_re.match(line)
            if m:
                title = m.group(1).strip()
                logging.info(f"Stage 5: heading at PDF page {i + 1}: {title!r}")
                found.append((1, title, i + 1))
                break

    doc.close()
    if found:
        logging.info(f"Stage 5: found {len(found)} sections.")
        return found
    logging.warning("Stage 5: no headings found.")
    return None


def _normalize_title(title: str) -> str:
    t = title.lower()
    t = re.sub(r'[^\w\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def _titles_match(t1: str, t2: str) -> bool:
    """True if two titles are close enough to represent the same section."""
    n1, n2 = _normalize_title(t1), _normalize_title(t2)
    return n1 == n2 or n1 in n2 or n2 in n1


def combine_llm_and_scan(
    toc4: List[TocEntry],
    toc5: List[TocEntry],
    total_pages: int,
) -> List[TocEntry]:
    """Merge Stage 4 (rich titles, possibly wrong pages) with Stage 5 (verified positions).

    For each Stage 5 entry, substitute the matching Stage 4 title when one exists.
    Compute a median page offset from matched pairs, then apply it to Stage 4-only
    entries so finer-grained sections from the LLM survive at corrected positions.
    """
    offsets: List[int] = []
    result: List[TocEntry] = []
    used4: set = set()

    for l5, t5, p5 in toc5:
        match_idx = None
        for i, (l4, t4, _) in enumerate(toc4):
            if i not in used4 and _titles_match(t4, t5):
                match_idx = i
                break
        if match_idx is not None:
            l4, t4, p4 = toc4[match_idx]
            used4.add(match_idx)
            offsets.append(p5 - p4)
            result.append((l4, t4, p5))
            logging.info(f"Stage 4+5: matched '{t4}' → PDF page {p5} (Stage 4 had {p4})")
        else:
            result.append((l5, t5, p5))

    offset: Optional[int] = None
    if offsets:
        offsets_s = sorted(offsets)
        offset = offsets_s[len(offsets_s) // 2]
        logging.info(f"Stage 4+5: median page offset {offset:+d} from {len(offsets)} matched pairs")

    existing_pages = {p for _, _, p in result}
    for i, (l4, t4, p4) in enumerate(toc4):
        if i in used4:
            continue
        pdf_page = (p4 + offset) if offset is not None else p4
        if 1 <= pdf_page <= total_pages and pdf_page not in existing_pages:
            result.append((l4, t4, pdf_page))
            existing_pages.add(pdf_page)
            logging.info(f"Stage 4+5: added Stage 4-only '{t4}' at PDF page {pdf_page}")

    result.sort(key=lambda x: x[2])
    logging.info(f"Stage 4+5: combined result — {len(result)} entries.")
    return result


def filter_chapters_only(toc: List[TocEntry]) -> List[TocEntry]:
    """
    Keep only entries from Chapter 1 onward.
    Drops front matter like Cover, Copyright, Dedication, Preface, etc.
    """
    for i, (level, title, page) in enumerate(toc):
        # Match "Chapter 1", "1 Introduction", "Chapter One", "1: Foo" ...
        if re.search(r'^(?:chapter\s*)?(1|one)\b', title.strip(), re.IGNORECASE):
            if i > 0:
                skipped = [t[1] for t in toc[:i]]
                logging.info(f"--chapters-only: skipped front matter: {skipped}")
            return toc[i:]
    
    logging.warning("--chapters-only: Could not find 'Chapter 1' entry. Keeping all TOC entries.")
    return toc


def sanitize_filename(title: str, max_length: int = 50) -> str:
    """Clean chapter title for use as a filename."""
    cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
    cleaned = re.sub(r'\s+', '_', cleaned)
    cleaned = cleaned.strip('._')
    return cleaned[:max_length] or "untitled"


def _is_scanned(pdf_path: str, sample_pages: int = 10) -> bool:
    """Return True if the PDF is image-only (no extractable text on most sampled pages)."""
    try:
        doc = fitz.open(pdf_path)
        total = len(doc)
        indices = sorted({int(total * f) % total for f in (
            0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95
        )})[:sample_pages]
        texts = [doc[i].get_text().strip() for i in indices]
        doc.close()
        return sum(1 for t in texts if not t) > len(texts) // 2
    except Exception:
        return False


def extract_toc(
    pdf_path: str,
    toc_page_num: int,
    target_level: int,
    no_ocr: bool = False,
    llm: LLMClient | None = None,
    is_scanned: bool = False,
    was_converted: bool = False,
) -> Tuple[Optional[List[TocEntry]], Optional[str]]:
    """Run the multi-stage TOC extraction pipeline. Returns (toc_list, source_name)."""
    toc = get_toc_from_bookmarks(pdf_path, target_level)
    if toc:
        return toc, "Stage 1 (Internal Bookmarks)"

    use_text = not is_scanned or was_converted
    logging.info(f"PDF type: {'scanned (image-only)' if is_scanned else 'native text'}")

    if use_text:
        toc_text = get_text_from_toc_page(pdf_path, toc_page_num)
        if toc_text:
            toc = parse_toc_from_text(toc_text)
            if toc:
                return toc, "Stage 2 (Direct Text Extraction)"

    if not no_ocr:
        ocr_text = get_ocr_text_from_toc_page(pdf_path, toc_page_num, use_text=use_text)
        if ocr_text:
            toc = parse_toc_from_text(ocr_text)
            if toc:
                return toc, "Stage 3 (OCR Fallback)"

    if not no_ocr:
        total = _get_total_pages(pdf_path)
        toc4 = get_toc_from_llm(pdf_path, llm=llm, use_text=use_text)

        if toc4 and use_text:
            return toc4, "Stage 4 (LLM Interpretation)"

        if toc4:
            logging.info("Stage 4: scanned PDF — combining with Stage 5 to verify page positions.")

        toc5 = get_toc_from_content_scan(pdf_path, use_text=use_text, skip_before=toc_page_num)

        if toc4 and toc5:
            combined = combine_llm_and_scan(toc4, toc5, total)
            if combined:
                return combined, "Stage 4+5 (LLM titles + content scan positions)"

        if toc5:
            return toc5, "Stage 5 (Content Scan)"

        if toc4:
            return toc4, "Stage 4 (LLM Interpretation, unvalidated)"

    return None, None


def _page_is_scanned(doc: fitz.Document, page_idx: int) -> bool:
    """Return True if a page has no extractable text (image-only / scanned)."""
    return not doc[page_idx].get_text().strip()


def _ocr_pages_to_pdf(pdf_path: str, first_page: int, last_page: int) -> fitz.Document:
    """Render pages to images, OCR each one, return a searchable fitz.Document.

    first_page / last_page are 1-based inclusive (pdf2image convention).
    """
    images = convert_from_path(pdf_path, first_page=first_page, last_page=last_page, dpi=300)
    result_doc = fitz.open()
    for img in images:
        pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension="pdf")
        page_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        result_doc.insert_pdf(page_doc)
        page_doc.close()
    return result_doc


def split_pdf_by_chapters(
    pdf_path: str,
    chapters: List[TocEntry],
    output_dir: str,
    prefix: str,
    dry_run: bool = False,
    ocr_embed: bool = False,
) -> List[Dict[str, Any]]:
    """
    Split PDF into separate files based on chapter start pages.
    Returns a list of metadata dicts for each created (or would-be-created) file.

    When ocr_embed=True, scanned (image-only) chapters are OCR'd with Tesseract
    and written as searchable PDFs. Text-based chapters are copied as normal.
    """
    if not dry_run:
        os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    results: List[Dict[str, Any]] = []

    for i, (level, title, start_page) in enumerate(chapters):
        start_idx = max(0, start_page - 1)

        if i + 1 < len(chapters):
            end_idx = chapters[i + 1][2] - 1
        else:
            end_idx = total_pages

        end_idx = min(end_idx, total_pages)

        if start_idx >= end_idx:
            logging.warning(f"Skipping '{title}': invalid range (page {start_page} >= {end_idx})")
            continue

        page_count = end_idx - start_idx
        safe_title = sanitize_filename(title)
        chap_num_str = str(i + 1).zfill(2)
        filename = f"{chap_num_str}_{prefix}_{safe_title}.pdf"
        output_path = os.path.join(output_dir, filename)

        result: Dict[str, Any] = {
            "filename": filename,
            "title": title,
            "start_page": start_page,
            "end_page": end_idx,
            "page_count": page_count,
            "output_path": output_path,
            "created": False,
            "ocr_embedded": False,
        }

        if dry_run:
            scanned = ocr_embed and _page_is_scanned(doc, start_idx)
            mode = " [OCR]" if scanned else ""
            logging.info(f"[DRY-RUN] Would create: {filename} ({page_count} pages){mode}")
        elif ocr_embed and _page_is_scanned(doc, start_idx):
            logging.info(f"OCR-embedding '{title}' ({page_count} pages) — this may take a moment...")
            new_doc = _ocr_pages_to_pdf(pdf_path, start_idx + 1, end_idx)
            new_doc.save(output_path)
            new_doc.close()
            logging.info(f"Created (OCR): {filename}")
            result["created"] = True
            result["ocr_embedded"] = True
        else:
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start_idx, to_page=end_idx - 1)
            new_doc.save(output_path)
            new_doc.close()
            logging.info(f"Created: {filename} ({page_count} pages)")
            result["created"] = True

        results.append(result)

    doc.close()
    return results


def _ensure_searchable(pdf_path: str, is_scanned: bool) -> Tuple[str, bool]:
    """
    If the PDF is scanned, return a searchable version of it and True.
    Converts once using OCRmyPDF and caches the result alongside the original.
    Returns (original_path, False) if conversion is not needed or not possible.
    """
    if not is_scanned:
        return pdf_path, False

    if not _OCRMYPDF_AVAILABLE:
        logging.warning("ocrmypdf not installed — skipping conversion. pip install ocrmypdf to enable.")
        return pdf_path, False

    p = Path(pdf_path)
    searchable_path = p.with_name(p.stem + "_searchable.pdf")

    if searchable_path.exists():
        logging.info(f"Searchable PDF already exists: {searchable_path}")
        return str(searchable_path), True

    total_pages = _get_total_pages(pdf_path)
    # Rough estimate for ARM/Raspberry Pi: ~30–90 s/page (CPU-only Tesseract)
    est_lo = max(1, total_pages * 30 // 60)
    est_hi = max(2, total_pages * 90 // 60)
    logging.info(
        f"Scanned PDF detected — {total_pages} pages. "
        f"Converting to searchable PDF (one-time). "
        f"Estimated time: {est_lo}–{est_hi} min."
    )
    logging.info(f"Output will be saved to: {searchable_path}")
    t0 = time.monotonic()
    ocrmypdf.ocr(pdf_path, str(searchable_path), skip_text=True, progress_bar=True)
    elapsed = time.monotonic() - t0
    logging.info(f"Conversion complete in {elapsed / 60:.1f} min: {searchable_path}")
    return str(searchable_path), True


def run_splitter(
    input_path: str,
    toc_page: int = DEFAULT_TOC_PAGE,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    prefix: str = DEFAULT_PREFIX,
    level: int = DEFAULT_LEVEL,
    no_ocr: bool = False,
    dry_run: bool = False,
    chapters_only: bool = False,
    verbose: bool = False,
    ocr_embed: bool = False,
    ocr_convert: bool = False,
    llm: LLMClient | None = None,
) -> Dict[str, Any]:
    """
    Orchestration-friendly entry point. Can be called directly from another Python script.
    
    Returns a dict with:
        success: bool
        source: str or None
        toc: list of extracted TOC entries
        files: list of file metadata dicts
        output_dir: str
        dry_run: bool
    """
    setup_logging(verbose)
    
    if not os.path.exists(input_path):
        logging.error(f"PDF not found: {input_path}")
        return {"success": False, "error": "File not found", "input_path": input_path}

    is_scanned = _is_scanned(input_path)
    if ocr_convert:
        input_path, was_converted = _ensure_searchable(input_path, is_scanned)
    else:
        if is_scanned and _OCRMYPDF_AVAILABLE:
            logging.info("Scanned PDF detected. OCR conversion skipped (pass ocr_convert=True to enable).")
        was_converted = False

    logging.info(f"Processing: {input_path}")
    logging.info(f"Looking for TOC on page {toc_page}")

    toc, source = extract_toc(
        input_path, toc_page, level, no_ocr, llm=llm,
        is_scanned=is_scanned, was_converted=was_converted,
    )
    
    if not toc:
        logging.error("All TOC extraction stages failed.")
        return {"success": False, "error": "TOC extraction failed", "input_path": input_path}
    
    if chapters_only:
        original_count = len(toc)
        toc = filter_chapters_only(toc)
        if len(toc) < original_count:
            logging.info(f"--chapters-only: reduced from {original_count} to {len(toc)} entries.")
    
    logging.info(f"Success using {source}. Splitting {len(toc)} chapters:")
    for level, title, page in toc:
        logging.info(f"  - {title} (page {page})")
    
    files = split_pdf_by_chapters(input_path, toc, output_dir, prefix, dry_run, ocr_embed)

    return {
        "success": True,
        "source": source,
        "toc": toc,
        "files": files,
        "output_dir": output_dir,
        "dry_run": dry_run,
        "ocr_embed": ocr_embed,
        "input_path": input_path
    }


def main():
    parser = argparse.ArgumentParser(
        description="Split a PDF into chapters using a 4-stage TOC extraction pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i book.pdf -p 10
  %(prog)s -i book.pdf --toc-page 12 --chapters-only
  %(prog)s -i book.pdf --dry-run -v
  
Python API:
  from pdf_splitter import run_splitter
  result = run_splitter("book.pdf", toc_page=10, chapters_only=True)
        """
    )
    
    parser.add_argument("-i", "--input", required=True, help="Path to input PDF file")
    parser.add_argument("-p", "--toc-page", type=int, default=DEFAULT_TOC_PAGE,
                        help=f"Page number containing the Table of Contents (default: {DEFAULT_TOC_PAGE})")
    parser.add_argument("-o", "--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help=f"Directory for output chapter files (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX,
                        help=f"Filename prefix for chapters (default: {DEFAULT_PREFIX})")
    parser.add_argument("--level", type=int, default=DEFAULT_LEVEL,
                        help=f"Bookmark level to extract (default: {DEFAULT_LEVEL})")
    parser.add_argument("--no-ocr", action="store_true",
                        help="Skip the OCR fallback stage for TOC extraction")
    parser.add_argument("--ocr-embed", action="store_true",
                        help="OCR scanned (image-only) pages and embed text into output chapter PDFs")
    parser.add_argument("--chapters-only", action="store_true",
                        help="Skip front matter (Cover, Copyright, etc.). Keep only from Chapter 1 onward.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be split without writing files")
    parser.add_argument("--ocr-convert", action="store_true",
                        help="Convert scanned PDF to searchable PDF before splitting (slow on ARM/Pi — opt-in)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging")
    
    args = parser.parse_args()

    from llm.env import resolve_from_env
    from llm.factory import create_client

    try:
        client = create_client(**resolve_from_env())
    except LLMConfigError as e:
        logging.error(f"LLM configuration error: {e}")
        client = None

    result = run_splitter(
        input_path=args.input,
        toc_page=args.toc_page,
        output_dir=args.output_dir,
        prefix=args.prefix,
        level=args.level,
        no_ocr=args.no_ocr,
        dry_run=args.dry_run,
        chapters_only=args.chapters_only,
        verbose=args.verbose,
        ocr_embed=args.ocr_embed,
        ocr_convert=args.ocr_convert,
        llm=client,
    )
    
    if not result["success"]:
        sys.exit(1)
    
    # Print a clean summary for CLI users
    print("\n--- Summary ---")
    print(f"Source:     {result['source']}")
    print(f"Chapters:   {len(result['toc'])}")
    print(f"Output dir: {result['output_dir']}")
    if result['dry_run']:
        print("Mode:       DRY RUN (no files written)")
    print("Files:")
    for f in result["files"]:
        if not f["created"]:
            status = "dry-run"
        elif f.get("ocr_embedded"):
            status = "✓ OCR"
        else:
            status = "✓"
        print(f"  [{status}] {f['filename']} ({f['page_count']} pages)")
    print("---------------")


if __name__ == "__main__":
    main()

