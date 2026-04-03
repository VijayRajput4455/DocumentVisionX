def build_pan_prompt(raw_text: str) -> str:
    return f"""
You are a PAN card information extraction system.

Extract ONLY valid PAN card details from OCR text.

IGNORE:
- Instructions
- Watermarks
- Unrelated paragraph text

EXTRACT:
- PAN number
- Name
- Father name
- Date of birth

STRICT RULES:
- Do NOT hallucinate
- Do NOT guess
- If not found, return empty string

Return ONLY JSON (no explanation):

{{
  "pan_number": "",
  "name": "",
  "father_name": "",
  "dob": ""
}}

OCR TEXT:
{raw_text}
"""
