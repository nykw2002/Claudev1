import pdfplumber
from typing import List, Dict
from pathlib import Path


class PDFProcessor:
    """Service for extracting text from PDF files"""

    def extract_text_from_pdf(self, file_path: str) -> Dict[str, any]:
        """
        Extract text from a single PDF file

        Args:
            file_path: Path to the PDF file

        Returns:
            dict: Contains full_text, pages (list of page texts), and metadata
        """
        try:
            pdf_path = Path(file_path)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {file_path}")

            pages_text = []
            full_text = ""

            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text() or ""
                    pages_text.append({
                        "page_number": page_num,
                        "text": page_text
                    })
                    full_text += f"\n--- Page {page_num} ---\n{page_text}\n"

            return {
                "file_name": pdf_path.name,
                "file_path": file_path,
                "total_pages": total_pages,
                "full_text": full_text.strip(),
                "pages": pages_text
            }

        except Exception as e:
            raise Exception(f"Error processing PDF {file_path}: {str(e)}")

    def extract_text_from_multiple_pdfs(self, file_paths: List[str]) -> List[Dict]:
        """
        Extract text from multiple PDF files

        Args:
            file_paths: List of paths to PDF files

        Returns:
            List[dict]: List of extraction results for each PDF
        """
        results = []
        for file_path in file_paths:
            result = self.extract_text_from_pdf(file_path)
            results.append(result)
        return results

    def search_text_in_pages(self, pages: List[Dict], search_term: str) -> List[Dict]:
        """
        Search for a term across pages and return matching sections

        Args:
            pages: List of page dictionaries with page_number and text
            search_term: Term to search for

        Returns:
            List[dict]: Matching sections with page number and context
        """
        matches = []
        for page in pages:
            text = page["text"]
            if search_term.lower() in text.lower():
                # Find context around the search term
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if search_term.lower() in line.lower():
                        # Get surrounding context (2 lines before and after)
                        start_idx = max(0, i - 2)
                        end_idx = min(len(lines), i + 3)
                        context = '\n'.join(lines[start_idx:end_idx])

                        matches.append({
                            "page_number": page["page_number"],
                            "text_snippet": context,
                            "matched_line": line.strip()
                        })

        return matches


# Singleton instance
pdf_processor = PDFProcessor()
