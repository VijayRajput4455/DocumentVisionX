from src.documents.llm_extractor_utils import (
    extract_year_from_dob,
    is_valid_address,
    is_valid_dob,
    is_valid_name,
)


def apply_aadhaar_validation(data):
    if not is_valid_name(data["USER_NAME"], max_len=80):
        data["USER_NAME"] = "NA"

    if not is_valid_name(data["FATHER_NAME"], max_len=80):
        data["FATHER_NAME"] = "NA"

    aadhaar = data["AADHAR_NUMBER"]
    if not (aadhaar.isdigit() and len(aadhaar) == 12):
        data["AADHAR_NUMBER"] = "NA"

    dob = data["DATE_OF_BIRTH"]
    if is_valid_dob(dob):
        year = extract_year_from_dob(dob)
        data["YEAR_OF_BIRTH"] = year if year else "NA"
    else:
        data["DATE_OF_BIRTH"] = "NA"
        data["YEAR_OF_BIRTH"] = "NA"

    gender = data["GENDER"]
    if gender not in {"MALE", "FEMALE", "OTHER"}:
        data["GENDER"] = "NA"

    mobile = data["MOBILE_NUMBER"]
    if not (mobile.isdigit() and len(mobile) == 10 and mobile[0] in "6789"):
        data["MOBILE_NUMBER"] = "NA"

    if not is_valid_address(data["ADDRESS"]):
        data["ADDRESS"] = "NA"

    return data
