from src.config import BANK_LLM_ENDPOINT, BANK_LLM_MODEL, BANK_LLM_TIMEOUT, OCR_BACKEND
from src.documents.base_llm_extractor import BaseLLMExtractor
from src.documents.llm_extractor_utils import (
    call_llm_json,
    normalize_with_schema,
)
from src.documents.prompts import build_bank_prompt
from src.documents.schemas import BANK_FIELDS
from src.documents.validators import apply_bank_validation
from src.logger import get_logger

logger = get_logger(__name__)


class BankExtractor(BaseLLMExtractor):
    def __init__(self):
        super().__init__(
            ocr_backend=OCR_BACKEND,
            llm_model=BANK_LLM_MODEL,
            llm_endpoint=BANK_LLM_ENDPOINT,
            llm_timeout=BANK_LLM_TIMEOUT,
            fast_path_rotations=1,
            full_path_rotations=1,
            logger=logger,
            extractor_name="BankExtractor",
        )

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
            "IDFC FIRST BANK",
        ]

    def _extract_details_with_llm(self, raw_text, data):
        prompt = build_bank_prompt(raw_text)

        parsed = call_llm_json(
            model=self.llm_model,
            endpoint=self.llm_endpoint,
            prompt=prompt,
            timeout=self.llm_timeout,
            logger=logger,
            tag="Bank extraction",
        )
        if not parsed:
            return

        parsed = normalize_with_schema(parsed, BANK_FIELDS)

        subtype = str(parsed.get("document_subtype", "")).strip().lower()
        account_holder_name = str(parsed.get("account_holder_name", "")).strip()
        account_number = str(parsed.get("account_number", "")).strip()
        ifsc = str(parsed.get("ifsc", "")).strip().upper()
        bank_name = str(parsed.get("bank_name", "")).strip().upper()

        if subtype:
            data["document_subtype"] = subtype
        if account_holder_name:
            data["account_holder_name"] = " ".join(account_holder_name.split())
        if account_number:
            data["account_number"] = account_number
        if ifsc:
            data["ifsc"] = ifsc
        if bank_name:
            data["bank_name"] = " ".join(bank_name.split())

        logger.info("LLM-based Bank extraction applied")

    def run_ocr(self, image):
        lines = super()._perform_ocr(image=image, max_rotations=1, det=True, cls=True)
        return "\n".join(lines).upper()

    def extract_details(self, image):
        ocr_text = self.run_ocr(image)

        data = {
            "document_subtype": "NA",
            "account_holder_name": "NA",
            "account_number": "NA",
            "ifsc": "NA",
            "bank_name": "NA",
            "raw_text": ocr_text,
        }

        self._extract_details_with_llm(ocr_text, data)
        apply_bank_validation(data, self.bank_names)
        return data
