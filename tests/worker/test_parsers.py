import pytest
import io
import zipfile
import docx
from reportlab.pdfgen import canvas
from src.worker.parsers.pdf_parser import parse_pdf
from src.worker.parsers.docx_parser import parse_docx
from src.worker.parsers.linkedin_export_parser import parse_linkedin_export

def create_sample_pdf_bytes():
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 100, "Hello PyMuPDF")
    c.save()
    return buf.getvalue()

def create_sample_docx_bytes():
    doc = docx.Document()
    doc.add_paragraph("Hello python-docx")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

def create_sample_zip_bytes():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Profile.csv", "First Name,Last Name\nJohn,Doe\n")
    return buf.getvalue()

def test_pdf_parsing():
    content = parse_pdf(create_sample_pdf_bytes())
    assert "Hello PyMuPDF" in content

def test_docx_parsing():
    content = parse_docx(create_sample_docx_bytes())
    assert "Hello python-docx" in content

def test_zip_parsing():
    content = parse_linkedin_export(create_sample_zip_bytes())
    assert "John | Doe" in content
