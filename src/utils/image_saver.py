import os
import uuid
import cv2
from datetime import datetime

from src.config import BASE_IMAGE_DIR

def save_image(
    image,
    prefix: str = "kyc",
    ext: str = ".png"
) -> dict:
    """
    Saves image to disk and returns metadata.
    """

    if image is None:
        raise ValueError("Cannot save empty image")

    # Create date-based folders (scalable)
    # date_folder = datetime.utcnow().strftime("%Y/%m/%d")
    # save_dir = os.path.join(BASE_IMAGE_DIR, date_folder)
    save_dir = os.path.join(BASE_IMAGE_DIR, prefix)
    os.makedirs(save_dir, exist_ok=True)

    # Unique filename
    image_id = str(uuid.uuid4())
    filename = f"{prefix}_{image_id}{ext}"

    file_path = os.path.join(save_dir, filename)

    # Save image
    success = cv2.imwrite(file_path, image)
    if not success:
        raise IOError("Failed to save image to disk")

    return {
        "image_id": image_id,
        "file_path": file_path,
        "relative_path": f"/{BASE_IMAGE_DIR}/{prefix}/{filename}",
        "filename": filename
    }
