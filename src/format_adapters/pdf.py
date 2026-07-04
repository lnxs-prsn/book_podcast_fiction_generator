from podcast_script_generator.llm.extract_pdf import extract_pdf
from engines.pdf_splitter import PDFSplitterEngine
from format_adapters.registry import register_adapters

register_adapters(".pdf", extract_pdf, PDFSplitterEngine)
