import fitz  # PyMuPDF
import io

def parse_pdf(file_bytes: bytes) -> str:
    """Extracts raw text from a PDF."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        
        extracted_text = "\n".join(text_parts).strip()
        if not extracted_text:
            raise ValueError("Scanned PDF or no extractable text found.")
            
        return extracted_text
    except Exception as e:
        raise ValueError(f"PDF Parsing Failed: {str(e)}")
