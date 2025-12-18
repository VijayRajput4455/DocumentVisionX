import os
import urllib.request
import cv2
import numpy as np
from src.logger import get_logger

logger = get_logger(__name__)

def load_image(image_source: str) -> np.ndarray:
    """
    Load an image from a local path or online URL.
    """
    # Local file
    if os.path.isfile(image_source):
        image = cv2.imread(image_source)
        if image is None:
            raise ValueError(f"Failed to read local image: {image_source}")
        logger.info(f"Loaded image from local path: {image_source}")
        return image

    # Online URL
    try:
        response = urllib.request.urlopen(image_source)
        image_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Failed to decode image from URL: {image_source}")
        logger.info(f"Downloaded image from URL: {image_source}")
        return image
    except Exception as e:
        raise ValueError(f"Cannot load image from source '{image_source}': {e}")
