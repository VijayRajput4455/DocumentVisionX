import json
import time
import asyncio

import cv2
import aiohttp
import requests

from src.config import (
    LLM_RETRY_BACKOFF_SECONDS,
    LLM_RETRY_COUNT,
    LOG_OCR_TEXT,
    OCR_TEXT_MAX_CHARS,
    OCR_TEXT_MAX_LINES,
)
from src.logger import get_logger
from src.scalability import LLM_SEMAPHORE, OCR_SEMAPHORE

logger = get_logger(__name__)


def safe_json_from_text(text):
    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    try:
        return json.loads(text[start:end + 1])
    except Exception:
        return None


def only_digits(value):
    return "".join(ch for ch in str(value) if ch.isdigit())


def extract_year_from_dob(dob):
    cleaned = str(dob).replace("-", "/").strip()
    parts = [p for p in cleaned.split("/") if p]
    for part in parts:
        if len(part) == 4 and part.isdigit() and part.startswith(("19", "20")):
            return part
    return ""


def is_valid_name(value, min_len=2, max_len=100):
    if not value or value == "NA":
        return False
    if len(value) < min_len or len(value) > max_len:
        return False
    alpha_count = sum(1 for ch in value if ch.isalpha())
    return alpha_count >= 2


def is_valid_dob(value):
    if not value or value == "NA":
        return False

    cleaned = str(value).replace("-", "/").strip()
    parts = [p for p in cleaned.split("/") if p]
    if len(parts) != 3:
        return False

    day_str, month_str, year_str = parts
    if not (day_str.isdigit() and month_str.isdigit() and year_str.isdigit()):
        return False

    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    if day < 1 or day > 31:
        return False
    if month < 1 or month > 12:
        return False
    if year < 1900 or year > 2099:
        return False
    return True


def is_valid_address(value, min_len=8, max_len=300):
    if not value or value == "NA":
        return False
    if len(value) < min_len or len(value) > max_len:
        return False
    alpha_count = sum(1 for ch in value if ch.isalpha())
    return alpha_count >= 5


def call_llm_json(model, endpoint, prompt, timeout, logger, tag):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    retries = max(0, LLM_RETRY_COUNT)
    for attempt in range(retries + 1):
        try:
            with LLM_SEMAPHORE:
                response = requests.post(endpoint, json=payload, timeout=timeout)
                response.raise_for_status()
                llm_output = response.json().get("response", "").strip()

            parsed = safe_json_from_text(llm_output)
            if not parsed:
                logger.warning(f"LLM JSON parsing failed for {tag}")
                return None
            return parsed
        except Exception as exc:
            if attempt >= retries:
                logger.warning(f"LLM {tag} failed: {exc}")
                return None

            wait_seconds = LLM_RETRY_BACKOFF_SECONDS * (2 ** attempt)
            logger.warning(
                f"LLM {tag} attempt {attempt + 1} failed: {exc}. "
                f"Retrying in {wait_seconds:.2f}s"
            )
            time.sleep(wait_seconds)


async def call_llm_json_async(model, endpoint, prompt, timeout, logger, tag):
    """
    Asynchronously call LLM endpoint and parse JSON response.
    Uses aiohttp for true async I/O instead of blocking requests.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    retries = max(0, LLM_RETRY_COUNT)
    session = None
    
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        session = aiohttp.ClientSession(timeout=timeout_obj)
        
        for attempt in range(retries + 1):
            try:
                # Use semaphore to limit concurrent LLM calls
                with LLM_SEMAPHORE:
                    async with session.post(endpoint, json=payload) as response:
                        response.raise_for_status()
                        result = await response.json()
                        llm_output = result.get("response", "").strip()

                parsed = safe_json_from_text(llm_output)
                if not parsed:
                    logger.warning(f"LLM JSON parsing failed for {tag}")
                    return None
                return parsed
            except aiohttp.ClientError as exc:
                if attempt >= retries:
                    logger.warning(f"LLM {tag} async failed: {exc}")
                    return None

                wait_seconds = LLM_RETRY_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(
                    f"LLM {tag} async attempt {attempt + 1} failed: {exc}. "
                    f"Retrying in {wait_seconds:.2f}s"
                )
                await asyncio.sleep(wait_seconds)
    finally:
        if session:
            await session.close()


def normalize_with_schema(parsed, fields):
    if not isinstance(parsed, dict):
        return {field: "" for field in fields}

    normalized = {}
    for field in fields:
        value = parsed.get(field, "")
        if value is None:
            normalized[field] = ""
        else:
            normalized[field] = str(value)

    return normalized


def get_rotated_images(image):
    return [
        image,
        cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(image, cv2.ROTATE_180),
        cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE),
    ]


def _collect_text_lines_from_paddle_output(output, lines):
    if output is None:
        return

    # Common legacy PaddleOCR item: [box, (text, score)]
    if isinstance(output, list) and len(output) >= 2:
        candidate = output[1]
        if isinstance(candidate, (list, tuple)) and len(candidate) >= 1 and isinstance(candidate[0], str):
            text = candidate[0].strip()
            if text:
                lines.append(text)
            return

    # Legacy PaddleOCR shape: [[ [box, (text, score)], ... ], ...]
    if isinstance(output, list):
        for item in output:
            _collect_text_lines_from_paddle_output(item, lines)
        return

    # Newer predict() object with text list
    rec_texts = getattr(output, "rec_texts", None)
    if rec_texts:
        for text in rec_texts:
            if text:
                lines.append(str(text))
        return

    # Dict-like shapes seen in some wrappers
    if isinstance(output, dict):
        if "rec_texts" in output and isinstance(output["rec_texts"], list):
            for text in output["rec_texts"]:
                if text:
                    lines.append(str(text))
            return

        # Legacy word tuple in dict wrappers
        if 1 in output and isinstance(output[1], (list, tuple)) and len(output[1]) > 0:
            lines.append(str(output[1][0]))
            return

        for value in output.values():
            _collect_text_lines_from_paddle_output(value, lines)
        return

    # Legacy word tuple: [box, (text, score)]
    if isinstance(output, tuple) and len(output) >= 2:
        # Some wrappers return a direct (text, score) tuple.
        if isinstance(output[0], str):
            text = output[0].strip()
            if text:
                lines.append(text)
            return

        candidate = output[1]
        if isinstance(candidate, (list, tuple)) and len(candidate) > 0:
            text = str(candidate[0]).strip()
            if text:
                lines.append(text)


def perform_ocr_lines(image, max_rotations, ocr_backend, ocr, glm_ocr, det=True, cls=False):
    lines = []
    with OCR_SEMAPHORE:
        for img in get_rotated_images(image)[:max_rotations]:
            if ocr_backend == "glm":
                try:
                    glm_text = glm_ocr.extract_text_from_array(img)
                except Exception as exc:
                    logger.exception("GLM OCR failed for one rotation: %s", exc)
                    continue
                lines.extend(glm_text.splitlines())
            else:
                # Try multiple Paddle call styles for broad version compatibility.
                try:
                    result = ocr.predict(img)
                except AttributeError:
                    # Older PaddleOCR versions still expose ocr(...).
                    result = ocr.ocr(img, det=det, cls=cls)
                except TypeError:
                    # Some intermediate versions expose ocr(img) without det/cls kwargs.
                    result = ocr.ocr(img)
                except Exception:
                    # Runtime fallback when predict() exists but fails in current backend.
                    try:
                        result = ocr.ocr(img, det=det, cls=cls)
                    except TypeError:
                        result = ocr.ocr(img)
                    except Exception as exc:
                        logger.exception("Paddle OCR failed for one rotation: %s", exc)
                        continue

                if result is None:
                    continue

                _collect_text_lines_from_paddle_output(result, lines)

    cleaned_lines = [line.strip() for line in lines if line.strip()]

    if LOG_OCR_TEXT:
        limited_lines = cleaned_lines[:max(1, OCR_TEXT_MAX_LINES)]
        preview_text = "\n".join(limited_lines)
        if len(preview_text) > max(1, OCR_TEXT_MAX_CHARS):
            preview_text = preview_text[: max(1, OCR_TEXT_MAX_CHARS)] + "\n...[truncated]"

        logger.info(
            "OCR text preview | backend=%s | lines=%s | showing=%s\n%s",
            ocr_backend,
            len(cleaned_lines),
            len(limited_lines),
            preview_text or "<no text detected>",
        )

    return cleaned_lines
