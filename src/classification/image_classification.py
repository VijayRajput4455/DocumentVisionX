from ultralytics import YOLO
import cv2
from src.logger import get_logger
from src.config import MODEL_WEIGHTS
logger = get_logger(__name__)

# Load YOLO model once when module is imported
model = YOLO(MODEL_WEIGHTS)
print(model.names,"kkkkkkkkkkkkkk")
logger.info("YOLOv8 model loaded for classification")

def image_classification(image: cv2.Mat) -> str:
    """
    Classify a document image using YOLOv8.
    Returns the predicted document type (e.g., 'aadhar', 'pancard').
    """
    results = model(image)
    predicted_name = None

    for result in results:
        class_id = result.probs.top1
        predicted_name = result.names[class_id]

    logger.info(f"Predicted document type: {predicted_name}")
    return predicted_name
