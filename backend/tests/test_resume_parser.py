import pytest
import fitz
from app.services.resume_parser import (
    resume_parser,
    InvalidPDFError,
    EmptyResumeError,
    ResumeParser
)


def create_test_pdf_bytes(text: str) -> bytes:
    """Helper to create a minimal in-memory PDF with text using fitz."""
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((50, 72), text, fontsize=11)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_extract_text_valid_pdf():
    sample_content = (
        "John Doe\n"
        "Software Engineer\n\n"
        "Skills:\n"
        "- Python, FastAPI, Docker, PostgreSQL, React\n\n"
        "Projects:\n"
        "- E-Commerce API: Built high throughput microservices with FastAPI and Redis."
    )
    pdf_bytes = create_test_pdf_bytes(sample_content)
    extracted = resume_parser.extract_text_from_bytes(pdf_bytes)
    
    assert "John Doe" in extracted
    assert "FastAPI" in extracted
    assert "Docker" in extracted
    assert "E-Commerce API" in extracted


def test_extract_text_empty_pdf():
    # PDF with no text on page
    pdf_bytes = create_test_pdf_bytes("")
    with pytest.raises(EmptyResumeError):
        resume_parser.extract_text_from_bytes(pdf_bytes)


def test_extract_text_corrupt_bytes():
    corrupt_bytes = b"NOT_A_REAL_PDF_DATA_HERE"
    with pytest.raises(InvalidPDFError):
        resume_parser.extract_text_from_bytes(corrupt_bytes)


def test_extract_text_zero_length_bytes():
    with pytest.raises(EmptyResumeError):
        resume_parser.extract_text_from_bytes(b"")


def test_clean_text_normalization():
    dirty = "  John   Doe   \xa0\xa0\n\n\n\n\nSoftware   Engineer  \t  Python  "
    cleaned = ResumeParser.clean_text(dirty)
    assert "\xa0" not in cleaned
    assert "\t" not in cleaned
    assert "  " not in cleaned
    assert "John Doe\n\nSoftware Engineer Python" == cleaned
