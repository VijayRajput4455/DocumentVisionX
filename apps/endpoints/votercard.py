import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from src.documents.VoterCardExtractor import VoterCardExtractor
from src.classification.image_classification import image_classification
from src.utils.image_loader import load_image
from src.utils.image_saver import save_image
from src.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Initialize extractor once
extractor = VoterCardExtractor()

@router.post("/extract")
async def extract_voter(
    document_type: str = Form(...),   # voter
    file: UploadFile = File(None),
    image_url: str = Form(None)
):
    """
    Accepts either file upload or image URL,
    validates document type,
    saves image,
    extracts Voter ID details.
    """

    if not file and not image_url:
        raise HTTPException(
            status_code=400,
            detail="Either file or image_url must be provided"
        )

    try:
        # ---------------------------
        # Load image
        # ---------------------------
        if file:
            contents = await file.read()

            if not contents:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is empty"
                )

            image = cv2.imdecode(
                np.frombuffer(contents, np.uint8),
                cv2.IMREAD_COLOR
            )
            logger.info("Voter image loaded from uploaded file")

        else:
            image = load_image(image_url)
            logger.info("Voter image loaded from URL")

        # ---------------------------
        # Validate image
        # ---------------------------
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to decode image"
            )

        if not isinstance(image, np.ndarray):
            raise HTTPException(
                status_code=400,
                detail="Invalid image format"
            )

        if image.size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty image array"
            )

        if len(image.shape) not in [2, 3]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported image dimensions"
            )

        # ---------------------------
        # Validate document type
        # ---------------------------
        predicted_type = image_classification(image)

        if predicted_type.lower() != document_type.lower():
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Document type mismatch. "
                    f"Expected '{document_type}', got '{predicted_type}'"
                )
            )

        # ---------------------------
        # Save image
        # ---------------------------
        image_meta = save_image(
            image=image,
            prefix=document_type.lower()
        )

        logger.info(
            f"Voter image saved | id={image_meta['image_id']} | path={image_meta['relative_path']}"
        )

        # ---------------------------
        # OCR extraction
        # ---------------------------
        ocr_result = extractor.extract_details(image)
        logger.info("Voter extraction successful")

        response = {
            "document_type": document_type,
            "image": {
                "image_id": image_meta["image_id"],
                "image_path": image_meta["filename"]
            },
            "data": ocr_result
        }

        return response

    except HTTPException:
        raise

    except Exception:
        logger.exception("Voter extraction failed")
        raise HTTPException(
            status_code=500,
            detail="Voter OCR failed due to internal error"
        )
