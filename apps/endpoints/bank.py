import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.concurrency import run_in_threadpool

from src.documents.BankExtractor import BankExtractor
from src.classification.image_classification import image_classification
from src.utils.image_loader import load_image
from src.utils.image_saver import save_image
from src.logger import get_logger
from src.schemas.api_models import BankExtractionRequest, BankExtractionResponse

router = APIRouter()
logger = get_logger(__name__)
EXPECTED_DOCUMENT_TYPE = "bank"

# Initialize once (IMPORTANT)
extractor = BankExtractor()


@router.post("/extract", response_model=BankExtractionResponse)
async def extract_bank_document(
    request: Request,
    document_type: str = Form(...),
    file: UploadFile = File(None),
    image_url: str = Form(None)
) -> BankExtractionResponse:
    """
    Supports:
    - Bank Passbook
    - Cancelled Cheque
    Image upload or image URL only
    """

    normalized_document_type = document_type.strip().lower()

    if normalized_document_type != EXPECTED_DOCUMENT_TYPE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid document_type for this endpoint. "
                f"Use '{EXPECTED_DOCUMENT_TYPE}' for /bank/extract."
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
                raise HTTPException(400, "Uploaded file is empty")

            image = cv2.imdecode(
                np.frombuffer(contents, np.uint8),
                cv2.IMREAD_COLOR
            )
            logger.info("Bank document image loaded from file")

        else:
            image = await run_in_threadpool(load_image, image_url)
            logger.info("Bank document image loaded from URL")

        # ---------------------------
        # Image validation
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
        # Validate Document Type
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
        # Save image
        # ---------------------------
        image_meta = await run_in_threadpool(
            save_image,
            image=image,
            prefix=document_type
        )

        logger.info(
                f"Bank document image saved | id={image_meta['image_id']} | path={image_meta['relative_path']}"
            )
        
        # ---------------------------
        # Extract Bank details
        # ---------------------------
        ocr_result = await run_in_threadpool(extractor.extract_details, image)
        logger.info("Bank extraction successful")

        # --------------------------------
        # Merge image path into ocr_result
        # --------------------------------
        image_url = str(
            request.url_for(
                "get_image",
                document_type=EXPECTED_DOCUMENT_TYPE,
                filename=image_meta["filename"],
            )
        )

        return BankExtractionResponse(
            document_type=EXPECTED_DOCUMENT_TYPE,
            image={
                "image_id": image_meta["image_id"],
                "image_url": image_url,
            },
            data=ocr_result
        )
    except HTTPException as e:
        raise

    except Exception as e:
        logger.exception("Error during bank document extraction")
        raise HTTPException(
            status_code=500,
            detail="Bank OCR failed due to internal error"
        )