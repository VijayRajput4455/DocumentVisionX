import logging
import os
from threading import Lock
from src.config import LOG_DIR, LOG_FILE
from src.context import get_request_id

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Format includes request ID for trace correlation
LOG_FORMAT = "[%(asctime)s] [%(request_id)s] [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class RequestIdFilter(logging.Filter):
    """Add current request ID to all log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


# True singleton logger with lock to prevent handler duplication
_ROOT_LOGGER = None
_LOGGER_LOCK = Lock()


def _setup_root_logger() -> logging.Logger:
    """Initialize the root logger once with file and console handlers."""
    root = logging.getLogger("DocumentVisionX")
    root.setLevel(logging.INFO)
    
    # Clear any existing handlers to prevent duplicates
    root.handlers.clear()
    
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    request_id_filter = RequestIdFilter()

    # File handler (single instance per process)
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(request_id_filter)

    # Console handler (single instance per process)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(request_id_filter)

    root.addHandler(file_handler)
    root.addHandler(console_handler)

    root.propagate = False
    return root


def get_logger(name: str = __name__, level=logging.INFO) -> logging.Logger:
    """
    Get a named logger under the DocumentVisionX root logger.
    
    Ensures:
    - Single file handle per process
    - No handler duplication
    - Request ID included in all log records (for trace correlation)
    - Proper hierarchy for sub-loggers
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (default INFO)
    
    Returns:
        logging.Logger: Named logger under root
    """
    global _ROOT_LOGGER
    
    if _ROOT_LOGGER is None:
        with _LOGGER_LOCK:
            if _ROOT_LOGGER is None:
                _ROOT_LOGGER = _setup_root_logger()
    
    # Get or create named logger under root
    logger = _ROOT_LOGGER.getChild(name)
    logger.setLevel(level)
    
    return logger

