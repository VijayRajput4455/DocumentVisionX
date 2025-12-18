import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from src.config import BASE_IMAGE_DIR
from src.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()
@router.get("/images/{document_type}/{filename}")
def get_image(document_type: str, filename: str):
    file_path = os.path.join(BASE_IMAGE_DIR, document_type, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    logger.info(f"Serving image: {file_path}")
    return FileResponse(file_path, media_type="image/jpeg")
