from src.documents.llm_extractor_utils import (
    is_valid_address,
    is_valid_dob,
    is_valid_name,
)


def _is_valid_epic(value):
    if not value:
        return False
    epic = value.replace(" ", "").upper().strip()
    if len(epic) != 10:
        return False
    if not epic[:3].isalpha():
        return False
    if not epic[3:].isdigit():
        return False
    return True


def apply_voter_validation(data):
    if not is_valid_name(data["NAME"]):
        data["NAME"] = "NA"

    if not _is_valid_epic(data["EPIC_NUMBER"]):
        data["EPIC_NUMBER"] = "NA"
    else:
        data["EPIC_NUMBER"] = data["EPIC_NUMBER"].replace(" ", "").upper()

    if not is_valid_name(data["RELATIVE_NAME"]):
        data["RELATIVE_NAME"] = "NA"

    if not is_valid_name(data["FATHER_NAME"]):
        data["FATHER_NAME"] = "NA"

    if not is_valid_dob(data["DATE_OF_BIRTH"]):
        data["DATE_OF_BIRTH"] = "NA"

    age_value = str(data["AGE"]).strip()
    if age_value.isdigit():
        age_num = int(age_value)
        data["AGE"] = age_value if 1 <= age_num <= 120 else "NA"
    else:
        data["AGE"] = "NA"

    if data["GENDER"] not in {"MALE", "FEMALE", "OTHER"}:
        data["GENDER"] = "NA"

    if not is_valid_address(data["ADDRESS"]):
        data["ADDRESS"] = "NA"

    if data["RELATIVE_NAME"] == "NA" and data["FATHER_NAME"] != "NA":
        data["RELATIVE_NAME"] = data["FATHER_NAME"]

    return data
