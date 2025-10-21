"""
Unified PDF Text Extractor
Automatically detects scanned PDFs and uses appropriate extraction method
"""
import pdfplumber
from typing import Dict, List
from .ocr_processor import is_pdf_scanned, process_scanned_pdf


def extract_text_from_pdf(pdf_path: str) -> Dict:
    """
    Extract text from PDF using best method (pdfplumber or OCR)
    Automatically detects if PDF is scanned

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dict with structure:
        {
            'file_path': str,
            'file_name': str,
            'total_pages': int,
            'pages': [{'page_num': int, 'text': str}, ...],
            'full_text': str,
            'extraction_method': str  # 'pdfplumber' or 'ocr'
        }
    """
    # Check if PDF is scanned
    is_scanned = is_pdf_scanned(pdf_path)

    if is_scanned:
        print(f"Detected scanned PDF: {pdf_path}, using OCR extraction")
        result = process_scanned_pdf(pdf_path)
        result['extraction_method'] = 'ocr'
        return result
    else:
        print(f"Detected regular PDF: {pdf_path}, using pdfplumber extraction")
        return extract_with_pdfplumber(pdf_path)


def extract_with_pdfplumber(pdf_path: str) -> Dict:
    """
    Extract text from regular PDF using pdfplumber

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dict with extraction results
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            all_text = []

            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages.append({
                    'page_num': i + 1,
                    'text': text
                })
                all_text.append(text)

            # Get filename from path
            file_name = pdf_path.split('\\')[-1].split('/')[-1]

            return {
                'file_path': pdf_path,
                'file_name': file_name,
                'total_pages': len(pdf.pages),
                'pages': pages,
                'full_text': '\n'.join(all_text),
                'extraction_method': 'pdfplumber'
            }

    except Exception as e:
        raise Exception(f"Error processing PDF {pdf_path}: {str(e)}")


def extract_text_from_multiple_pdfs(pdf_paths: List[str]) -> List[Dict]:
    """
    Extract text from multiple PDF files

    Args:
        pdf_paths: List of paths to PDF files

    Returns:
        List of dicts with extraction results for each PDF
    """
    results = []

    for pdf_path in pdf_paths:
        try:
            result = extract_text_from_pdf(pdf_path)
            results.append(result)
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except Exception as e:
            raise Exception(f"Error processing PDF {pdf_path}: {str(e)}")

    return results
