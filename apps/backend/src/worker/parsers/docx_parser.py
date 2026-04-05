import docx
import io

def parse_docx(file_bytes: bytes) -> str:
    """Extracts raw text from a DOCX."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text_parts = []
        for para in doc.paragraphs:
            text_parts.append(para.text)
            
        extracted_text = "\n".join(text_parts).strip()
        if not extracted_text:
            raise ValueError("Empty DOCX or no extractable text found.")
            
        return extracted_text
    except Exception as e:
        raise ValueError(f"DOCX Parsing Failed: {str(e)}")
