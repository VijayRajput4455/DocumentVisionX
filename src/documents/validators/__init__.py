from src.documents.validators.aadhaar import apply_aadhaar_validation
from src.documents.validators.bank import apply_bank_validation
from src.documents.validators.pan import apply_pan_validation
from src.documents.validators.voter import apply_voter_validation

__all__ = [
    "apply_aadhaar_validation",
    "apply_pan_validation",
    "apply_voter_validation",
    "apply_bank_validation",
]
