"""
DocumentVisionX — Streamlit UI
Dark navy + neon-cyan theme matching the project logo.
Calls the existing FastAPI endpoints at localhost:8000 (or DOCUMENTVISIONX_API_URL).
"""

import os
import io
import base64
import json
import requests
from PIL import Image
import streamlit as st

# ─────────────────────────── page config (MUST be first st call) ───────────
st.set_page_config(
    page_title="DocumentVisionX",
    page_icon="assets/DocumentVisionX.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── constants ─────────────────────────────────────
API_BASE_URL = os.environ.get("DOCUMENTVISIONX_API_URL", "http://localhost:8000").rstrip("/")
API_TIMEOUT  = 180  # seconds

DOC_OPTIONS = {
    "🪪  Aadhaar Card":  "aadhaar",
    "💳  PAN Card":      "pancard",
    "🗳️  Voter ID Card": "voter",
    "🏦  Bank Document": "bank",
}

ENDPOINT_MAP = {
    "aadhaar": "/aadhar/extract",
    "pancard": "/pancard/extract",
    "voter":   "/voter/extract",
    "bank":    "/bank/extract",
}

FORM_DOC_TYPE = {
    "aadhaar": "aadhar",
    "pancard": "pancard",
    "voter":   "voter",
    "bank":    "bank",
}

FIELD_LABELS = {
    "aadhaar": {
        "USER_NAME":      ("👤 Full Name",       "person"),
        "AADHAR_NUMBER":  ("🔢 Aadhaar Number",  "id"),
        "FATHER_NAME":    ("👨 Father's Name",   "person"),
        "DATE_OF_BIRTH":  ("🎂 Date of Birth",   "date"),
        "YEAR_OF_BIRTH":  ("📅 Year of Birth",   "date"),
        "GENDER":         ("⚥ Gender",           "info"),
        "MOBILE_NUMBER":  ("📱 Mobile Number",    "phone"),
        "ADDRESS":        ("📍 Address",          "address"),
    },
    "pancard": {
        "PAN_NUMBER":    ("🪪 PAN Number",      "id"),
        "NAME":          ("👤 Name",             "person"),
        "FATHER_NAME":   ("👨 Father's Name",    "person"),
        "DATE_OF_BIRTH": ("🎂 Date of Birth",    "date"),
    },
    "voter": {
        "NAME":           ("👤 Name",              "person"),
        "EPIC_NUMBER":    ("🪪 EPIC Number",        "id"),
        "RELATIVE_NAME":  ("👥 Relative's Name",   "person"),
        "FATHER_NAME":    ("👨 Father's Name",      "person"),
        "DATE_OF_BIRTH":  ("🎂 Date of Birth",      "date"),
        "AGE":            ("🔢 Age",                "info"),
        "GENDER":         ("⚥ Gender",              "info"),
        "ADDRESS":        ("📍 Address",             "address"),
    },
    "bank": {
        "document_subtype":    ("📄 Document Sub-type",  "info"),
        "account_holder_name": ("👤 Account Holder",     "person"),
        "account_number":      ("🔢 Account Number",     "id"),
        "ifsc":                ("🏦 IFSC Code",           "id"),
        "bank_name":           ("🏛️ Bank Name",           "info"),
    },
}

DOC_ICONS = {
    "aadhaar": "🪪",
    "pancard": "💳",
    "voter":   "🗳️",
    "bank":    "🏦",
}

# ─────────────────────────── CSS injection ─────────────────────────────────
def inject_css():
    st.markdown("""
<style>
/* ── Google Font ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@700;900&display=swap');

/* ── Root variables ─────────────────────────────────────────────────────── */
:root {
  --navy-deep:   #020b18;
  --navy-mid:    #071428;
  --navy-card:   #0a1e3a;
  --navy-border: #0e2a4d;
  --cyan-bright: #00c8ff;
  --cyan-mid:    #0096cc;
  --cyan-glow:   rgba(0, 200, 255, 0.3);
  --cyan-faint:  rgba(0, 200, 255, 0.08);
  --text-main:   #e8f4ff;
  --text-muted:  #7a9bbf;
  --accent-gold: #f5a623;
  --success:     #00e676;
  --error-red:   #ff4d6d;
  --warn-orange: #ff9800;
}

/* ── Global background ──────────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container {
  background: var(--navy-deep) !important;
  color: var(--text-main) !important;
  font-family: 'Inter', sans-serif !important;
}

[data-testid="stApp"] {
  background: var(--navy-deep) !important;
}

/* Star-field pseudo-background */
[data-testid="stAppViewContainer"]::before {
  content: '';
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background:
    radial-gradient(1px 1px at 20% 30%, rgba(0,200,255,0.6) 0%, transparent 100%),
    radial-gradient(1px 1px at 80% 10%, rgba(0,200,255,0.4) 0%, transparent 100%),
    radial-gradient(1px 1px at 50% 70%, rgba(0,200,255,0.3) 0%, transparent 100%),
    radial-gradient(1px 1px at 10% 80%, rgba(0,200,255,0.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 90% 60%, rgba(0,200,255,0.4) 0%, transparent 100%),
    radial-gradient(1.5px 1.5px at 35% 15%, rgba(255,255,255,0.3) 0%, transparent 100%),
    radial-gradient(1.5px 1.5px at 65% 85%, rgba(255,255,255,0.2) 0%, transparent 100%);
  pointer-events: none;
  z-index: 0;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #020e1e 0%, #030f22 40%, #041426 100%) !important;
  border-right: 1px solid var(--navy-border) !important;
}

[data-testid="stSidebar"] * {
  color: var(--text-main) !important;
}

/* ── Sidebar logo container ──────────────────────────────────────────────── */
.dvx-logo-container {
  text-align: center;
  padding: 1.5rem 0 0.5rem;
}

.dvx-logo-container img {
  filter: drop-shadow(0 0 18px rgba(0, 200, 255, 0.5));
  border-radius: 12px;
}

/* ── Sidebar headings ──────────────────────────────────────────────────── */
.dvx-sidebar-title {
  font-family: 'Orbitron', sans-serif !important;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--cyan-bright) !important;
  letter-spacing: 0.12em;
  text-align: center;
  text-transform: uppercase;
  margin: 0.25rem 0 1.2rem;
  text-shadow: 0 0 10px var(--cyan-glow);
}

.dvx-sidebar-section {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 1.2rem 0 0.5rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dvx-sidebar-section::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--navy-border), transparent);
}

/* ── Radio buttons ────────────────────────────────────────────────────────── */
[data-testid="stRadio"] > div {
  gap: 0.4rem !important;
}

[data-testid="stRadio"] label {
  background: var(--navy-card) !important;
  border: 1px solid var(--navy-border) !important;
  border-radius: 10px !important;
  padding: 0.6rem 1rem !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  font-size: 0.88rem !important;
}

[data-testid="stRadio"] label:hover {
  border-color: var(--cyan-mid) !important;
  background: var(--cyan-faint) !important;
}

[data-testid="stRadio"] label[data-checked="true"],
[data-testid="stRadio"] label:has(input:checked) {
  border-color: var(--cyan-bright) !important;
  background: linear-gradient(135deg, rgba(0,200,255,0.12), rgba(0,150,200,0.06)) !important;
  box-shadow: 0 0 12px var(--cyan-glow) !important;
}

/* ── Main area headings ───────────────────────────────────────────────────── */
.dvx-page-header {
  text-align: center;
  padding: 1rem 0 0.2rem;
}

.dvx-page-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 2.2rem;
  font-weight: 900;
  background: linear-gradient(135deg, #00c8ff 0%, #0080ff 50%, #00e5ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: none;
  filter: drop-shadow(0 0 20px rgba(0,200,255,0.4));
  margin: 0;
}

.dvx-page-subtitle {
  font-size: 0.95rem;
  color: var(--text-muted);
  margin-top: 0.3rem;
}

/* ── Panel cards ─────────────────────────────────────────────────────────── */
.dvx-panel {
  background: var(--navy-card);
  border: 1px solid var(--navy-border);
  border-radius: 16px;
  padding: 1.6rem;
  position: relative;
  overflow: hidden;
}

.dvx-panel::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--cyan-bright), transparent);
}

.dvx-panel-title {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--cyan-bright);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Image preview ───────────────────────────────────────────────────────── */
.dvx-image-wrapper {
  border: 1.5px solid var(--cyan-mid);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 0 20px var(--cyan-glow), inset 0 0 20px rgba(0,0,0,0.3);
  margin: 0.8rem 0;
}

.dvx-image-wrapper img {
  width: 100%;
  display: block;
}

/* ── Extract button ─────────────────────────────────────────────────────── */
[data-testid="stButton"] > button {
  background: linear-gradient(135deg, #0073e6 0%, #00b4ff 50%, #00e5ff 100%) !important;
  color: #020b18 !important;
  font-family: 'Orbitron', sans-serif !important;
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.08em !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 0.75rem 2rem !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: all 0.25s ease !important;
  box-shadow: 0 4px 20px rgba(0, 180, 255, 0.4) !important;
}

[data-testid="stButton"] > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 30px rgba(0, 200, 255, 0.6) !important;
  filter: brightness(1.1) !important;
}

[data-testid="stButton"] > button:active {
  transform: translateY(0) !important;
}

/* ── File uploader ───────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
  border: 2px dashed var(--navy-border) !important;
  border-radius: 12px !important;
  background: rgba(0,200,255,0.03) !important;
  transition: border-color 0.2s !important;
}

[data-testid="stFileUploader"]:hover {
  border-color: var(--cyan-mid) !important;
}

/* ── Result field rows ───────────────────────────────────────────────────── */
.dvx-field-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--navy-border);
}

.dvx-field-row:last-child {
  border-bottom: none;
}

.dvx-field-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--cyan-bright);
  background: rgba(0, 200, 255, 0.1);
  border: 1px solid rgba(0, 200, 255, 0.25);
  border-radius: 6px;
  padding: 3px 9px;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 140px;
  text-align: center;
  line-height: 1.6;
}

.dvx-field-value {
  font-size: 0.92rem;
  font-weight: 500;
  color: var(--text-main);
  flex: 1;
  word-break: break-word;
  line-height: 1.55;
  padding-top: 2px;
}

.dvx-field-value.na {
  color: var(--text-muted);
  font-style: italic;
  font-size: 0.85rem;
}

.dvx-field-value.id-value {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: var(--cyan-bright);
  letter-spacing: 0.05em;
}

/* ── Result card header ──────────────────────────────────────────────────── */
.dvx-result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--navy-border);
}

.dvx-doc-badge {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #020b18;
  background: linear-gradient(135deg, #00c8ff, #0073e6);
  border-radius: 20px;
  padding: 4px 14px;
}

.dvx-image-id {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-family: 'Courier New', monospace;
}

/* ── Placeholder state ───────────────────────────────────────────────────── */
.dvx-placeholder {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}

.dvx-placeholder-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  filter: grayscale(0.3);
}

.dvx-placeholder-text {
  font-size: 0.9rem;
  line-height: 1.6;
}

/* ── Steps in sidebar ────────────────────────────────────────────────────── */
.dvx-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 0.75rem;
}

.dvx-step-num {
  width: 22px;
  height: 22px;
  min-width: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0073e6, #00c8ff);
  font-size: 0.7rem;
  font-weight: 800;
  color: #020b18;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}

.dvx-step-text {
  font-size: 0.8rem;
  color: var(--text-muted);
  line-height: 1.5;
}

/* ── Metric chips (health) ───────────────────────────────────────────────── */
.dvx-metric-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(0,200,255,0.08);
  border: 1px solid rgba(0,200,255,0.2);
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 0.78rem;
  color: var(--cyan-bright);
  margin: 2px;
}

/* ── Spinner override ────────────────────────────────────────────────────── */
[data-testid="stSpinner"] {
  color: var(--cyan-bright) !important;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--navy-deep); }
::-webkit-scrollbar-thumb { background: var(--navy-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--cyan-glow); }

/* ── Hide Streamlit chrome ──────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Success/error banners ───────────────────────────────────────────────── */
.dvx-banner {
  border-radius: 10px;
  padding: 0.9rem 1.2rem;
  margin: 0.8rem 0;
  font-size: 0.88rem;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.dvx-banner.error {
  background: rgba(255, 77, 109, 0.1);
  border: 1px solid rgba(255, 77, 109, 0.35);
  color: #ff7096;
}

.dvx-banner.warning {
  background: rgba(255, 152, 0, 0.1);
  border: 1px solid rgba(255, 152, 0, 0.35);
  color: #ffb74d;
}

.dvx-banner.success {
  background: rgba(0, 230, 118, 0.08);
  border: 1px solid rgba(0, 230, 118, 0.3);
  color: #00e676;
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
.dvx-divider {
  border: none;
  border-top: 1px solid var(--navy-border);
  margin: 1.2rem 0;
}

/* ── Column gap fix ──────────────────────────────────────────────────────── */
[data-testid="stColumns"] { gap: 1.5rem; }

/* ── Footer strip ────────────────────────────────────────────────────────── */
.dvx-result-footer {
  margin-top: 1rem;
  padding-top: 0.7rem;
  border-top: 1px solid var(--navy-border);
  font-size: 0.7rem;
  color: var(--text-muted);
  text-align: right;
  letter-spacing: 0.04em;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────── helpers ───────────────────────────────────────
def img_to_base64(pil_img: Image.Image, fmt: str = "PNG") -> str:
    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode()
    mime = "image/png" if fmt == "PNG" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def logo_html(path: str, width: int = 210) -> str:
    try:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return (
            f'<div class="dvx-logo-container">'
            f'<img src="data:image/png;base64,{b64}" width="{width}px" alt="DocumentVisionX"/>'
            f'</div>'
        )
    except FileNotFoundError:
        return '<div class="dvx-logo-container"><span style="font-size:2rem;">🔭</span></div>'


def banner(msg: str, kind: str = "error", icon: str = "⚠️") -> str:
    return f'<div class="dvx-banner {kind}"><span>{icon}</span><span>{msg}</span></div>'


def extract_document(
    file_bytes: bytes,
    filename: str,
    doc_type: str,
) -> dict:
    """POST to the appropriate extraction endpoint. Returns parsed response JSON."""
    endpoint = API_BASE_URL + ENDPOINT_MAP[doc_type]
    form_doc_type = FORM_DOC_TYPE[doc_type]

    # Determine content type from filename extension
    ext = filename.rsplit(".", 1)[-1].lower()
    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    mime_type = mime_map.get(ext, "image/jpeg")

    files = {"file": (filename, file_bytes, mime_type)}
    data  = {"document_type": form_doc_type}

    resp = requests.post(endpoint, files=files, data=data, timeout=API_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# ─────────────────────────── results renderer ──────────────────────────────
def render_result_card(doc_type: str, api_response: dict):
    data_obj   = api_response.get("data", {})
    image_meta = api_response.get("image", {})
    image_id   = image_meta.get("image_id", "N/A")
    fields     = FIELD_LABELS.get(doc_type, {})
    doc_label  = {
        "aadhaar": "Aadhaar Card",
        "pancard": "PAN Card",
        "voter":   "Voter ID Card",
        "bank":    "Bank Document",
    }.get(doc_type, doc_type.upper())

    # Header
    st.markdown(
        f'<div class="dvx-result-header">'
        f'  <span class="dvx-doc-badge">{DOC_ICONS[doc_type]} {doc_label}</span>'
        f'  <span class="dvx-image-id">ID: {image_id[:8]}…</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not fields:
        st.json(data_obj)
        return

    rows_html = ""
    for key, (label, field_type) in fields.items():
        raw_val = data_obj.get(key, "")
        if raw_val is None or str(raw_val).strip() == "":
            val_str   = "Not Available"
            val_class = "na"
        else:
            val_str   = str(raw_val)
            val_class = "id-value" if field_type == "id" else ""

        label_text = label.split(" ", 1)[1] if " " in label else label  # strip emoji for badge
        emoji_part = label.split(" ", 1)[0]

        rows_html += (
            f'<div class="dvx-field-row">'
            f'  <span class="dvx-field-label">{emoji_part} {label_text}</span>'
            f'  <span class="dvx-field-value {val_class}">{val_str}</span>'
            f'</div>'
        )

    st.markdown(rows_html, unsafe_allow_html=True)
    st.markdown(
        '<div class="dvx-result-footer">Extracted via DocumentVisionX API</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────── sidebar ───────────────────────────────────────
def build_sidebar() -> str:
    with st.sidebar:
        st.markdown(logo_html("assets/DocumentVisionX.png", width=210), unsafe_allow_html=True)
        st.markdown(
            '<p class="dvx-sidebar-title">Document Intelligence Platform</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="dvx-sidebar-section">📂 Document Type</div>',
            unsafe_allow_html=True,
        )
        selected_label = st.radio(
            label="Select document type",
            options=list(DOC_OPTIONS.keys()),
            index=0,
            label_visibility="collapsed",
        )

        st.markdown('<hr class="dvx-divider"/>', unsafe_allow_html=True)

        # How it works
        st.markdown(
            '<div class="dvx-sidebar-section">💡 How it works</div>',
            unsafe_allow_html=True,
        )
        steps = [
            ("Select", "Choose the document type from the options above."),
            ("Upload", "Drop or browse an image file (JPG, PNG, WEBP)."),
            ("Extract", "Click Extract Details — AI reads your document instantly."),
        ]
        for i, (title, desc) in enumerate(steps, 1):
            st.markdown(
                f'<div class="dvx-step">'
                f'<div class="dvx-step-num">{i}</div>'
                f'<div class="dvx-step-text"><strong>{title}</strong> — {desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="dvx-divider"/>', unsafe_allow_html=True)

        # API status
        st.markdown(
            '<div class="dvx-sidebar-section">🔌 API Status</div>',
            unsafe_allow_html=True,
        )
        try:
            health = requests.get(f"{API_BASE_URL}/health", timeout=3).json()
            status = health.get("status", "unknown")
            chip_color = "#00e676" if status == "healthy" else "#ff9800"
            st.markdown(
                f'<span class="dvx-metric-chip" style="color:{chip_color};border-color:{chip_color}33;">'
                f'● {status.upper()}</span>',
                unsafe_allow_html=True,
            )
        except Exception:
            st.markdown(
                '<span class="dvx-metric-chip" style="color:#ff4d6d;border-color:#ff4d6d33;">'
                '● OFFLINE</span>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<p style="font-size:0.68rem;color:#3a6080;margin-top:0.5rem;">'
            f'API: {API_BASE_URL}</p>',
            unsafe_allow_html=True,
        )

    return DOC_OPTIONS[selected_label]


# ─────────────────────────── main ──────────────────────────────────────────
def main():
    inject_css()
    doc_type = build_sidebar()

    # Page header
    st.markdown(
        '<div class="dvx-page-header">'
        '<h1 class="dvx-page-title">DocumentVisionX</h1>'
        '<p class="dvx-page-subtitle">AI-powered document intelligence · Extract structured data in seconds</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br/>", unsafe_allow_html=True)

    col_upload, col_spacer, col_result = st.columns([1, 0.06, 1])

    # ── LEFT: Upload panel ──────────────────────────────────────────────────
    with col_upload:
        st.markdown(
            '<div class="dvx-panel">'
            '<div class="dvx-panel-title">📤 Upload Document</div>',
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            label="Upload an image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            help="Supported formats: JPG, JPEG, PNG, WEBP",
        )

        if uploaded_file:
            file_bytes = uploaded_file.read()
            pil_img = Image.open(io.BytesIO(file_bytes))

            # Resize for display (max 600px wide, maintain aspect)
            max_w = 600
            if pil_img.width > max_w:
                ratio = max_w / pil_img.width
                pil_img_display = pil_img.resize(
                    (max_w, int(pil_img.height * ratio)), Image.LANCZOS
                )
            else:
                pil_img_display = pil_img

            img_src = img_to_base64(pil_img_display)
            st.markdown(
                f'<div class="dvx-image-wrapper"><img src="{img_src}" /></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p style="font-size:0.74rem;color:#3a6080;margin-top:0.3rem;">'
                f'📎 {uploaded_file.name} &nbsp;·&nbsp; '
                f'{pil_img.width}×{pil_img.height}px &nbsp;·&nbsp; '
                f'{len(file_bytes) / 1024:.1f} KB</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="border:2px dashed #0e2a4d;border-radius:12px;padding:2.5rem 1rem;'
                'text-align:center;color:#3a6080;font-size:0.85rem;margin:0.8rem 0;">'
                '<div style="font-size:2.5rem;margin-bottom:0.6rem;">🖼️</div>'
                'Drag & drop your document image here<br/>'
                '<span style="font-size:0.75rem;color:#1e3a54;">Supported: JPG · PNG · WEBP</span>'
                '</div>',
                unsafe_allow_html=True,
            )

        extract_clicked = st.button("⚡  Extract Details", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)  # close dvx-panel

    # ── RIGHT: Result panel ─────────────────────────────────────────────────
    with col_result:
        st.markdown(
            '<div class="dvx-panel">'
            '<div class="dvx-panel-title">🔍 Extracted Data</div>',
            unsafe_allow_html=True,
        )

        if not extract_clicked:
            # idle placeholder
            labels_preview = list(FIELD_LABELS.get(doc_type, {}).values())
            preview_items = "".join(
                f'<div style="height:10px;background:rgba(0,200,255,0.07);border-radius:4px;'
                f'margin:6px 0;width:{70 + (i % 3) * 10}%;"></div>'
                for i in range(min(len(labels_preview), 6))
            )
            doc_label_map = {
                "aadhaar": "Aadhaar Card",
                "pancard": "PAN Card",
                "voter":   "Voter ID Card",
                "bank":    "Bank Document",
            }
            st.markdown(
                f'<div class="dvx-placeholder">'
                f'<div class="dvx-placeholder-icon">{DOC_ICONS[doc_type]}</div>'
                f'<div class="dvx-placeholder-text">'
                f'Upload a <strong>{doc_label_map[doc_type]}</strong> image<br/>and click '
                f'<strong>⚡ Extract Details</strong><br/>to see structured data here.'
                f'</div>'
                f'<div style="margin-top:1.5rem;padding:0 1rem;">{preview_items}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        elif not uploaded_file:
            st.markdown(
                banner(
                    "Please upload an image first, then click Extract Details.",
                    kind="warning",
                    icon="⚠️",
                ),
                unsafe_allow_html=True,
            )

        else:
            with st.spinner("🔭  Analysing document…"):
                try:
                    result = extract_document(file_bytes, uploaded_file.name, doc_type)
                    st.markdown(
                        banner(
                            "Extraction complete — all fields retrieved successfully.",
                            kind="success",
                            icon="✅",
                        ),
                        unsafe_allow_html=True,
                    )
                    render_result_card(doc_type, result)

                except requests.exceptions.ConnectionError:
                    st.markdown(
                        banner(
                            f"Cannot reach the API server at <code>{API_BASE_URL}</code>. "
                            "Please start the FastAPI server and try again.",
                            kind="error",
                            icon="🔴",
                        ),
                        unsafe_allow_html=True,
                    )
                except requests.exceptions.Timeout:
                    st.markdown(
                        banner(
                            f"Request timed out after {API_TIMEOUT}s. "
                            "The server may be busy — please retry.",
                            kind="warning",
                            icon="⏱️",
                        ),
                        unsafe_allow_html=True,
                    )
                except requests.exceptions.HTTPError as exc:
                    status_code = exc.response.status_code if exc.response is not None else "?"
                    try:
                        detail = exc.response.json().get("detail", str(exc))
                    except Exception:
                        detail = str(exc)
                    st.markdown(
                        banner(
                            f"API error {status_code}: {detail}",
                            kind="error",
                            icon="❌",
                        ),
                        unsafe_allow_html=True,
                    )
                except Exception as exc:  # noqa: BLE001
                    st.markdown(
                        banner(f"Unexpected error: {exc}", kind="error", icon="🚨"),
                        unsafe_allow_html=True,
                    )

        st.markdown('</div>', unsafe_allow_html=True)  # close dvx-panel


if __name__ == "__main__":
    main()
