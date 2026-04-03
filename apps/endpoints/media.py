import os
import mimetypes
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from src.config import BASE_IMAGE_DIR
from src.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()
@router.get("/images/{document_type}/{filename}")
def get_image(document_type: str, filename: str):
    safe_doc_type = os.path.basename(document_type)
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(BASE_IMAGE_DIR, safe_doc_type, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")

    media_type, _ = mimetypes.guess_type(file_path)
    if media_type is None:
        media_type = "application/octet-stream"

    logger.info(f"Serving image: {file_path}")
    return FileResponse(file_path, media_type=media_type)
