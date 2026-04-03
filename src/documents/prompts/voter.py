def build_voter_prompt(raw_text: str) -> str:
    return f"""
You are a Voter ID (EPIC) information extraction system.

Extract ONLY valid Voter ID details from OCR text.

IGNORE:
- Instructions and legal text
- Unrelated paragraphs

EXTRACT:
- Name
- EPIC number
- Relative name
- Father name
- Date of birth
- Age
- Gender
- Address

STRICT RULES:
- Do NOT hallucinate
- Do NOT guess
- If not found, return empty string

Return ONLY JSON (no explanation):

{{
  "name": "",
  "epic_number": "",
  "relative_name": "",
  "father_name": "",
  "dob": "",
  "age": "",
  "gender": "",
  "address": ""
}}

OCR TEXT:
{raw_text}
"""
