from src.ocr.glm_ocr_singleton import GLMOCRSingleton
from src.ocr.paddle_ocr_singleton import PaddleOCRSingleton


class OCRFactory:
    @staticmethod
    def get_clients(backend: str):
        backend_value = (backend or "").strip().lower()
        if backend_value == "glm":
            return {
                "paddle": None,
                "glm": GLMOCRSingleton.get_instance(),
            }

        return {
            "paddle": PaddleOCRSingleton.get_paddle_instance(),
            "glm": None,
        }
