from ultralytics import YOLO
import cv2
from typing import List
from threading import Lock
from src.logger import get_logger
from src.config import MODEL_WEIGHTS

logger = get_logger(__name__)

_model = None
_model_lock = Lock()


def _get_model() -> YOLO:
    """Return a process-local singleton YOLO model instance."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = YOLO(MODEL_WEIGHTS)
                logger.info("YOLOv8 model loaded for classification")
    return _model


def preload_classification_model() -> None:
    """Eagerly load model at app startup to avoid first-request latency."""
    _get_model()


def _predict_name_from_result(result) -> str:
    """Safely extract the top-1 class name from a YOLO classification result."""
    if result is None or result.probs is None:
        return "unknown"

    class_id = int(result.probs.top1)
    return result.names.get(class_id, "unknown")

def image_classification(image: cv2.Mat) -> str:
    """
    Classify a document image using YOLOv8.
    Returns the predicted document type (e.g., 'aadhar', 'pancard').
    """
    if image is None:
        logger.warning("Received empty image for classification")
        return "unknown"

    model = _get_model()
    results = model(image, verbose=False)
    if not results:
        logger.warning("No classification results returned by model")
        return "unknown"

    predicted_name = _predict_name_from_result(results[0])
    logger.info("Predicted document type: %s", predicted_name)
    return predicted_name


def image_classification_batch(images: List[cv2.Mat]) -> List[str]:
    """
    Classify multiple document images in one model call.
    Returns predictions in the same order as input images.
    """
    if not images:
        return []

    predictions: List[str] = ["unknown"] * len(images)
    valid_indices = [idx for idx, image in enumerate(images) if image is not None]

    if not valid_indices:
        logger.warning("Batch classification received only empty images")
        return predictions

    valid_images = [images[idx] for idx in valid_indices]
    model = _get_model()
    results = model(valid_images, verbose=False)

    if not results:
        logger.warning("No classification results returned for batch request")
        return predictions

    for out_idx, result in enumerate(results):
        if out_idx >= len(valid_indices):
            break
        input_idx = valid_indices[out_idx]
        predictions[input_idx] = _predict_name_from_result(result)

    logger.info("Batch predicted document types: %s", predictions)
    return predictions
