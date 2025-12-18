from paddleocr import PaddleOCR
from src.logger import get_logger

logger = get_logger(__name__)

class OCRSingleton:
    _ocr_instance = None

    @classmethod
    def get_instance(cls):
        if cls._ocr_instance is None:
            logger.info("Initializing shared PaddleOCR model")
            cls._ocr_instance = PaddleOCR(lang='en', use_textline_orientation=True, show_log=False)
        return cls._ocr_instance
