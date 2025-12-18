import re
import cv2
import numpy as np

from src.ocr.paddle_ocr_singleton import OCRSingleton
from src.logger import get_logger
logger = get_logger(__name__)


class AadharExtractor:
    """
    Aadhaar OCR extractor using PaddleOCR.
    Heavy OCR model is initialized once per instance.
    """

    def __init__(self):
        logger.info("Initializing AadharExtractor")
        self.ocr = self.ocr = OCRSingleton.get_instance()

        # Image and extracted data placeholders
        self.image = None
        self.data = None

    # ------------------------------------------------------------------------
    def _get_rotated_images(self):
        """
        Returns list of image rotations to handle orientation issues.
        """
        return [
            self.image,
            cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE),
            cv2.rotate(self.image, cv2.ROTATE_180),
            cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE),
        ]

    # ------------------------------------------------------------------------
    def _perform_ocr(self):
        """
        Performs OCR on original and rotated images.
        Returns cleaned list of detected text lines.
        """
        logger.info("Starting OCR on image with rotations")
        text = []

        for img in self._get_rotated_images():
            result = self.ocr.ocr(img, cls=False, det=True)
            text_lines = [word[1][0] for line in result for word in line]
            text.extend(text_lines)

        logger.info("OCR completed successfully")
        return [t.strip() for t in text if len(t.strip()) > 0]

    # ------------------------------------------------------------------------
    def _extract_aadhar_number(self, lines):
        """
        Extracts Aadhaar number (12 digits).
        """
        pattern = re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')

        for line in lines:
            m = pattern.search(line)
            if m:
                self.data["AADHAR_NUMBER"] = m.group()
                logger.info("Aadhaar number detected")
                return

    # ------------------------------------------------------------------------
    def _extract_father_name(self, lines):
        """
        Extracts Father / Spouse name using relationship keywords.
        """
        pattern = re.compile(r'(S/O|F/O|D/O|W/O)\s*[:\-]?\s*([A-Za-z ]{3,})', re.IGNORECASE)

        for line in lines:
            m = pattern.search(line)
            if m:
                self.data["FATHER_NAME"] = m.group(2).strip()
                logger.info("Father/Spouse name detected")
                return

    # ------------------------------------------------------------------------
    def _extract_dob(self, lines):
        """
        Extracts Date of Birth or Year of Birth.
        """
        dob_patterns = [
            r"\b\d{2}-\d{2}-\d{4}\b",
            r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        ]

        year_pattern = r"\b(19|20)\d{2}\b"

        # Full DOB
        for line in lines:
            for pattern in dob_patterns:
                m = re.search(pattern, line)
                if m:
                    dob = m.group()
                    self.data["DATE_OF_BIRTH"] = dob
                    self.data["YEAR_OF_BIRTH"] = re.search(r"\d{4}", dob).group()
                    logger.info("Date of Birth detected")
                    return

        # Year only
        for line in lines:
            m = re.search(year_pattern, line)
            if m:
                self.data["YEAR_OF_BIRTH"] = m.group()
                logger.info("Year of Birth detected")
                return

    # ------------------------------------------------------------------------
    def _extract_gender(self, lines):
        """
        Extracts gender (MALE / FEMALE).
        """
        pattern = re.compile(r"\b(MALE|FEMALE)\b", re.IGNORECASE)

        for line in lines:
            m = pattern.search(line)
            if m:
                self.data["GENDER"] = m.group().upper()
                logger.info("Gender detected")
                return

    # ------------------------------------------------------------------------
    def _extract_mobile(self, lines):
        """
        Extracts Indian mobile number.
        """
        pattern = re.compile(r"\b(\+91[\-\s]?)?[6-9]\d{9}\b")

        for line in lines:
            m = pattern.search(line)
            if m:
                self.data["MOBILE_NUMBER"] = m.group().replace(" ", "")
                logger.info("Mobile number detected")
                return

    # ------------------------------------------------------------------------
    def _extract_user_name(self, lines):
        """
        Extracts user name using UIDAI header logic or name pattern matching.
        """

        uidai_variants = [
            "UNIQUEIDENTIFICATIONAUTHORITYOFINDIA",
            "UNIQUEIDENTIFICATIONAUTHORITY",
            "UNIQUEIDENTIFICATION",
            "UNIQUE IDENTIFICATION AUTHORITY OF INDIA",
            "GOVERNMENT OF INDIA"
        ]

        upper_lines = [l.upper().replace(" ", "") for l in lines]

        # UIDAI header-based extraction
        for idx, txt in enumerate(upper_lines):
            if any(uid in txt for uid in uidai_variants):
                if idx + 1 < len(lines):
                    candidate = lines[idx + 1].strip()
                    if 2 <= len(candidate.split()) <= 4 and not re.search(r"\d", candidate):
                        self.data["USER_NAME"] = candidate
                        logger.info("User name detected (UIDAI logic)")
                        return

        # Pattern-based extraction
        for line in lines:
            if re.search(r"\d", line):
                continue

            if any(k in line.upper() for k in ["FEMALE", "MALE", "ADDRESS", "DOB", "YEAR", "AADHAAR", "S/O", "F/O", "D/O"]):
                continue

            if re.match(r"^[A-Z][a-zA-Z]{2,}(?:\s[A-Z][a-zA-Z]{2,}){0,3}$", line):
                self.data["USER_NAME"] = line
                logger.info("User name detected (pattern match)")
                return

    # ------------------------------------------------------------------------
    def _extract_address(self, ocr_text_lines):
        """
        Extracts multi-line address until PIN code.
        """
        address_keywords = ["ADDRESS", "S/O", "W/O", "C/O", "D/O"]
        pincode_pattern = re.compile(r"\b\d{6}\b")

        address_lines = []
        capturing = False

        for line in ocr_text_lines:
            if any(k in line.upper() for k in address_keywords):
                capturing = True

            if capturing:
                address_lines.append(line)
                if pincode_pattern.search(line):
                    break

        if address_lines:
            self.data["ADDRESS"] = re.sub(r"\s+", " ", " ".join(address_lines)).strip()
            logger.info("Address detected")

    # ------------------------------------------------------------------------
    def extract_details(self, image_input):
        """
        Main public method.
        Accepts image path or numpy array.
        """
        logger.info("Starting Aadhaar extraction")

        # Load image
        if isinstance(image_input, np.ndarray):
            self.image = image_input
        else:
            self.image = cv2.imread(image_input)

        if self.image is None:
            logger.error("Invalid image input")
            raise ValueError("Invalid image input")

        # Initialize output structure
        self.data = {
            'USER_NAME': "NA",
            'AADHAR_NUMBER': "NA",
            'FATHER_NAME': "NA",
            'DATE_OF_BIRTH': "NA",
            'YEAR_OF_BIRTH': "NA",
            'GENDER': "NA",
            'MOBILE_NUMBER': "NA",
            'ADDRESS': "NA"
        }

        lines = self._perform_ocr()
        logger.debug(f"OCR Output: {lines}")

        self._extract_aadhar_number(lines)
        self._extract_father_name(lines)
        self._extract_dob(lines)
        self._extract_gender(lines)
        self._extract_mobile(lines)
        self._extract_address(lines)
        self._extract_user_name(lines)

        logger.info("Aadhaar extraction completed")
        return self.data
