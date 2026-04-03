![DocumentVisionX](assets/DocumentVisionX.png)

# 🎯 DocumentVisionX

**DocumentVisionX** is a powerful, production-ready **OCR and document data extraction API** for Indian KYC (Know Your Customer) workflows. Extract structured data from **Aadhaar, PAN, Voter ID, and Bank documents** using state-of-the-art computer vision and large language models.

> 🚀 **Get started in 5 minutes** with [Quick Start](#-quick-start) | 📚 **Full API docs** at `/docs`

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🎯 Quick Start](#-quick-start)
- [🔧 Installation & Setup](#-installation--setup)
- [📡 API Endpoints](#-api-endpoints)
- [⚙️ Configuration](#-configuration)
- [🏗️ Architecture Overview](#-architecture-overview)
- [🛠️ Function Details](#-function-details)
- [💾 Project Structure](#-project-structure)
- [📊 Monitoring & Scalability](#-monitoring--scalability)
- [🐛 Troubleshooting](#-troubleshooting)
- [⚡ Performance Tuning](#-performance-tuning)
- [🔒 Security Notes](#-security-notes)
- [📄 License](#-license)

---

## ✨ Features

- ✅ **Multi-Document Extraction**: Aadhaar, PAN, Voter ID, Bank documents
- ✅ **Dual OCR Backends**: PaddleOCR (local) or GLM (cloud-based LLM vision)
- ✅ **LLM-Powered Extraction**: Structured JSON field extraction with validation
- ✅ **Document Classification**: YOLOv8-based document type verification
- ✅ **Production-Ready Scalability**:
  - Concurrent request limiting with semaphores
  - Exponential backoff retry with configurable limits
  - Per-minute rate limiting
  - Health/Ready/Metrics monitoring endpoints
- ✅ **Flexible Image Input**: Upload files or provide URLs
- ✅ **Comprehensive Validation**: Field-level validation with detailed rules
- ✅ **Detailed Logging & Metrics**: Track performance per operation

---

## 🚀 Quick Start

```bash
# 1️⃣ Clone and navigate
git clone <repo-url>
cd DocumentVisionX

# 2️⃣ Create conda environment
conda create -n docvisionx python=3.9
conda activate docvisionx

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Configure environment
cp .env.example .env  # Edit with your settings

# 5️⃣ Start server
uvicorn apps.main:app --reload

# 6️⃣ Visit API docs
# Open: http://localhost:8000/docs
```

---

## 🔧 Installation & Setup

### 📋 System Requirements

| Requirement | Version | Notes |
|---|---|---|
| **Python** | 3.9+ | Tested on 3.9, 3.10, 3.11 |
| **OS** | Linux, macOS, Windows | WSL2 on Windows recommended |
| **RAM** | 8GB+ | 16GB+ recommended for concurrent operations |
| **Storage** | 10GB+ | For models, logs, and image storage |

### Step 1️⃣: Create Conda Environment

**On Linux/macOS:**
```bash
conda create -n docvisionx python=3.9
conda activate docvisionx
```

**On Windows (PowerShell):**
```powershell
conda create -n docvisionx python=3.9
conda activate docvisionx
```

**Verify activation:**
```bash
python --version  # Should show Python 3.9.x
```

### Step 2️⃣: Clone Repository

```bash
git clone <repository-url>
cd DocumentVisionX
```

### Step 3️⃣: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | ≥0.110.0 | 🌐 Web API framework |
| `uvicorn[standard]` | ≥0.29.0 | 🚀 ASGI server |
| `python-multipart` | ≥0.0.9 | 📤 File upload handling |
| `opencv-python` | ≥4.8.0 | 🖼️ Image processing |
| `numpy` | ≥1.24.0 | 📊 Array operations |
| `paddleocr` | 2.7-2.9 | 📖 Local OCR engine |
| `paddlepaddle` | 2.6-2.9 | 🧠 Deep learning framework |
| `ultralytics` | ≥8.2.0 | 🎯 YOLOv8 classifier |
| `requests` | ≥2.31.0 | 🔗 HTTP requests |
| `aiohttp` | latest | ⚡ Async HTTP client |
| `python-dotenv` | ≥1.0.1 | 📝 Environment config |

### Step 4️⃣: Environment Configuration

Create `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

**Edit `.env` with your settings:**

```env
# 🎯 OCR Backend: "paddle" (local) or "glm" (remote LLM)
OCR_BACKEND=glm

# 📖 GLM OCR Configuration (when OCR_BACKEND=glm)
GLM_OCR_MODEL=glm-ocr
GLM_OCR_ENDPOINT=http://localhost:11434/api/generate
GLM_OCR_TIMEOUT=120

# 🤖 LLM Configuration
# For Aadhaar extraction:
AADHAR_LLM_MODEL=llama3.2
AADHAR_LLM_ENDPOINT=http://localhost:11434/api/generate
AADHAR_LLM_TIMEOUT=120

# For PAN extraction:
PAN_LLM_MODEL=llama3.2
PAN_LLM_ENDPOINT=http://localhost:11434/api/generate
PAN_LLM_TIMEOUT=120

# For Voter extraction:
VOTER_LLM_MODEL=llama3.2
VOTER_LLM_ENDPOINT=http://localhost:11434/api/generate
VOTER_LLM_TIMEOUT=120

# For Bank extraction:
BANK_LLM_MODEL=llama3.2
BANK_LLM_ENDPOINT=http://localhost:11434/api/generate
BANK_LLM_TIMEOUT=120

# ⚙️ Scalability Settings
MAX_CONCURRENT_OCR_TASKS=4
MAX_CONCURRENT_LLM_CALLS=4
API_RATE_LIMIT_PER_MINUTE=120

# 📊 Logging
LOG_OCR_TEXT=true
OCR_TEXT_MAX_LINES=120
OCR_TEXT_MAX_CHARS=8000
```

### Step 5️⃣: Verify Model Weights

Pre-trained YOLO classification model should be present:

```bash
ls -la src/classification/models/
# Should show: OcrClassification_V8L_6C_08July24_640B.pt (or similar)
```

If missing, the application will attempt to auto-download on first run.

### Step 6️⃣: Start the Server

```bash
# Development mode (auto-reload on code changes)
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

# Production mode (no auto-reload)
uvicorn apps.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Verify startup:**

```bash
# In another terminal
curl http://localhost:8000/health

# Expected response (if running):
# {"status":"ok","service":"DocumentVisionX",...}
```

---

## 📡 API Endpoints

### 📌 Base URL
```
http://localhost:8000
```

### 🔍 Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

### 1️⃣ Aadhaar Extraction

**Endpoint:**
```
POST /aadhar/extract
```

**Extract data from Aadhaar card images**

**Request Parameters:**
```python
document_type: str = "aadhar"      # Must be exactly "aadhar"
file: UploadFile = None             # OR provide file upload
image_url: str = None               # OR provide image URL
```

**Extracted Fields (7 fields):**

| Field | Type | Validation | Example |
|-------|------|-----------|---------|
| `user_name` | string | 2-80 chars, ≥2 alpha | "Rajesh Kumar Singh" |
| `aadhar_number` | string | 12 digits | "324155412563" |
| `father_name` | string | 2-80 chars, ≥2 alpha | "Vikram Singh" |
| `date_of_birth` | string | DD/MM/YYYY, 1900-2099 | "15/06/1985" |
| `year_of_birth` | string | 4-digit year | "1985" |
| `gender` | string | MALE \| FEMALE \| OTHER \| NA | "MALE" |
| `mobile_number` | string | 10 digits, starts 6-9 | "9876543210" |
| `address` | string | 8-300 chars, ≥5 alpha | "123 Main Street, Delhi..." |

**Example Request (Python):**

```python
import requests

url = "http://localhost:8000/aadhar/extract"

# Method 1: Upload from file
with open("aadhaar.jpg", "rb") as f:
    files = {"file": f}
    data = {"document_type": "aadhar"}
    response = requests.post(url, files=files, data=data)

# Method 2: Provide image URL
response = requests.post(url, data={
    "document_type": "aadhar",
    "image_url": "https://example.com/aadhaar.jpg"
})

print(response.json())
```

**Success Response (200):**

```json
{
  "document_type": "aadhar",
  "image": {
    "image_id": "550e8400-e29b-41d4-a716-446655440001",
    "image_url": "http://localhost:8000/media/images/aadhar/550e8400-e29b-41d4-a716-446655440001.jpg"
  },
  "data": {
    "user_name": "Rajesh Kumar Singh",
    "aadhar_number": "324155412563",
    "father_name": "Vikram Singh",
    "date_of_birth": "15/06/1985",
    "year_of_birth": "1985",
    "gender": "MALE",
    "mobile_number": "9876543210",
    "address": "123 Main Street, New Delhi, Delhi 110001"
  }
}
```

---

### 2️⃣ PAN Card Extraction

**Endpoint:**
```
POST /pancard/extract
```

**Extract data from PAN card images**

**Request Parameters:**
```python
document_type: str = "pancard"      # Must be exactly "pancard"
file: UploadFile = None
image_url: str = None
```

**Extracted Fields (4 fields):**

| Field | Type | Validation | Example |
|-------|------|-----------|---------|
| `pan_number` | string | 10-char PAN format | "ABCDE1234F" |
| `name` | string | 2-80 chars, ≥2 alpha | "Rajesh Kumar" |
| `father_name` | string | 2-80 chars, ≥2 alpha | "Vikram Singh" |
| `date_of_birth` | string | DD/MM/YYYY or NA | "15/06/1985" |

**Example Request (Python):**

```python
import requests

url = "http://localhost:8000/pancard/extract"

with open("pancard.jpg", "rb") as f:
    files = {"file": f}
    data = {"document_type": "pancard"}
    response = requests.post(url, files=files, data=data)

print(response.json())
```

**Success Response (200):**

```json
{
  "document_type": "pancard",
  "image": {
    "image_id": "550e8400-e29b-41d4-a716-446655440002",
    "image_url": "http://localhost:8000/media/images/pancard/550e8400-e29b-41d4-a716-446655440002.jpg"
  },
  "data": {
    "pan_number": "ABCDE1234F",
    "name": "Rajesh Kumar",
    "father_name": "Vikram Singh",
    "date_of_birth": "15/06/1985"
  }
}
```

---

### 3️⃣ Voter ID Extraction

**Endpoint:**
```
POST /voter/extract
```

**Extract data from Voter ID / EPIC card images**

**Request Parameters:**
```python
document_type: str = "voter"        # Must be exactly "voter"
file: UploadFile = None
image_url: str = None
```

**Extracted Fields (8 fields):**

| Field | Type | Validation | Example |
|-------|------|-----------|---------|
| `name` | string | 2-80 chars, ≥2 alpha | "Rajesh Kumar Singh" |
| `voter_id` | string | EPIC number (10 chars) | "ABC1234567" |
| `relative_name` | string | 2-80 chars or use father | "Vikram Singh" |
| `father_name` | string | 2-80 chars (fallback) | "Vikram Singh" |
| `date_of_birth` | string | DD/MM/YYYY format | "15/06/1985" |
| `age` | string | 18-120 numeric | "39" |
| `gender` | string | MALE \| FEMALE \| OTHER \| NA | "MALE" |
| `address` | string | 8-300 chars, ≥5 alpha | "123 Main Street..." |

**Example Request (Python):**

```python
import requests

url = "http://localhost:8000/voter/extract"

with open("voter_card.jpg", "rb") as f:
    files = {"file": f}
    data = {"document_type": "voter"}
    response = requests.post(url, files=files, data=data)

print(response.json())
```

**Success Response (200):**

```json
{
  "document_type": "voter",
  "image": {
    "image_id": "550e8400-e29b-41d4-a716-446655440003",
    "image_url": "http://localhost:8000/media/images/voter/550e8400-e29b-41d4-a716-446655440003.jpg"
  },
  "data": {
    "name": "Rajesh Kumar Singh",
    "voter_id": "ABC1234567",
    "relative_name": "Vikram Singh",
    "father_name": "Vikram Singh",
    "date_of_birth": "15/06/1985",
    "age": "39",
    "gender": "MALE",
    "address": "123 Main Street, New Delhi, Delhi 110001"
  }
}
```

---

### 4️⃣ Bank Document Extraction

**Endpoint:**
```
POST /bank/extract
```

**Extract data from Bank Passbook or Cancelled Cheque images**

**Request Parameters:**
```python
document_type: str = "bank"         # Must be exactly "bank"
file: UploadFile = None
image_url: str = None
```

**Extracted Fields (5 fields):**

| Field | Type | Validation | Example |
|-------|------|-----------|---------|
| `document_subtype` | string | passbook \| cancelled_cheque | "passbook" |
| `account_holder_name` | string | 2-80 chars | "Rajesh Kumar Singh" |
| `account_number` | string | 9-18 digits | "123456789012" |
| `ifsc` | string | 11-char IFSC code | "HDFC0001234" |
| `bank_name` | string | matched against known list | "HDFC Bank" |

**Example Request (Python):**

```python
import requests

url = "http://localhost:8000/bank/extract"

with open("bank_passbook.jpg", "rb") as f:
    files = {"file": f}
    data = {"document_type": "bank"}
    response = requests.post(url, files=files, data=data)

print(response.json())
```

**Success Response (200):**

```json
{
  "document_type": "bank",
  "image": {
    "image_id": "550e8400-e29b-41d4-a716-446655440004",
    "image_url": "http://localhost:8000/media/images/bank/550e8400-e29b-41d4-a716-446655440004.jpg"
  },
  "data": {
    "document_subtype": "passbook",
    "account_holder_name": "Rajesh Kumar Singh",
    "account_number": "123456789012",
    "ifsc": "HDFC0001234",
    "bank_name": "HDFC Bank"
  }
}
```

---

### 5️⃣ Retrieve Saved Image

**Endpoint:**
```
GET /media/images/{document_type}/{filename}
```

**Retrieve image saved from previous extractions**

**Example:**
```bash
curl "http://localhost:8000/media/images/aadhar/550e8400-e29b-41d4-a716-446655440001.jpg" \
  --output retrieved_image.jpg
```

---

### 📊 Health & Monitoring Endpoints

#### Health Check
```
GET /health
```
Returns system status and resource utilization.

**Response:**
```json
{
  "status": "ok",
  "service": "DocumentVisionX",
  "scalability": {
    "ocr": {
      "name": "ocr_semaphore",
      "limit": 4,
      "in_use": 1,
      "available": 3,
      "utilization": 0.25
    },
    "llm": {
      "name": "llm_semaphore",
      "limit": 4,
      "in_use": 0,
      "available": 4,
      "utilization": 0.0
    },
    "rate_limit": {
      "requests_per_minute": 120,
      "window_seconds": 60,
      "active_keys": 2,
      "requests_in_window": 15
    }
  }
}
```

#### Readiness Check
```
GET /ready
```
Check if system has capacity to accept requests.

**Response (Ready):**
```json
{
  "ready": true,
  "reason": "capacity_available",
  "scalability": {...}
}
```

**Response (Busy - HTTP 503):**
```json
{
  "ready": false,
  "reason": "capacity_saturated",
  "scalability": {...}
}
```

#### Metrics
```
GET /metrics
```
Performance metrics for all tracked operations.

**Response:**
```json
{
  "metrics": {
    "aadhar_extraction": {
      "operation": "aadhar_extraction",
      "count": 45,
      "avg_ms": 2350.5,
      "min_ms": 1200,
      "max_ms": 5600,
      "p50_ms": 2100,
      "p95_ms": 4800
    },
    ...
  },
  "timestamp": "2025-04-04T12:30:45.123Z"
}
```

---

### ❌ Error Responses

**400 - Bad Request** (invalid document type, missing file):
```json
{
  "detail": "Invalid document_type for this endpoint. Use 'aadhar' for /aadhar/extract."
}
```

**404 - Not Found** (image doesn't exist):
```json
{
  "detail": "Image not found"
}
```

**503 - Service Unavailable** (capacity exceeded):
```json
{
  "detail": "Service temporarily saturated. Please retry.",
  "scalability": {...}
}
```

---

## ⚙️ Configuration

### Environment Variables Reference

**OCR Backend Configuration:**

```env
# Choose OCR engine
OCR_BACKEND=glm                              # "paddle" or "glm"
LOG_OCR_TEXT=true                            # Log extracted text
OCR_TEXT_MAX_LINES=120                       # Truncate output
OCR_TEXT_MAX_CHARS=8000                      # Character limit
```

**GLM OCR (Remote LLM-based OCR):**

```env
GLM_OCR_MODEL=glm-ocr                        # Model name
GLM_OCR_ENDPOINT=http://localhost:11434/api/generate
GLM_OCR_TIMEOUT=120                          # Seconds
GLM_OCR_RETRY_COUNT=2                        # Failed request retries
GLM_OCR_RETRY_BACKOFF_SECONDS=0.5            # Exponential backoff base
```

**Document-Specific LLM Configuration:**

Each document type uses the same configuration pattern:

```env
# Aadhaar
AADHAR_LLM_MODEL=llama3.2
AADHAR_LLM_ENDPOINT=http://localhost:11434/api/generate
AADHAR_LLM_TIMEOUT=120
AADHAR_FAST_PATH_ROTATIONS=1                 # Quick attempt with 1 rotation
AADHAR_FULL_PATH_ROTATIONS=2                 # Retry with 2 rotations if needed

# PAN
PAN_LLM_MODEL=llama3.2
PAN_LLM_ENDPOINT=http://localhost:11434/api/generate
PAN_LLM_TIMEOUT=120
PAN_FAST_PATH_ROTATIONS=1
PAN_FULL_PATH_ROTATIONS=4                    # More thorough search

# Voter
VOTER_LLM_MODEL=llama3.2
VOTER_LLM_ENDPOINT=http://localhost:11434/api/generate
VOTER_LLM_TIMEOUT=120
VOTER_FAST_PATH_ROTATIONS=1
VOTER_FULL_PATH_ROTATIONS=4

# Bank
BANK_LLM_MODEL=llama3.2
BANK_LLM_ENDPOINT=http://localhost:11434/api/generate
BANK_LLM_TIMEOUT=120
```

**Scalability & Rate Limiting:**

```env
MAX_CONCURRENT_OCR_TASKS=4                   # Parallel OCR operations
MAX_CONCURRENT_LLM_CALLS=4                   # Parallel LLM requests
LLM_RETRY_COUNT=2                            # Retry failed LLM calls
LLM_RETRY_BACKOFF_SECONDS=0.5                # Backoff base (0.5, 1.0, 2.0...)
API_RATE_LIMIT_PER_MINUTE=120                # Per-user requests/minute
```

**File Paths (set in `src/config.py`, modify if needed):**

```
UPLOAD_DIR = "images"                        # Temporary upload storage
LOG_DIR = "logs"                             # Log output directory
BASE_IMAGE_DIR = "storage/kyc_images"        # Persistent image storage
MODEL_WEIGHTS = "src/classification/models/OcrClassification_V8L_6C_08July24_640B.pt"
```

### 🔗 LLM Service Setup (Ollama)

DocumentVisionX expects an Ollama service running locally. This provides both OCR and LLM extraction capabilities.

**If Ollama is not installed:**

```bash
# Visit https://ollama.ai and follow installation for your OS
# Or use Docker:
docker run -d -p 11434:11434 ollama/ollama

# Pull required model:
ollama pull llama3.2

# Verify:
curl http://localhost:11434/api/generate -d '{"model":"llama3.2","prompt":"test"}'
```

> ℹ️ **Note:** Full Ollama setup is outside the scope of this README. See [ollama.ai](https://ollama.ai) for detailed installation instructions.

---

## 🏗️ Architecture Overview

### Request Processing Pipeline

```
┌─────────────────────────────────────┐
│  API Request (File / Image URL)     │
└────────────────┬────────────────────┘
                 ↓
        ┌────────────────────┐
        │  Load Image        │
        │  (local/remote)    │
        └────────┬───────────┘
                 ↓
        ┌────────────────────┐
        │  Classify Document │
        │  (YOLOv8)          │
        └────────┬───────────┘
                 ↓
        ┌────────────────────────────┐
        │  Select Extractor          │
        │  (Aadhaar/PAN/Voter/Bank)  │
        └────────┬───────────────────┘
                 ↓
        ┌────────────────────────────┐
        │  OCR Phase (Multi-rotation)│
        │  PaddleOCR or GLM OCR      │
        └────────┬───────────────────┘
                 ↓
        ┌────────────────────────────┐
        │  LLM Extraction            │
        │  (Structured JSON)         │
        └────────┬───────────────────┘
                 ↓
        ┌────────────────────────────┐
        │  Validation & Normalization│
        │  (Document-specific rules) │
        └────────┬───────────────────┘
                 ↓
        ┌────────────────────────────┐
        │  Save Image                │
        │  (persistent storage)      │
        └────────┬───────────────────┘
                 ↓
    ┌──────────────────────────┐
    │  Return Response + URL   │
    └──────────────────────────┘
```

### Concurrency & Rate Limiting

- **OCR Semaphore**: Limits parallel OCR operations (max 4 by default)
- **LLM Semaphore**: Limits parallel LLM calls (max 4 by default)
- **Rate Limiter**: Per-user rate limiting (120 requests/minute by default)
- **Context Tracking**: Request UUID for distributed tracing

---

## 🛠️ Function Details

### Document Extractors

#### **AadharExtractor**
Extracts Aadhaar card information using multi-rotation OCR + LLM.

**Key Methods:**
- `extract_details(image_input)` - Main method; accepts image path or numpy array
  - Fast path: Single rotation for speed
  - Full path retry: 2 rotations if critical fields missing
  - Validates extracted data
- `_extract_details_with_llm(lines, data)` - Processes OCR output through LLM

**Configuration:** `AADHAR_*` environment variables

---

#### **PANExtractor**
Extracts PAN card information.

**Key Methods:**
- `extract_details(image_input)` - Multi-rotation extraction up to 4 rotations
- `_extract_details_with_llm(lines, data)` - LLM-based extraction

**Configuration:** `PAN_*` environment variables

---

#### **VoterCardExtractor**
Extracts Voter ID card information with smart fallbacks.

**Key Methods:**
- `extract_details(image_input)` - Extraction with retry on missing critical fields
- Smart logic: Uses father name if relative name missing
- `_extract_details_with_llm(lines, data)` - Structured extraction

**Configuration:** `VOTER_*` environment variables

---

#### **BankExtractor**
Extracts bank document information (passbook/cheque).

**Key Methods:**
- `extract_details(image)` - Single-rotation OCR + LLM extraction
- `run_ocr(image)` - OCR with character classification enabled
- Auto-detection: Identifies passbook vs. cancelled cheque

**Configuration:** `BANK_*` environment variables

---

### Utility Functions

#### **perform_ocr_lines()**
Multi-rotation OCR with backend switching.

```python
def perform_ocr_lines(image, max_rotations, ocr_backend, ocr, glm_ocr):
    """
    Rotates image 0°, 90°, 180°, 270° and extracts text.
    Supports both PaddleOCR and GLM backends.
    Returns list of cleaned text lines.
    """
```

#### **call_llm_json() / call_llm_json_async()**
LLM calls with exponential backoff retry.

```python
def call_llm_json(model, endpoint, prompt, timeout, logger, tag):
    """
    Calls LLM endpoint, extracts JSON from response.
    Retries on failure with exponential backoff.
    Uses LLM_SEMAPHORE for rate limiting.
    """
```

#### **Image I/O Functions**
```python
load_image(image_source)     # Load image from file or URL
save_image(image, prefix)    # Save image to storage, return metadata
```

---

### Validators

**Aadhaar Validation Rules:**
- Name: 2-80 chars, ≥2 alphabetic
- Aadhaar: exactly 12 digits
- DOB: valid DD/MM/YYYY (1900-2099)
- Mobile: 10 digits starting with 6-9
- Address: 8-300 chars, ≥5 alphabetic

**PAN Validation Rules:**
- PAN: 5 letters + 4 digits + 1 letter
- Name/Father Name: standard name rules
- DOB: valid date format

**Voter Validation Rules:**
- EPIC: 3 letters + 7 digits (10 total)
- Age: 18-120
- Gender: MALE | FEMALE | OTHER
- Smart fallback: uses father name if relative name missing

**Bank Validation Rules:**
- Subtype: passbook or cancelled_cheque
- Account: 9-18 digits
- IFSC: 11 chars (4 letters + "0" + 6 alphanumeric)
- Bank name: matches known bank list
- Auto-detection: identifies subtype from "CANCEL" keyword

---

## 💾 Project Structure

```
DocumentVisionX/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── .env                               # Your configuration (gitignored)
│
├── apps/
│   ├── main.py                        # FastAPI app setup, health/ready endpoints
│   └── endpoints/                     # Document extraction endpoints
│       ├── aadhar.py                  # POST /aadhar/extract
│       ├── pancard.py                 # POST /pancard/extract
│       ├── votercard.py               # POST /voter/extract
│       ├── bank.py                    # POST /bank/extract
│       └── media.py                   # GET /media/images/{type}/{filename}
│
├── src/
│   ├── config.py                      # Configuration & environment variables
│   ├── logger.py                      # Logging setup
│   ├── context.py                     # Request context & tracing
│   ├── metrics.py                     # Performance metrics collector
│   ├── scalability.py                 # Semaphores & rate limiting
│   │
│   ├── classification/
│   │   ├── image_classification.py    # YOLOv8 document classifier
│   │   └── models/
│   │       └── OcrClassification_V8L_6C_08July24_640B.pt
│   │
│   ├── documents/                     # Document extractors
│   │   ├── base_llm_extractor.py      # Base class for all extractors
│   │   ├── AadharExtracter.py
│   │   ├── PanCardExtracter.py
│   │   ├── VoterCardExtractor.py
│   │   ├── BankExtractor.py
│   │   ├── llm_extractor_utils.py     # OCR, LLM, validation utilities
│   │   ├── prompts/                   # LLM prompts per document type
│   │   │   ├── aadhaar.py
│   │   │   ├── bank.py
│   │   │   ├── pan.py
│   │   │   └── voter.py
│   │   ├── schemas/                   # Field schemas per document type
│   │   │   ├── aadhaar.py
│   │   │   ├── bank.py
│   │   │   ├── pan.py
│   │   │   └── voter.py
│   │   └── validators/                # Validation rules per document type
│   │       ├── aadhaar.py
│   │       ├── bank.py
│   │       ├── pan.py
│   │       └── voter.py
│   │
│   ├── ocr/                           # OCR backend management
│   │   ├── ocr_factory.py             # Create OCR instances
│   │   ├── paddle_ocr_singleton.py    # PaddleOCR singleton
│   │   └── glm_ocr_singleton.py       # GLM OCR singleton
│   │
│   ├── schemas/
│   │   └── api_models.py              # Pydantic request/response models
│   │
│   └── utils/
│       ├── image_loader.py            # Load images from file/URL
│       └── image_saver.py             # Save extracted images
│
├── storage/
│   └── kyc_images/                    # Persistent image storage
│       ├── aadhar/
│       ├── pancard/
│       └── voter/
│
├── logs/                              # Application logs
│   └── DocVisionX.log
│
└── tests/                             # (Optional) Unit tests
    └── ...
```

---

## 📊 Monitoring & Scalability

### Health Checks

Use these endpoints to monitor system health:

```bash
# System health + resource usage
curl http://localhost:8000/health | jq

# Check if service has capacity before sending request
curl http://localhost:8000/ready | jq

# Performance metrics
curl http://localhost:8000/metrics | jq
```

### Interpreting Scalability Stats

The `/health` response includes:

```json
"ocr": {
  "limit": 4,                    // Max concurrent OCR operations
  "in_use": 1,                   // Currently running
  "available": 3,                // Available slots
  "utilization": 0.25            // Percentage (in_use / limit)
}
```

**Action items:**
- `utilization > 0.8`: Consider adding more servers or increasing limits
- `available == 0`: System at capacity, requests will be delayed
- Adjust `MAX_CONCURRENT_OCR_TASKS` in `.env` if bottleneck

---

## 🐛 Troubleshooting

### ❌ Issue: ModuleNotFoundError: No module named 'paddleocr'

**Cause:** Dependencies not installed or wrong environment activated.

**Solution:**
```bash
# Verify environment activation
conda activate docvisionx  # Make sure you see (docvisionx) in terminal

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Verify installation
python -c "import paddleocr; print('✓ PaddleOCR installed')"
```

---

### ❌ Issue: "Connection refused" to Ollama endpoint

**Cause:** Ollama service not running on expected address.

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/generate -d '{"model":"test"}'

# If error, start Ollama (example with Docker):
docker run -d -p 11434:11434 ollama/ollama
ollama pull llama3.2

# Update .env if Ollama is on different host:
GLM_OCR_ENDPOINT=http://your-ollama-host:11434/api/generate
```

---

### ❌ Issue: "YOLO model weights not found"

**Cause:** Pre-trained classifier model missing.

**Solution:**
```bash
# Check files exist
ls -la src/classification/models/

# If missing, download manually (will be attempted on startup)
# File: OcrClassification_V8L_6C_08July24_640B.pt
# Place in: src/classification/models/

# Restart app
```

---

### ❌ Issue: Extraction returns empty/NA fields

**Cause:** 
1. Image quality too low
2. Document not in expected position
3. LLM service timeout

**Solution:**
```bash
# 1. Try better image (bright, document-centered, high resolution)

# 2. Increase OCR rotations (try harder):
export AADHAR_FULL_PATH_ROTATIONS=4  # Try up to 4 rotations

# 3. Increase LLM timeout:
export AADHAR_LLM_TIMEOUT=180        # 180 seconds instead of 120

# 4. Check logs for details:
tail -f logs/DocVisionX.log
```

---

### ❌ Issue: "Rate limit exceeded" / HTTP 429

**Cause:** Too many concurrent requests.

**Solution:**
```bash
# Check current stats
curl http://localhost:8000/health | jq '.scalability'

# Option 1: Increase rate limit
export API_RATE_LIMIT_PER_MINUTE=200

# Option 2: Distribute requests over time
# Send in batches with delays between them

# Option 3: Scale horizontally
# Run multiple server instances (see nginx/load balancer setup)
```

---

### ❌ Issue: PaddleOCR model download failing

**Cause:** Network issue or slow connection.

**Solution:**
```bash
# First attempt downloads models (this may take time)
# Check your network connection

# Try manual download with retry
python -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(use_angle_cls=True); print('✓ Ready')"

# If still fails, check firewall/proxy settings
```

---

### ❌ Issue: "File not found" when saving image

**Cause:** Directory doesn't exist or permission denied.

**Solution:**
```bash
# Create necessary directories
mkdir -p storage/kyc_images/{aadhar,pancard,voter,bank}
mkdir -p logs images

# Fix permissions
chmod 755 storage/kyc_images
chmod 755 logs
```

---

## ⚡ Performance Tuning

### 📈 Increase Throughput

**Scenario:** System needs to handle 100s of requests/minute

**Actions:**

1. **Increase concurrency limits:**
```env
MAX_CONCURRENT_OCR_TASKS=8          # Up from 4
MAX_CONCURRENT_LLM_CALLS=8          # Up from 4
API_RATE_LIMIT_PER_MINUTE=500       # Adjust as needed
```

2. **Run multiple uvicorn workers:**
```bash
uvicorn apps.main:app --host 0.0.0.0 --port 8000 --workers 4
```

3. **Use a load balancer (nginx):**
```bash
# Route traffic across multiple servers
```

---

### ⚡ Reduce Latency

**Scenario:** Single requests taking too long (> 5 seconds)

**Actions:**

1. **Reduce rotation attempts for fast path:**
```env
AADHAR_FAST_PATH_ROTATIONS=1        # Already optimized
PAN_FAST_PATH_ROTATIONS=1
VOTER_FAST_PATH_ROTATIONS=1
```

2. **Increase timeouts (counter-intuitive but helps):**
```env
AADHAR_LLM_TIMEOUT=150              # More time = fewer retries
GLM_OCR_TIMEOUT=150
```

3. **Pre-process images for better OCR:**
   - Ensure bright lighting
   - Document centered and straight
   - High resolution (1200+ pixels wide)

---

### 💾 Reduce Memory Usage

**Scenario:** System running out of memory

**Actions:**

1. **Reduce concurrent tasks:**
```env
MAX_CONCURRENT_OCR_TASKS=2
MAX_CONCURRENT_LLM_CALLS=2
```

2. **Use PaddleOCR with smaller model (if available)**

3. **Monitor memory:**
```bash
# Watch memory usage
watch -n 1 'ps aux | grep uvicorn'
```

---

### 📊 Monitor Performance in Real-Time

```bash
# Every 5 seconds, show current utilization
watch -n 5 'curl -s http://localhost:8000/health | jq ".scalability | {ocr_util: .ocr.utilization, llm_util: .llm.utilization}"'

# Get detailed metrics
curl http://localhost:8000/metrics | jq '.metrics | to_entries[] | "\(.key): avg=\(.value.avg_ms)ms p95=\(.value.p95_ms)ms"'
```

---

## 🔒 Security Notes

1. **Image Storage**: Saved images stored in `storage/kyc_images/` — restrict access to authorized users only
2. **API Access**: Use authentication (API keys/OAuth) in production
3. **PII Data**: Handle personally identifiable data according to local regulations (GDPR, data protection laws)
4. **Endpoint Security**: Don't expose `/health` or `/metrics` to untrusted networks
5. **HTTPS**: Use HTTPS in production (configure via reverse proxy)
6. **Rate Limiting**: Prevents abuse; adjust based on your use case
7. **Audit Logging**: All operations are logged; monitor logs for suspicious activity

---

## 📄 License

[Add your license information here]

---

## 🤝 Contributing

[Add contribution guidelines here]

---

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub or contact the development team.

**Last Updated:** April 4, 2025  
**Version:** 1.0.0
