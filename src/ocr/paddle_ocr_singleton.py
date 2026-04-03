from paddleocr import PaddleOCR
from src.logger import get_logger

logger = get_logger(__name__)


class PaddleOCRSingleton:
    _ocr_instance = None

    @staticmethod
    def _build_ocr_instance():
        # PaddleOCR constructor arguments differ between releases.
        candidate_kwargs = [
            {"lang": "en"},
            {"lang": "en", "use_textline_orientation": True},
        ]

        last_error = None
        for kwargs in candidate_kwargs:
            try:
                return PaddleOCR(**kwargs)
            except (TypeError, ValueError) as err:
                last_error = err
                logger.warning("PaddleOCR init failed with args=%s: %s", kwargs, err)

        raise RuntimeError(f"Unable to initialize PaddleOCR with compatible arguments: {last_error}")

    @classmethod
    def get_instance(cls):
        # Backward-compatible alias for existing code paths.
        return cls.get_paddle_instance()

    @classmethod
    def get_paddle_instance(cls):
        if cls._ocr_instance is None:
            logger.info("Initializing shared PaddleOCR model")
            cls._ocr_instance = cls._build_ocr_instance()
        return cls._ocr_instance


# Backward-compatible alias.
OCRSingleton = PaddleOCRSingleton
