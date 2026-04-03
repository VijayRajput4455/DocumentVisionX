import os
from dotenv import load_dotenv

# Load .env first; fall back to .env.example for local/dev convenience.
load_dotenv(".env")
load_dotenv(".env.example")


def _getenv_clean(name: str, default: str) -> str:
	value = os.getenv(name, default)
	return str(value).strip().strip('"').strip("'")

# --- Directories ---
UPLOAD_DIR = "images"
LOG_DIR = "logs"
LOG_FILE = "DocVisionX.log" 

# Path to your trained YOLO model weights
MODEL_WEIGHTS = r"src/classification/models/OcrClassification_V8L_6C_08July24_640B.pt"

BASE_IMAGE_DIR = "storage/kyc_images"

# OCR backend configuration
# Supported backends: "paddle", "glm" (default)
OCR_BACKEND = _getenv_clean("OCR_BACKEND", "glm").lower()
if OCR_BACKEND not in {"paddle", "glm"}:
	OCR_BACKEND = "glm"
LOG_OCR_TEXT = os.getenv("LOG_OCR_TEXT", "true").strip().lower() in {"1", "true", "yes", "on"}
OCR_TEXT_MAX_LINES = int(os.getenv("OCR_TEXT_MAX_LINES", "120"))
OCR_TEXT_MAX_CHARS = int(os.getenv("OCR_TEXT_MAX_CHARS", "8000"))

# GLM OCR config (used only when OCR_BACKEND=glm)
GLM_OCR_MODEL = os.getenv("GLM_OCR_MODEL", "glm-ocr")
GLM_OCR_ENDPOINT = os.getenv("GLM_OCR_ENDPOINT", "http://localhost:11434/api/generate")
GLM_OCR_TIMEOUT = int(os.getenv("GLM_OCR_TIMEOUT", "120"))
GLM_OCR_RETRY_COUNT = int(os.getenv("GLM_OCR_RETRY_COUNT", "2"))
GLM_OCR_RETRY_BACKOFF_SECONDS = float(os.getenv("GLM_OCR_RETRY_BACKOFF_SECONDS", "0.5"))

# Aadhaar LLM extraction config
AADHAR_LLM_MODEL = os.getenv("AADHAR_LLM_MODEL", "llama3.2")
AADHAR_LLM_ENDPOINT = os.getenv("AADHAR_LLM_ENDPOINT", "http://localhost:11434/api/generate")
AADHAR_LLM_TIMEOUT = int(os.getenv("AADHAR_LLM_TIMEOUT", "120"))

# Aadhaar OCR rotation strategy
AADHAR_FAST_PATH_ROTATIONS = int(os.getenv("AADHAR_FAST_PATH_ROTATIONS", "1"))
AADHAR_FULL_PATH_ROTATIONS = int(os.getenv("AADHAR_FULL_PATH_ROTATIONS", "4"))

# PAN LLM extraction config
PAN_LLM_MODEL = os.getenv("PAN_LLM_MODEL", "llama3.2")
PAN_LLM_ENDPOINT = os.getenv("PAN_LLM_ENDPOINT", "http://localhost:11434/api/generate")
PAN_LLM_TIMEOUT = int(os.getenv("PAN_LLM_TIMEOUT", "120"))
PAN_FAST_PATH_ROTATIONS = int(os.getenv("PAN_FAST_PATH_ROTATIONS", "1"))
PAN_FULL_PATH_ROTATIONS = int(os.getenv("PAN_FULL_PATH_ROTATIONS", "4"))

# Voter LLM extraction config
VOTER_LLM_MODEL = os.getenv("VOTER_LLM_MODEL", "llama3.2")
VOTER_LLM_ENDPOINT = os.getenv("VOTER_LLM_ENDPOINT", "http://localhost:11434/api/generate")
VOTER_LLM_TIMEOUT = int(os.getenv("VOTER_LLM_TIMEOUT", "120"))
VOTER_FAST_PATH_ROTATIONS = int(os.getenv("VOTER_FAST_PATH_ROTATIONS", "1"))
VOTER_FULL_PATH_ROTATIONS = int(os.getenv("VOTER_FULL_PATH_ROTATIONS", "4"))

# Bank LLM extraction config
BANK_LLM_MODEL = os.getenv("BANK_LLM_MODEL", "llama3.2")
BANK_LLM_ENDPOINT = os.getenv("BANK_LLM_ENDPOINT", "http://localhost:11434/api/generate")
BANK_LLM_TIMEOUT = int(os.getenv("BANK_LLM_TIMEOUT", "120"))

# Scalability controls
MAX_CONCURRENT_OCR_TASKS = int(os.getenv("MAX_CONCURRENT_OCR_TASKS", "4"))
MAX_CONCURRENT_LLM_CALLS = int(os.getenv("MAX_CONCURRENT_LLM_CALLS", "4"))
LLM_RETRY_COUNT = int(os.getenv("LLM_RETRY_COUNT", "2"))
LLM_RETRY_BACKOFF_SECONDS = float(os.getenv("LLM_RETRY_BACKOFF_SECONDS", "0.5"))
API_RATE_LIMIT_PER_MINUTE = int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "120"))