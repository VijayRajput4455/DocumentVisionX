from src.documents.prompts.aadhaar import build_aadhaar_prompt
from src.documents.prompts.bank import build_bank_prompt
from src.documents.prompts.pan import build_pan_prompt
from src.documents.prompts.voter import build_voter_prompt

__all__ = [
    "build_aadhaar_prompt",
    "build_pan_prompt",
    "build_voter_prompt",
    "build_bank_prompt",
]
