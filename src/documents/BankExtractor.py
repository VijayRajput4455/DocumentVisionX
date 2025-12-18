# src/documents/BankExtractor.py

import re
from paddleocr import PaddleOCR


class BankExtractor:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang="en")

        self.bank_names = [
            "STATE BANK OF INDIA",
            "HDFC BANK",
            "ICICI BANK",
            "AXIS BANK",
            "PUNJAB NATIONAL BANK",
            "BANK OF BARODA",
            "CANARA BANK",
            "UNION BANK OF INDIA",
            "INDIAN BANK",
            "YES BANK",
            "IDFC FIRST BANK"
        ]

    # -------------------------
    # OCR
    # -------------------------
    def run_ocr(self, image):
        result = self.ocr.ocr(image, cls=True)
        texts = []
        for line in result:
            for word in line:
                texts.append(word[1][0])
        return "\n".join(texts).upper()

    # -------------------------
    # Extractors
    # -------------------------
    def extract_account_number(self, text):
        match = re.search(r"\b\d{9,18}\b", text)
        return match.group() if match else None

    def extract_ifsc(self, text):
        match = re.search(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", text)
        return match.group() if match else None

    def extract_bank_name(self, text):
        for bank in self.bank_names:
            if bank in text:
                return bank
        return None

    def extract_name(self, text):
        lines = text.split("\n")
        for line in lines:
            if "NAME" in line and len(line.split()) >= 2:
                return (
                    line.replace("NAME", "")
                    .replace(":", "")
                    .strip()
                )
        return None

    def detect_subtype(self, text):
        if "CANCELLED" in text:
            return "cancelled_cheque"
        return "passbook"

    # -------------------------
    # Main
    # -------------------------
    def extract_details(self, image):
        ocr_text = self.run_ocr(image)

        return {
            "document_subtype": self.detect_subtype(ocr_text),
            "account_holder_name": self.extract_name(ocr_text),
            "account_number": self.extract_account_number(ocr_text),
            "ifsc": self.extract_ifsc(ocr_text),
            "bank_name": self.extract_bank_name(ocr_text),
            "raw_text": ocr_text
        }
