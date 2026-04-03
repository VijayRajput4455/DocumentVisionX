import base64
import asyncio
import time

import cv2
import aiohttp
import requests

from src.config import (
    GLM_OCR_ENDPOINT,
    GLM_OCR_MODEL,
    GLM_OCR_RETRY_BACKOFF_SECONDS,
    GLM_OCR_RETRY_COUNT,
    GLM_OCR_TIMEOUT,
)
from src.logger import get_logger

logger = get_logger(__name__)


class GLMOCR:
    """Synchronous GLM OCR client (backward compatible)."""
    
    def __init__(self, model: str = GLM_OCR_MODEL, endpoint: str = GLM_OCR_ENDPOINT):
        self.model = model
        self.endpoint = endpoint

    @staticmethod
    def _encode_image_array(image) -> str:
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise ValueError("Failed to encode image for GLM OCR")
        return base64.b64encode(encoded.tobytes()).decode("utf-8")

    def extract_text_from_array(self, image):
        image_base64 = self._encode_image_array(image)

        prompt = """
                You are an advanced multilingual OCR system.

                Extract ALL visible text from the image EXACTLY as it appears.

                STRICT RULES:
                - Preserve original language (English, etc.)
                - DO NOT translate
                - DO NOT summarize
                - DO NOT modify characters
                - Preserve numbers and formatting

                Return raw text only.
                """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
        }

        retries = max(0, GLM_OCR_RETRY_COUNT)
        last_exc = None
        for attempt in range(retries + 1):
            try:
                response = requests.post(self.endpoint, json=payload, timeout=GLM_OCR_TIMEOUT)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "").strip()
            except requests.RequestException as exc:
                last_exc = exc
                if attempt >= retries:
                    break

                wait_seconds = GLM_OCR_RETRY_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(
                    "GLM OCR request failed (attempt %s/%s): %s. Retrying in %.2fs",
                    attempt + 1,
                    retries + 1,
                    exc,
                    wait_seconds,
                )
                time.sleep(wait_seconds)

        raise RuntimeError(f"GLM OCR failed after retries: {last_exc}")


class GLMOCRAsync:
    """Async GLM OCR client using aiohttp for true async I/O."""
    
    def __init__(self, model: str = GLM_OCR_MODEL, endpoint: str = GLM_OCR_ENDPOINT):
        self.model = model
        self.endpoint = endpoint
        self._session = None

    @staticmethod
    def _encode_image_array(image) -> str:
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise ValueError("Failed to encode image for GLM OCR")
        return base64.b64encode(encoded.tobytes()).decode("utf-8")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=GLM_OCR_TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def extract_text_from_array_async(self, image) -> str:
        """
        Asynchronously extract text from image using GLM OCR.
        Uses true async I/O instead of blocking requests.
        """
        image_base64 = self._encode_image_array(image)

        prompt = """
                You are an advanced multilingual OCR system.

                Extract ALL visible text from the image EXACTLY as it appears.

                STRICT RULES:
                - Preserve original language (English, etc.)
                - DO NOT translate
                - DO NOT summarize
                - DO NOT modify characters
                - Preserve numbers and formatting

                Return raw text only.
                """

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
        }

        retries = max(0, GLM_OCR_RETRY_COUNT)
        last_exc = None
        session = await self._get_session()

        for attempt in range(retries + 1):
            try:
                async with session.post(
                    self.endpoint,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result.get("response", "").strip()
            except aiohttp.ClientError as exc:
                last_exc = exc
                if attempt >= retries:
                    break

                wait_seconds = GLM_OCR_RETRY_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(
                    "GLM OCR async request failed (attempt %s/%s): %s. Retrying in %.2fs",
                    attempt + 1,
                    retries + 1,
                    exc,
                    wait_seconds,
                )
                await asyncio.sleep(wait_seconds)

        raise RuntimeError(f"GLM OCR async failed after retries: {last_exc}")

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def __del__(self):
        """Cleanup on deletion."""
        if self._session and not self._session.closed:
            try:
                asyncio.run(self.close())
            except RuntimeError:
                # Event loop might be closed already
                pass


class GLMOCRSingleton:
    _glm_instance = None
    _glm_async_instance = None

    @classmethod
    def get_instance(cls) -> GLMOCR:
        """Get synchronous GLM OCR instance."""
        if cls._glm_instance is None:
            logger.info("Initializing shared synchronous GLM OCR client")
            cls._glm_instance = GLMOCR()
        return cls._glm_instance

    @classmethod
    def get_async_instance(cls) -> GLMOCRAsync:
        """Get asynchronous GLM OCR instance."""
        if cls._glm_async_instance is None:
            logger.info("Initializing shared async GLM OCR client")
            cls._glm_async_instance = GLMOCRAsync()
        return cls._glm_async_instance
