from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from apps.endpoints import aadhar, pancard, votercard, bank, media
from src.logger import get_logger
import time

logger = get_logger(__name__)

# -----------------------------
# FastAPI App Initialization
# -----------------------------
app = FastAPI(
    title="DocumentVisionX API",
    description="Document OCR and data extraction API",
    version="1.0.0"
)

# -----------------------------
# Include Routers
# -----------------------------
app.include_router(
    aadhar.router,
    prefix="/aadhar",
    tags=["Aadhaar"]
)

app.include_router(
    pancard.router,
    prefix="/pancard",
    tags=["PAN Card"]
)

app.include_router(
    votercard.router,
    prefix="/voter",
    tags=["Voter ID"]
)

app.include_router(
    bank.router,
    prefix="/bank",
    tags=["Bank Document"]
)

app.include_router(
    media.router, 
    prefix="/media", 
    tags=["Media"]
)

logger.info("FastAPI application initialized with all endpoints")

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to DocumentVisionX API! Use /docs for API documentation."}

# -----------------------------
# Global Request Logging Middleware
# -----------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = None
    try:
        logger.info(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        return response
    finally:
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Completed request: {request.method} {request.url} "
            f"Status code: {response.status_code if response else 'N/A'} "
            f"Time: {process_time:.2f} ms"
        )

# -----------------------------
# Global Exception Handler
# -----------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc} for request {request.method} {request.url}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
