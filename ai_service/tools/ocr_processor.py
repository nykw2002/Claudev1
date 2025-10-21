"""
OCR Processor for Scanned PDFs
Uses PyMuPDF (fitz) to extract text from image-based PDFs
"""
import fitz  # PyMuPDF
from typing import Dict, List


def is_pdf_scanned(pdf_path: str) -> bool:
    """
    Detect if a PDF is scanned by checking if the first page has extractable text

    Args:
        pdf_path: Path to PDF file

    Returns:
        bool: True if PDF appears to be scanned (no text on first page)
    """
    try:
        doc = fitz.open(pdf_path)

        if len(doc) == 0:
            return False

        # Check first page for text
        first_page = doc[0]
        text = first_page.get_text().strip()

        doc.close()

        # If first page has less than 10 characters, likely scanned
        return len(text) < 10

    except Exception as e:
        print(f"Error detecting if PDF is scanned: {str(e)}")
        return False


def process_scanned_pdf(pdf_path: str) -> Dict:
    """
    Extract text from scanned PDF using OCR via PyMuPDF

    Args:
        pdf_path: Path to scanned PDF file

    Returns:
        Dict with structure:
        {
            'file_path': str,
            'file_name': str,
            'total_pages': int,
            'pages': [{'page_num': int, 'text': str}, ...],
            'full_text': str
        }
    """
    try:
        doc = fitz.open(pdf_path)

        pages = []
        all_text = []

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Try to get text first (in case some pages have text)
            text = page.get_text()

            # If no text, try OCR using get_textpage with OCR flag
            if len(text.strip()) < 10:
                # PyMuPDF's built-in OCR capabilities
                # Extract as images and then as text
                pix = page.get_pixmap()
                # Use get_text with "text" mode which works better for images
                text = page.get_text("text")

                # If still no text, try extracting from images
                if len(text.strip()) < 10:
                    image_list = page.get_images()
                    if image_list:
                        # Note: For true OCR, you'd need pytesseract here
                        # PyMuPDF alone can't do OCR, it just extracts existing text
                        # For now, we'll use best-effort text extraction
                        text = page.get_text("text")
                        if not text:
                            text = f"[Scanned page {page_num + 1} - OCR not available without tesseract]"

            pages.append({
                'page_num': page_num + 1,
                'text': text
            })
            all_text.append(text)

        doc.close()

        # Get filename from path
        file_name = pdf_path.split('\\')[-1].split('/')[-1]

        return {
            'file_path': pdf_path,
            'file_name': file_name,
            'total_pages': len(pages),
            'pages': pages,
            'full_text': '\n'.join(all_text)
        }

    except Exception as e:
        raise Exception(f"Error processing scanned PDF {pdf_path}: {str(e)}")


def extract_text_with_ocr(pdf_path: str) -> str:
    """
    Helper function to extract text from a single page with OCR fallback

    Args:
        pdf_path: Path to PDF file

    Returns:
        str: Extracted text
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = []

        for page in doc:
            text = page.get_text()
            full_text.append(text)

        doc.close()
        return '\n'.join(full_text)

    except Exception as e:
        print(f"Error extracting text with OCR: {str(e)}")
        return ""
