"""
Request context tracking for distributed tracing across async operations.
Provides request ID correlation for all logs, OCR, and LLM calls.
"""

import contextvars
import uuid
from typing import Optional

# Context variable for request ID (survives async context switches)
_request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    'request_id',
    default='N/A'
)


def set_request_id(request_id: Optional[str] = None) -> str:
    """
    Set the current request ID in context.
    
    If no ID provided, generates a new UUID4.
    Returns the set request ID.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]  # Short 8-char ID
    
    _request_id_var.set(request_id)
    return request_id


def get_request_id() -> str:
    """
    Get the current request ID from context.
    
    Returns:
        str: Current request ID or 'N/A' if not set
    """
    return _request_id_var.get()


def reset_request_id() -> None:
    """Reset request ID to default."""
    _request_id_var.set('N/A')
