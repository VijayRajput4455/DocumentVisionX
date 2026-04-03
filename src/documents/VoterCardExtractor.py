import cv2
import numpy as np

from src.config import (
    OCR_BACKEND,
    VOTER_FAST_PATH_ROTATIONS,
    VOTER_FULL_PATH_ROTATIONS,
    VOTER_LLM_ENDPOINT,
    VOTER_LLM_MODEL,
    VOTER_LLM_TIMEOUT,
)
from src.documents.base_llm_extractor import BaseLLMExtractor
from src.documents.llm_extractor_utils import (
    call_llm_json,
    normalize_with_schema,
    only_digits,
)
from src.documents.prompts import build_voter_prompt
from src.documents.schemas import VOTER_FIELDS
from src.documents.validators import apply_voter_validation
from src.logger import get_logger

logger = get_logger(__name__)


class VoterCardExtractor(BaseLLMExtractor):
    def __init__(self):
        logger.info("Initializing VoterCardExtractor")
        super().__init__(
            ocr_backend=OCR_BACKEND,
            llm_model=VOTER_LLM_MODEL,
            llm_endpoint=VOTER_LLM_ENDPOINT,
            llm_timeout=VOTER_LLM_TIMEOUT,
            fast_path_rotations=VOTER_FAST_PATH_ROTATIONS,
            full_path_rotations=VOTER_FULL_PATH_ROTATIONS,
            logger=logger,
            extractor_name="VoterCardExtractor",
        )

    def _extract_details_with_llm(self, lines, data):
        raw_text = "\n".join(lines)
        prompt = build_voter_prompt(raw_text)

        parsed = call_llm_json(
            model=self.llm_model,
            endpoint=self.llm_endpoint,
            prompt=prompt,
            timeout=self.llm_timeout,
            logger=logger,
            tag="Voter extraction",
        )
        if not parsed:
            return

        parsed = normalize_with_schema(parsed, VOTER_FIELDS)

        name = str(parsed.get("name", "")).strip()
        epic = str(parsed.get("epic_number", "")).strip().upper()
        relative_name = str(parsed.get("relative_name", "")).strip()
        father_name = str(parsed.get("father_name", "")).strip()
        dob = str(parsed.get("dob", "")).strip()
        age = str(parsed.get("age", "")).strip()
        gender = str(parsed.get("gender", "")).strip().upper()
        address = str(parsed.get("address", "")).strip()

        if name:
            data["NAME"] = " ".join(name.split())
        if epic:
            data["EPIC_NUMBER"] = epic
        if relative_name:
            data["RELATIVE_NAME"] = " ".join(relative_name.split())
        if father_name:
            data["FATHER_NAME"] = " ".join(father_name.split())
        if dob:
            data["DATE_OF_BIRTH"] = dob
        if age:
            data["AGE"] = only_digits(age)
        if gender:
            data["GENDER"] = gender
        if address:
            data["ADDRESS"] = " ".join(address.split())

        logger.info("LLM-based Voter extraction applied")

    def extract_details(self, image_input):
        logger.info("Starting Voter card extraction")

        if isinstance(image_input, np.ndarray):
            image = image_input
        else:
            image = cv2.imread(image_input)

        if image is None:
            raise ValueError("Invalid image input")

        data = {
            "NAME": "NA",
            "EPIC_NUMBER": "NA",
            "RELATIVE_NAME": "NA",
            "DATE_OF_BIRTH": "NA",
            "AGE": "NA",
            "GENDER": "NA",
            "ADDRESS": "NA",
            "FATHER_NAME": "NA",
        }

        logger.info(f"Performing Voter OCR with max_rotations={self.fast_path_rotations}")
        lines = super()._perform_ocr(
            image=image,
            max_rotations=self.fast_path_rotations,
            det=True,
            cls=False,
        )
        self._extract_details_with_llm(lines, data)
        apply_voter_validation(data)

        critical_missing = data["EPIC_NUMBER"] == "NA" or data["NAME"] == "NA"
        if critical_missing:
            logger.info("Voter critical fields missing. Retrying with all rotations.")
            logger.info(f"Performing Voter OCR with max_rotations={self.full_path_rotations}")
            lines = super()._perform_ocr(
                image=image,
                max_rotations=self.full_path_rotations,
                det=True,
                cls=False,
            )
            self._extract_details_with_llm(lines, data)
            apply_voter_validation(data)

        logger.info("Voter card extraction completed")
        return data
