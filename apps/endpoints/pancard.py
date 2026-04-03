import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.concurrency import run_in_threadpool

from src.documents.PanCardExtracter import PANExtractor
from src.classification.image_classification import image_classification
from src.utils.image_loader import load_image
from src.utils.image_saver import save_image
from src.logger import get_logger
from src.schemas.api_models import PANExtractionRequest, PANExtractionResponse

router = APIRouter()
logger = get_logger(__name__)
EXPECTED_DOCUMENT_TYPE = "pancard"

# Initialize PAN extractor once
pan_extractor = PANExtractor()

@router.post("/extract", response_model=PANExtractionResponse)
async def extract_pan(
    request: Request,
    document_type: str = Form(...),  # e.g., "pancard"
    file: UploadFile = File(None),
    image_url: str = Form(None)
) -> PANExtractionResponse:
    """
    Accepts either a file upload or an image URL, validates document type using classifier,
    saves the image, and extracts PAN card details.
    """

    normalized_document_type = document_type.strip().lower()

    if normalized_document_type != EXPECTED_DOCUMENT_TYPE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid document_type for this endpoint. "
                f"Use '{EXPECTED_DOCUMENT_TYPE}' for /pancard/extract."
            )
        )

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
            logger.info("PAN image loaded from uploaded file")
        else:
            image = await run_in_threadpool(load_image, image_url)
            logger.info("PAN image loaded from URL")

        # ---------------------------
        # Validate image
        # ---------------------------
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to decode image. Unsupported or corrupted image."
            )

        if not isinstance(image, np.ndarray):
            logger.error(f"Invalid image type: {type(image)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid image format. Image could not be processed."
            )

        if image.size == 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid image: empty image array"
            )

        if len(image.shape) not in [2, 3]:
            raise HTTPException(
                status_code=400,
                detail="Invalid image: unsupported image dimensions"
            )

        # ---------------------------
        # Validate document type
        # ---------------------------
        predicted_type = await run_in_threadpool(image_classification, image)

        if predicted_type.lower() != document_type.lower():
            logger.warning(
                f"Document type mismatch: Expected {document_type}, got {predicted_type}"
            )
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Document type mismatch. "
                    f"Expected '{document_type}', got '{predicted_type}'"
                )
            )

        # ---------------------------
        # Save image HERE
        # ---------------------------
        image_meta = await run_in_threadpool(
            save_image,
            image=image,
            prefix=document_type
        )

        logger.info(
            f"PAN image saved | id={image_meta['image_id']} | path={image_meta['relative_path']}"
        )

        # ---------------------------
        # Extract PAN details
        # ---------------------------
        ocr_result = await run_in_threadpool(pan_extractor.extract_details, image)
        logger.info("PAN extraction successful")

        # ----------------------------------
        # Merge image path into ocr_result
        # ----------------------------------
        image_url = str(
            request.url_for(
                "get_image",
                document_type=EXPECTED_DOCUMENT_TYPE,
                filename=image_meta["filename"],
            )
        )

        return PANExtractionResponse(
            document_type=EXPECTED_DOCUMENT_TYPE,
            image={
                "image_id": image_meta["image_id"],
                "image_url": image_url,
            },
            data=ocr_result
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("PAN extraction failed")
        raise HTTPException(
            status_code=500,
            detail="PAN OCR failed due to internal error"
        )