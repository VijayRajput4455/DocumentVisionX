from src.documents.llm_extractor_utils import is_valid_dob, is_valid_name


def _is_valid_pan(value):
    if not value:
        return False
    pan = value.replace(" ", "").upper().strip()
    if len(pan) != 10:
        return False
    if not pan[:5].isalpha():
        return False
    if not pan[5:9].isdigit():
        return False
    if not pan[9].isalpha():
        return False
    return True


def apply_pan_validation(data):
    if not _is_valid_pan(data["PAN_NUMBER"]):
        data["PAN_NUMBER"] = "NA"
    else:
        data["PAN_NUMBER"] = data["PAN_NUMBER"].replace(" ", "").upper()

    if not is_valid_name(data["NAME"], max_len=80):
        data["NAME"] = "NA"

    if not is_valid_name(data["FATHER_NAME"], max_len=80):
        data["FATHER_NAME"] = "NA"

    if not is_valid_dob(data["DATE_OF_BIRTH"]):
        data["DATE_OF_BIRTH"] = "NA"

    return data
