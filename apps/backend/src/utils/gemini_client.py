import json
import httpx
from src.utils.logger import log
from src.config import settings

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def generate_profile_json(extracted_text: str) -> dict:
    """
    Calls Gemini API to extract a structured dict matching the profile schema.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        log.error("Gemini API key is not configured.", extra={"phase": "semantic_extract", "status": "failed"})
        return {}

    url = f"{GEMINI_API_URL}?key={api_key}"
    headers = {
        'Content-Type': 'application/json'
    }
    
    prompt = f"""
You are an expert HR data parsing assistant. 
Extract the following information from the provided raw text (resume or linkedin export) and return ONLY a valid JSON object matching the exact schema below:

SCHEMA:
{{
  "identity": {{
    "name": "",
    "email": "",
    "phone": "",
    "location": ""
  }},
  "headline": "",
  "summary": "",
  "skills": [],
  "experience": [
    {{
      "title": "",
      "company": "",
      "location": "",
      "start_date": "",
      "end_date": "",
      "is_current": false,
      "bullets": []
    }}
  ],
  "education": [
      {{
          "institution": "",
          "degree": "",
          "startDate": "",
          "endDate": ""
      }}
  ],
  "projects": [],
  "certifications": [],
  "links": []
}}

Do not include markdown blocks like ```json ... ```, just output the raw JSON object.

Raw Data:
{extracted_text}
"""
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
        }
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                log.error("No candidates in Gemini response", extra={"phase": "semantic_extract", "response": data})
                return {}
            
            text_result = candidates[0]["content"]["parts"][0]["text"]
            # Clean possible markdown
            text_result = text_result.strip()
            if text_result.startswith("```json"):
                text_result = text_result[7:]
            if text_result.startswith("```"):
                text_result = text_result[3:]
            if text_result.endswith("```"):
                text_result = text_result[:-3]
                
            return json.loads(text_result.strip())
            
    except Exception as e:
        log.error(f"Gemini API exception", extra={"phase": "semantic_extract", "error": str(e)})
        return {}
