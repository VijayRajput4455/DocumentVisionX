from src.documents.llm_extractor_utils import is_valid_name, only_digits


def _is_valid_ifsc(value):
    if not value:
        return False
    ifsc = value.replace(" ", "").upper().strip()
    if len(ifsc) != 11:
        return False
    if not ifsc[:4].isalpha():
        return False
    if ifsc[4] != "0":
        return False
    if not ifsc[5:].isalnum():
        return False
    return True


def _normalize_bank_name(value, bank_names):
    candidate = " ".join(value.upper().split())
    for bank in bank_names:
        if bank == candidate:
            return bank
    return "NA"


def apply_bank_validation(data, bank_names):
    subtype = str(data["document_subtype"]).strip().lower()
    if subtype not in {"passbook", "cancelled_cheque"}:
        data["document_subtype"] = "NA"
    else:
        data["document_subtype"] = subtype

    if not is_valid_name(data["account_holder_name"], max_len=120):
        data["account_holder_name"] = "NA"

    account_number = only_digits(str(data["account_number"]))
    if 9 <= len(account_number) <= 18:
        data["account_number"] = account_number
    else:
        data["account_number"] = "NA"

    ifsc = str(data["ifsc"]).replace(" ", "").upper().strip()
    if _is_valid_ifsc(ifsc):
        data["ifsc"] = ifsc
    else:
        data["ifsc"] = "NA"

    data["bank_name"] = _normalize_bank_name(str(data["bank_name"]), bank_names)

    if data["document_subtype"] == "NA" and "CANCEL" in data["raw_text"]:
        data["document_subtype"] = "cancelled_cheque"
    elif data["document_subtype"] == "NA":
        data["document_subtype"] = "passbook"

    return data
