import cv2
import numpy as np

from src.config import (
    OCR_BACKEND,
    PAN_FAST_PATH_ROTATIONS,
    PAN_FULL_PATH_ROTATIONS,
    PAN_LLM_ENDPOINT,
    PAN_LLM_MODEL,
    PAN_LLM_TIMEOUT,
)
from src.documents.base_llm_extractor import BaseLLMExtractor
from src.documents.llm_extractor_utils import (
    call_llm_json,
    normalize_with_schema,
)
from src.documents.prompts import build_pan_prompt
from src.documents.schemas import PAN_FIELDS
from src.documents.validators import apply_pan_validation
from src.logger import get_logger

logger = get_logger(__name__)


class PANExtractor(BaseLLMExtractor):
    def __init__(self):
        logger.info("Initializing PanCardExtractor")
        super().__init__(
            ocr_backend=OCR_BACKEND,
            llm_model=PAN_LLM_MODEL,
            llm_endpoint=PAN_LLM_ENDPOINT,
            llm_timeout=PAN_LLM_TIMEOUT,
            fast_path_rotations=PAN_FAST_PATH_ROTATIONS,
            full_path_rotations=PAN_FULL_PATH_ROTATIONS,
            logger=logger,
            extractor_name="PANExtractor",
        )

    def _extract_details_with_llm(self, lines, data):
        raw_text = "\n".join(lines)
        prompt = build_pan_prompt(raw_text)

        parsed = call_llm_json(
            model=self.llm_model,
            endpoint=self.llm_endpoint,
            prompt=prompt,
            timeout=self.llm_timeout,
            logger=logger,
            tag="PAN extraction",
        )
        if not parsed:
            return

        parsed = normalize_with_schema(parsed, PAN_FIELDS)

        pan_number = str(parsed.get("pan_number", "")).strip().upper()
        name = str(parsed.get("name", "")).strip()
        father_name = str(parsed.get("father_name", "")).strip()
        dob = str(parsed.get("dob", "")).strip()

        if pan_number:
            data["PAN_NUMBER"] = pan_number
        if name:
            data["NAME"] = " ".join(name.split())
        if father_name:
            data["FATHER_NAME"] = " ".join(father_name.split())
        if dob:
            data["DATE_OF_BIRTH"] = dob

        logger.info("LLM-based PAN extraction applied")

    def extract_details(self, image_input):
        logger.info("Starting PAN extraction process")

        if isinstance(image_input, np.ndarray):
            image = image_input
        else:
            image = cv2.imread(image_input)

        if image is None:
            raise ValueError("Invalid PAN image input")

        data = {
            "PAN_NUMBER": "NA",
            "NAME": "NA",
            "FATHER_NAME": "NA",
            "DATE_OF_BIRTH": "NA",
        }

        logger.info(f"Performing PAN OCR with max_rotations={self.fast_path_rotations}")
        lines = super()._perform_ocr(
            image=image,
            max_rotations=self.fast_path_rotations,
            det=True,
            cls=False,
        )
        self._extract_details_with_llm(lines, data)
        apply_pan_validation(data)

        critical_missing = data["PAN_NUMBER"] == "NA" or data["NAME"] == "NA"
        if critical_missing:
            logger.info("PAN critical fields missing. Retrying with all rotations.")
            logger.info(f"Performing PAN OCR with max_rotations={self.full_path_rotations}")
            lines = super()._perform_ocr(
                image=image,
                max_rotations=self.full_path_rotations,
                det=True,
                cls=False,
            )
            self._extract_details_with_llm(lines, data)
            apply_pan_validation(data)

        logger.info("PAN extraction completed")
        return data
