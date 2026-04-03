def build_bank_prompt(raw_text: str) -> str:
    return f"""
You are a bank document information extraction system.

Extract ONLY valid details from OCR text of a bank passbook or cancelled cheque.

EXTRACT:
- Document subtype (passbook or cancelled_cheque)
- Account holder name
- Account number
- IFSC code
- Bank name

STRICT RULES:
- Do NOT hallucinate
- Do NOT guess
- If not found, return empty string

Return ONLY JSON (no explanation):

{{
  "document_subtype": "",
  "account_holder_name": "",
  "account_number": "",
  "ifsc": "",
  "bank_name": ""
}}

OCR TEXT:
{raw_text}
"""
