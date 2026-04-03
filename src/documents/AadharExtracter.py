import cv2
import numpy as np

from src.config import (
    AADHAR_FAST_PATH_ROTATIONS,
    AADHAR_FULL_PATH_ROTATIONS,
    AADHAR_LLM_ENDPOINT,
    AADHAR_LLM_MODEL,
    AADHAR_LLM_TIMEOUT,
    OCR_BACKEND,
)
from src.documents.base_llm_extractor import BaseLLMExtractor
from src.documents.llm_extractor_utils import (
    call_llm_json,
    extract_year_from_dob,
    normalize_with_schema,
    only_digits,
)
from src.documents.prompts import build_aadhaar_prompt
from src.documents.schemas import AADHAR_FIELDS
from src.documents.validators import apply_aadhaar_validation
from src.logger import get_logger
logger = get_logger(__name__)


class AadharExtractor(BaseLLMExtractor):
    """
    Aadhaar OCR extractor using PaddleOCR.
    Heavy OCR model is initialized once per instance.
    """

    def __init__(self):
        logger.info("Initializing AadharExtractor")
        super().__init__(
            ocr_backend=OCR_BACKEND,
            llm_model=AADHAR_LLM_MODEL,
            llm_endpoint=AADHAR_LLM_ENDPOINT,
            llm_timeout=AADHAR_LLM_TIMEOUT,
            fast_path_rotations=AADHAR_FAST_PATH_ROTATIONS,
            full_path_rotations=AADHAR_FULL_PATH_ROTATIONS,
            logger=logger,
            extractor_name="AadharExtractor",
        )

    # ------------------------------------------------------------------------
    def _extract_details_with_llm(self, lines, data):
        """
        Uses LLM over OCR lines to extract structured Aadhaar fields.
        """
        raw_text = "\n".join(lines)
        prompt = build_aadhaar_prompt(raw_text)

        parsed = call_llm_json(
            model=self.llm_model,
            endpoint=self.llm_endpoint,
            prompt=prompt,
            timeout=self.llm_timeout,
            logger=logger,
            tag="Aadhaar extraction",
        )
        if not parsed:
            return

        parsed = normalize_with_schema(parsed, AADHAR_FIELDS)

        name = str(parsed.get("name", "")).strip()
        father_name = str(parsed.get("father_name", "")).strip()
        dob = str(parsed.get("dob", "")).strip()
        gender = str(parsed.get("gender", "")).strip().upper()
        aadhaar_raw = str(parsed.get("aadhaar_number", "")).strip()
        mobile_raw = str(parsed.get("mobile_number", "")).strip()
        address = str(parsed.get("address", "")).strip()
        aadhaar_digits = only_digits(aadhaar_raw)
        mobile_digits = only_digits(mobile_raw)

        if name:
            data["USER_NAME"] = name
        if father_name:
            data["FATHER_NAME"] = father_name
        if dob:
            data["DATE_OF_BIRTH"] = dob
            year = extract_year_from_dob(dob)
            if year:
                data["YEAR_OF_BIRTH"] = year
        if gender in {"MALE", "FEMALE", "OTHER"}:
            data["GENDER"] = gender
        if len(aadhaar_digits) == 12:
            data["AADHAR_NUMBER"] = aadhaar_digits
        if len(mobile_digits) == 10:
            data["MOBILE_NUMBER"] = mobile_digits
        elif len(mobile_digits) == 12 and mobile_digits.startswith("91"):
            data["MOBILE_NUMBER"] = mobile_digits[2:]
        if address:
            data["ADDRESS"] = " ".join(address.split())

        logger.info("LLM-based Aadhaar extraction applied")

    # ------------------------------------------------------------------------
    def extract_details(self, image_input):
        """
        Main public method.
        Accepts image path or numpy array.
        """
        logger.info("Starting Aadhaar extraction")

        # Load image
        if isinstance(image_input, np.ndarray):
            image = image_input
        else:
            image = cv2.imread(image_input)

        if image is None:
            logger.error("Invalid image input")
            raise ValueError("Invalid image input")

        # Initialize output structure
        data = {
            'USER_NAME': "NA",
            'AADHAR_NUMBER': "NA",
            'FATHER_NAME': "NA",
            'DATE_OF_BIRTH': "NA",
            'YEAR_OF_BIRTH': "NA",
            'GENDER': "NA",
            'MOBILE_NUMBER': "NA",
            'ADDRESS': "NA"
        }

        # Fast path: single orientation first for lower latency/cost.
        logger.info(f"Starting OCR with max_rotations={self.fast_path_rotations}")
        lines = super()._perform_ocr(
            image=image,
            max_rotations=self.fast_path_rotations,
            det=True,
            cls=False,
        )
        logger.info("OCR completed successfully")
        logger.debug(f"OCR Output: {lines}")

        self._extract_details_with_llm(lines, data)
        apply_aadhaar_validation(data)

        # Slow path: retry with all rotations only if critical fields are missing.
        critical_missing = (
            data["AADHAR_NUMBER"] == "NA"
            or data["USER_NAME"] == "NA"
            or data["DATE_OF_BIRTH"] == "NA"
        )
        if critical_missing:
            logger.info("Critical fields missing in fast path. Retrying with all rotations.")
            logger.info(f"Starting OCR with max_rotations={self.full_path_rotations}")
            lines = super()._perform_ocr(
                image=image,
                max_rotations=self.full_path_rotations,
                det=True,
                cls=False,
            )
            logger.info("OCR completed successfully")
            self._extract_details_with_llm(lines, data)
            apply_aadhaar_validation(data)

        logger.info("Aadhaar extraction completed")
        return data
