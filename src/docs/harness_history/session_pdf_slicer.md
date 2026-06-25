# SESSION.md

# SESSION — Build Chapter Slicer

## Project
Multi-angle learning engine. Step 1: slice books into chapters so downstream stages can transform them into podcast, xianxia fiction, and animation formats.

## Active Task
Build a Python script that takes a PDF path and the page number where the table of contents begins. It extracts the TOC text, parses chapter titles and start pages, then slices the PDF into one PDF per chapter.

## Stack
Python 3.11+. Use `pypdf` for PDF manipulation and text extraction. No other dependencies.

## Rules
- One Python file. No classes, no tests, no CLI framework.
- Input: a PDF file path and `toc_start_page` (1-indexed integer). Optionally `toc_end_page`; if omitted, scan `toc_start_page` through `toc_start_page + 2`.
- Extract text from the specified TOC page range. Parse lines with regex to find chapter titles and their trailing page numbers. Handle common leader dots and whitespace.
- Output: individual PDFs written to an `output/` directory, named `01_Chapter_Title.pdf`, `02_Chapter_Title.pdf`, etc.
- The last chapter runs to the end of the source PDF.
- Page numbers parsed from the TOC are 1-indexed and map directly to PDF pages.
- If a parsed chapter start page is invalid (beyond PDF length), raise ValueError immediately with the chapter name and page number.
- Sanitize filenames: alphanumeric, underscores, no spaces. Truncate titles to 50 chars for filename safety.
- Print the parsed TOC to stdout before slicing so the user can verify it.

## Never Do
- Do not require the user to type or paste the table of contents manually.
- Do not create `requirements.txt`, `setup.py`, or virtual environment instructions.
- Do not write docstrings beyond a single one-line description at the top of the file.
- Do not handle text extraction, OCR, or content analysis outside the TOC pages; this is purely mechanical page-range slicing.
- Do not create sub-packages or `__init__.py` files.

## Done When
A single `.py` file exists that, given a PDF path and TOC start page, correctly extracts the TOC, prints it for verification, and slices the PDF into chapter files.