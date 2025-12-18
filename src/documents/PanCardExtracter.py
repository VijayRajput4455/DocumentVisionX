import re
import cv2
import numpy as np

from src.ocr.paddle_ocr_singleton import OCRSingleton
from src.logger import get_logger
logger = get_logger(__name__)


class PANExtractor:
    """
    PAN Card Information Extractor

    This class performs:
    - OCR using PaddleOCR
    - PAN number extraction
    - Name and Father's name extraction
    - Date of Birth extraction

    OCR model is loaded once and reused for performance.
    """

    def __init__(self):
        """
        Initialize OCR engine.
        Heavy OCR model is loaded only once.
        """
        logger.info("Initializing PanCardExtractor")

        self.ocr = OCRSingleton.get_instance()

        # Image placeholder (set during extract)
        self.image = None

        # Result dictionary (initialized per request)
        self.data = None

    # -----------------------------------------------------------
    def _get_all_rotations(self):
        """
        Generate all possible image rotations to improve OCR accuracy.
        """
        return [
            self.image,
            cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE),
            cv2.rotate(self.image, cv2.ROTATE_180),
            cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        ]

    # -----------------------------------------------------------
    def _perform_ocr(self):
        """
        Perform OCR on all rotated versions of the image
        and collect extracted text lines.
        """
        logger.info("Performing OCR on PAN image")

        lines = []
        for img in self._get_all_rotations():
            result = self.ocr.ocr(img, cls=False, det=True)
            for block in result:
                for word in block:
                    lines.append(word[1][0])

        logger.debug(f"OCR extracted {len(lines)} text lines")
        return lines

    # -----------------------------------------------------------
    def _extract_pan_number(self, lines):
        """
        Extract PAN number.

        PAN format:
        - 5 uppercase letters
        - 4 digits
        - 1 uppercase letter
        Example: ABCDE1234F
        """
        logger.info("Extracting PAN number")

        pattern = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", re.I)

        for line in lines:
            match = pattern.search(line.replace(" ", "").upper())
            if match:
                self.data["PAN_NUMBER"] = match.group().upper()
                logger.info(f"PAN number detected: {self.data['PAN_NUMBER']}")
                return

    # -----------------------------------------------------------
    def _extract_dob(self, lines):
        """
        Extract Date of Birth in formats:
        - DD/MM/YYYY
        - DD-MM-YYYY
        """
        logger.info("Extracting Date of Birth")

        pattern = re.compile(r"\b\d{2}[/-]\d{2}[/-]\d{4}\b")

        for line in lines:
            match = pattern.search(line)
            if match:
                self.data["DATE_OF_BIRTH"] = match.group()
                logger.info(f"DOB detected: {self.data['DATE_OF_BIRTH']}")
                return

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
            r"FAT", r"FATHER5", r"FATHER\$",
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

    # -----------------------------------------------------------
    def extract_details(self, image_input):
        """
        Main extraction method.

        Args:
            image_input: numpy array OR image file path

        Returns:
            dict: Extracted PAN details
        """
        logger.info("Starting PAN extraction process")

        # Load image
        if isinstance(image_input, np.ndarray):
            self.image = image_input
        else:
            self.image = cv2.imread(image_input)

        if self.image is None:
            logger.error("Invalid PAN image input")
            raise ValueError("Invalid PAN image input")

        # Initialize output structure
        self.data = {
            "PAN_NUMBER": "NA",
            "NAME": "NA",
            "FATHER_NAME": "NA",
            "DATE_OF_BIRTH": "NA"
        }

        # Perform OCR and extraction
        lines = self._perform_ocr()
        logger.debug(f"OCR Lines: {lines}")

        self._extract_pan_number(lines)
        self._extract_dob(lines)
        self._extract_name_and_father(lines)

        logger.info("PAN extraction completed successfully")
        return self.data
