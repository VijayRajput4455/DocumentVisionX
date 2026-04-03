from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from apps.endpoints import aadhar, pancard, votercard, bank, media
from src.config import API_RATE_LIMIT_PER_MINUTE
from src.logger import get_logger
from src.scalability import RATE_LIMITER, get_scalability_stats
from src.classification.image_classification import preload_classification_model
from src.schemas.api_models import HealthResponse, ReadyResponse, MetricsResponse
from src.context import set_request_id, reset_request_id
from src.metrics import get_metrics_collector
from datetime import datetime
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


@app.on_event("startup")
async def preload_models() -> None:
    preload_classification_model()
    logger.info("Classification model preloaded at startup")

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to DocumentVisionX API! Use /docs for API documentation."}


@app.get("/health", response_model=HealthResponse)
async def health():
    stats = get_scalability_stats()
    return HealthResponse(
        status="ok",
        service="DocumentVisionX",
        scalability=stats,
    )


@app.get("/ready")
async def ready():
    stats = get_scalability_stats()
    ocr_busy = stats["ocr"]["in_use"] >= stats["ocr"]["limit"]
    llm_busy = stats["llm"]["in_use"] >= stats["llm"]["limit"]
    is_ready = not (ocr_busy or llm_busy)

    response = ReadyResponse(
        ready=is_ready,
        reason="capacity_available" if is_ready else "capacity_saturated",
        scalability=stats,
    )
    
    status_code = 200 if is_ready else 503
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )


@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    """Expose performance metrics for all tracked operations."""
    metrics_collector = get_metrics_collector()
    all_stats = metrics_collector.get_all_stats()
    
    # Convert to Pydantic model format
    metrics_data = {
        op: {
            "operation": stat["operation"],
            "count": stat["count"],
            "avg_ms": stat["avg_ms"],
            "min_ms": stat["min_ms"],
            "max_ms": stat["max_ms"],
            "p50_ms": stat["p50_ms"],
            "p95_ms": stat["p95_ms"],
        }
        for op, stat in all_stats.items()
    }
    
    return MetricsResponse(
        metrics=metrics_data,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )

# -----------------------------
# Request Context Setup Middleware
# Set request ID for trace correlation across all logs
# -----------------------------
@app.middleware("http")
async def setup_request_context(request: Request, call_next):
    """Set request ID in context at start of each request."""
    req_id = set_request_id()
    try:
        response = await call_next(request)
        return response
    finally:
        reset_request_id()


# -----------------------------
# Global Request Logging Middleware
# -----------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = None
    try:
        client_host = request.client.host if request.client else "unknown"
        rate_limit_key = f"{client_host}:{request.url.path}"
        if not RATE_LIMITER.allow(rate_limit_key):
            logger.warning(f"Rate limit exceeded for {rate_limit_key}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please retry shortly."},
                headers={"Retry-After": "60"},
            )

        logger.info(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        return response
    finally:
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Completed request: {request.method} {request.url} "
            f"Status code: {response.status_code if response else 'N/A'} "
            f"Time: {process_time:.2f} ms "
            f"RateLimitPerMinute: {API_RATE_LIMIT_PER_MINUTE}"
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
