"""
AI Service Tools
Utilities for document processing, OCR, and text extraction
"""

from .pdf_text_extractor import extract_text_from_pdf, extract_text_from_multiple_pdfs
from .ocr_processor import process_scanned_pdf, is_pdf_scanned

__all__ = [
    'extract_text_from_pdf',
    'extract_text_from_multiple_pdfs',
    'process_scanned_pdf',
    'is_pdf_scanned',
]
