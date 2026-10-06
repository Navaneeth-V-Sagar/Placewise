import io
import re
import fitz  # PyMuPDF
from typing import Union, BinaryIO


class ResumeParserError(Exception):
    """Base exception for resume parsing errors"""
    pass


class InvalidPDFError(ResumeParserError):
    """Raised when the uploaded file is not a valid PDF or is corrupted"""
    pass


class EmptyResumeError(ResumeParserError):
    """Raised when the PDF contains no extractable text"""
    pass


class ResumeParser:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans extracted text by normalizing whitespace, removing redundant blank lines,
        and stripping control characters.
        """
        if not text:
            return ""
        
        # Replace non-breaking spaces and tabs
        text = text.replace('\xa0', ' ').replace('\t', ' ')
        
        # Split into lines and strip each line
        lines = [re.sub(r'[ ]+', ' ', line).strip() for line in text.splitlines()]
        
        # Join lines and collapse multiple consecutive blank lines
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()

    @classmethod
    def extract_text_from_bytes(cls, pdf_bytes: bytes) -> str:
        """
        Extracts clean text from PDF byte content using PyMuPDF.
        """
        if not pdf_bytes or len(pdf_bytes) == 0:
            raise EmptyResumeError("PDF file is empty (0 bytes).")

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise InvalidPDFError(f"Failed to open PDF file. Corrupted or invalid format: {str(e)}") from e

        try:
            if doc.page_count == 0:
                raise EmptyResumeError("PDF contains 0 pages.")

            extracted_pages = []
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                page_text = page.get_text("text")
                if page_text:
                    extracted_pages.append(page_text)

            full_text = "\n\n".join(extracted_pages)
            cleaned = cls.clean_text(full_text)

            if not cleaned or len(cleaned.strip()) < 10:
                raise EmptyResumeError("No readable text found in PDF. Scanned images without OCR are not supported.")

            return cleaned
        finally:
            doc.close()

    @classmethod
    def extract_text_from_file(cls, file_path: str) -> str:
        """
        Extracts clean text from a PDF file on disk.
        """
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            return cls.extract_text_from_bytes(content)
        except (InvalidPDFError, EmptyResumeError):
            raise
        except Exception as e:
            raise InvalidPDFError(f"Could not read PDF from path {file_path}: {str(e)}") from e


resume_parser = ResumeParser()
