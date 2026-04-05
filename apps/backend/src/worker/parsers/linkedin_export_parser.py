import zipfile
import io
import csv

def parse_linkedin_export(file_bytes: bytes) -> str:
    """Extracts raw text from a LinkedIn data export ZIP."""
    text_parts = []
    
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            # We specifically look for useful files like Profile.csv, Positions.csv
            # But for a robust MVP, let's just collect all CSV content safely.
            for file_info in z.infolist():
                if file_info.filename.endswith('.csv') and not file_info.filename.startswith('__MACOSX'):
                    with z.open(file_info) as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        
                        # Process CSV to text
                        csv_reader = csv.reader(io.StringIO(content))
                        rows = []
                        for row in csv_reader:
                            if any(row):  # Skip empty rows
                                rows.append(" | ".join([cell.strip() for cell in row if cell.strip()]))
                                
                        if rows:
                            text_parts.append(f"--- {file_info.filename} ---")
                            text_parts.extend(rows)
                            text_parts.append("\n")
                            
        extracted_text = "\n".join(text_parts).strip()
        if not extracted_text:
            raise ValueError("Archive present but no supported CSV files or data found inside.")
            
        return extracted_text
    except zipfile.BadZipFile:
        raise ValueError("Corrupted or invalid ZIP file.")
    except Exception as e:
        raise ValueError(f"LinkedIn Export Parsing Failed: {str(e)}")
