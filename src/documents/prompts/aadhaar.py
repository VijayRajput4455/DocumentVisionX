def build_aadhaar_prompt(raw_text: str) -> str:
    return f"""
You are an Aadhaar information extraction system.

Extract ONLY valid Aadhaar details from the OCR text.

IGNORE:
- Hindi/English paragraphs
- Instructions
- Legal text like "Aadhaar is proof of identity"

EXTRACT:
- Name (prefer English if available)
- Father/Spouse Name
- Date of Birth (DOB)
- Gender
- Aadhaar Number (12 digits only, remove spaces)
- Mobile Number (if present)
- Address (if present)

STRICT RULES:
- Do NOT hallucinate
- Do NOT guess
- If not found, return empty string

Return ONLY JSON (no explanation):

{{
  "name": "",
  "father_name": "",
  "dob": "",
  "gender": "",
  "aadhaar_number": "",
  "mobile_number": "",
  "address": ""
}}

OCR TEXT:
{raw_text}
"""
