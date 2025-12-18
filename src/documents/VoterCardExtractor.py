import re
import cv2
import numpy as np

from src.ocr.paddle_ocr_singleton import OCRSingleton
from src.logger import get_logger

logger = get_logger(__name__)


class VoterCardExtractor:
    """
    Voter ID (EPIC) OCR extractor using PaddleOCR.
    OCR model is loaded once using singleton.
    """

    def __init__(self):
        logger.info("Initializing VoterCardExtractor")
        self.ocr = OCRSingleton.get_instance()
        self.image = None
        self.data = None

    # ------------------------------------------------------------------
    def _get_rotated_images(self):
        return [
            self.image,
            cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE),
            cv2.rotate(self.image, cv2.ROTATE_180),
            cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE),
        ]

    # ------------------------------------------------------------------
    def _perform_ocr(self):
        logger.info("Performing OCR on voter card")
        text = []

        for img in self._get_rotated_images():
            result = self.ocr.ocr(img, det=True, cls=False)
            lines = [word[1][0] for line in result for word in line]
            text.extend(lines)

        return [t.strip() for t in text if t.strip()]

    # ------------------------------------------------------------------
    def _extract_epic_number(self, lines):
        """
        EPIC number format: ABC1234567
        """
        pattern = re.compile(r"\b[A-Z]{3}\d{7}\b")

        for line in lines:
            m = pattern.search(line.replace(" ", "").upper())
            if m:
                self.data["EPIC_NUMBER"] = m.group()
                logger.info("EPIC number detected")
                return

    # ------------------------------------------------------------------
    def _extract_name(self, lines):
        ignore_keywords = [
            "ELECTION", "COMMISSION", "INDIA", "IDENTITY",
            "CARD", "EPIC", "DOB", "AGE", "SEX", "GENDER"
        ]

        for line in lines:
            if any(k in line.upper() for k in ignore_keywords):
                continue
            if re.search(r"\d", line):
                continue

            if re.match(r"^[A-Z][a-zA-Z ]{3,}$", line):
                self.data["NAME"] = line.strip()
                logger.info("Voter name detected")
                return

    # ------------------------------------------------------------------
    def _extract_father_or_husband(self, lines):
        pattern = re.compile(
            r"(FATHER|HUSBAND|S/O|W/O)\s*[:\-]?\s*([A-Za-z ]{3,})",
            re.IGNORECASE
        )

        for line in lines:
            m = pattern.search(line)
            if m:
                self.data["RELATIVE_NAME"] = m.group(2).strip()
                logger.info("Father/Husband name detected")
                return

    # ------------------------------------------------------------------
    def _extract_dob_or_age(self, lines):
        dob_pattern = re.compile(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b")
        age_pattern = re.compile(r"\bAGE\s*[:\-]?\s*(\d{1,3})\b", re.IGNORECASE)

        for line in lines:
            dob = dob_pattern.search(line)
            if dob:
                self.data["DATE_OF_BIRTH"] = dob.group()
                logger.info("DOB detected")
                return

        for line in lines:
            age = age_pattern.search(line)
            if age:
                self.data["AGE"] = age.group(1)
                logger.info("Age detected")
                return

    # ------------------------------------------------------------------
    def _extract_gender(self, lines):
        pattern = re.compile(r"\b(MALE|FEMALE|OTHER)\b", re.IGNORECASE)

        for line in lines:
            m = pattern.search(line)
            if m:
                self.data["GENDER"] = m.group().upper()
                logger.info("Gender detected")
                return

    # ------------------------------------------------------------------
    def _extract_address(self, lines):
        pincode_pattern = re.compile(r"\b\d{6}\b")
        address_lines = []
        capturing = False

        for line in lines:
            if "ADDRESS" in line.upper():
                capturing = True

            if capturing:
                address_lines.append(line)
                if pincode_pattern.search(line):
                    break

        if address_lines:
            self.data["ADDRESS"] = " ".join(address_lines)
            logger.info("Address detected")

    # -----------------------------------------------------------
    def _extract_name_and_father(self, lines):
        """
        Extract Name and Father's Name using:
        1. Father label detection (primary)
        2. DOB position-based fallback (secondary)
        """
        logger.info("Extracting Name and Father's Name")

        cleaned = [x.strip() for x in lines if len(x.strip()) > 2]

        father_variants = [
            r"FATHER", r"FATHER'S", r"FATHERS", r"FATHER NAME",
            r"FATHE", r"FATHE R", r"FATHE$", r"FATHEC", r"FALHER",
            r"FOTHER", r"FATNER", r"FATIIER", r"FATHER N",
            r"FAT", r"FATHER5", r"FATHER\$", r"FATHER'SNAME",
            r"FATHER’S"
        ]

        father_pattern = re.compile("|".join(father_variants), re.IGNORECASE)

        father_index = -1
        for i, line in enumerate(cleaned):
            if father_pattern.search(line.upper()):
                father_index = i
                break

        # Primary approach using Father label
        if father_index != -1:
            if father_index - 1 >= 0:
                self.data["NAME"] = cleaned[father_index - 1]

            if father_index + 1 < len(cleaned):
                self.data["FATHER_NAME"] = cleaned[father_index + 1]

            logger.info("Name and Father name extracted using label-based method")
            return

        # Fallback approach using DOB position
        dob_index = -1
        for i, line in enumerate(cleaned):
            if re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", line):
                dob_index = i
                break

        if dob_index != -1:
            if dob_index - 2 >= 0:
                self.data["NAME"] = cleaned[dob_index - 2]

            if dob_index - 1 >= 0:
                self.data["FATHER_NAME"] = cleaned[dob_index - 1]

            logger.info("Name and Father name extracted using DOB fallback method")

    # ------------------------------------------------------------------
    def extract_details(self, image_input):
        logger.info("Starting Voter card extraction")

        if isinstance(image_input, np.ndarray):
            self.image = image_input
        else:
            self.image = cv2.imread(image_input)

        if self.image is None:
            raise ValueError("Invalid image input")

        self.data = {
            "NAME": "NA",
            "EPIC_NUMBER": "NA",
            "RELATIVE_NAME": "NA",
            "DATE_OF_BIRTH": "NA",
            "AGE": "NA",
            "GENDER": "NA",
            "ADDRESS": "NA",
            "FATHER_NAME": "NA"
        }

        lines = self._perform_ocr()
        print(lines,"kkkkkkkkk")
        logger.debug(f"OCR Lines: {lines}")

        self._extract_epic_number(lines)
        self._extract_name(lines)
        self._extract_father_or_husband(lines)
        self._extract_dob_or_age(lines)
        self._extract_gender(lines)
        self._extract_address(lines)
        self._extract_name_and_father(lines)

        logger.info("Voter card extraction completed")
        return self.data