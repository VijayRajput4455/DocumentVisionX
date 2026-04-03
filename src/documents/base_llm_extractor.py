from src.documents.llm_extractor_utils import perform_ocr_lines
from src.ocr.ocr_factory import OCRFactory


class BaseLLMExtractor:
    def __init__(
        self,
        *,
        ocr_backend,
        llm_model,
        llm_endpoint,
        llm_timeout,
        fast_path_rotations=1,
        full_path_rotations=1,
        logger=None,
        extractor_name="Extractor",
    ):
        self.ocr_backend = ocr_backend
        self.llm_model = llm_model
        self.llm_endpoint = llm_endpoint
        self.llm_timeout = llm_timeout
        self.fast_path_rotations = max(1, fast_path_rotations)
        self.full_path_rotations = max(self.fast_path_rotations, full_path_rotations)

        clients = OCRFactory.get_clients(self.ocr_backend)
        self.ocr = clients["paddle"]
        self.glm_ocr = clients["glm"]

        if logger is not None:
            if self.ocr_backend == "glm":
                logger.info(f"{extractor_name} using GLM OCR backend")
            else:
                logger.info(f"{extractor_name} using PaddleOCR backend")

    def _perform_ocr(self, image, max_rotations=1, det=True, cls=False):
        return perform_ocr_lines(
            image=image,
            max_rotations=max_rotations,
            ocr_backend=self.ocr_backend,
            ocr=self.ocr,
            glm_ocr=self.glm_ocr,
            det=det,
            cls=cls,
        )
