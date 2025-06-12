"""
finbrain.exceptions
~~~~~~~~~~~~~~~~~~~

Canonical exception hierarchy for the FinBrain Python SDK.
Every public error subclasses :class:`FinBrainError`.

Docs-based mapping
------------------
400  Bad Request            → BadRequest
401  Unauthorized           → AuthenticationError
403  Forbidden              → PermissionDenied
404  Not Found              → NotFound
405  Method Not Allowed     → MethodNotAllowed
500  Internal Server Error  → ServerError
"""

from __future__ import annotations

from typing import Any, Dict, Union

__all__ = [
    "FinBrainError",
    "BadRequest",
    "AuthenticationError",
    "PermissionDenied",
    "NotFound",
    "MethodNotAllowed",
    "ServerError",
    #
    "InvalidResponse",
    "http_error_to_exception",
]

# ─────────────────────────────────────────────────────────────
# Base class
# ─────────────────────────────────────────────────────────────


class FinBrainError(Exception):
    """Root of the SDK's exception tree."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        payload: Any | None = None,
    ):
        super().__init__(message)
        self.status_code: int | None = status_code
        self.payload: Any | None = payload  # raw JSON/text for debugging


# ─────────────────────────────────────────────────────────────
# 4xx family
# ─────────────────────────────────────────────────────────────


class BadRequest(FinBrainError):
    """400 - The request is malformed or contains invalid parameters."""


class AuthenticationError(FinBrainError):
    """401 - API key missing or invalid."""


class PermissionDenied(FinBrainError):
    """403 - Authenticated, but not authorised to perform this action."""


class NotFound(FinBrainError):
    """404 - Requested data or endpoint not found."""


class MethodNotAllowed(FinBrainError):
    """405 - Endpoint exists, but the HTTP method is not supported."""


# ─────────────────────────────────────────────────────────────
# 5xx family
# ─────────────────────────────────────────────────────────────


class ServerError(FinBrainError):
    """500 - Internal error on FinBrain's side. Retrying later may help."""


# ─────────────────────────────────────────────────────────────
# Transport / decoding guard
# ─────────────────────────────────────────────────────────────


class InvalidResponse(FinBrainError):
    """Response couldn't be parsed as JSON or is missing required fields."""


# ─────────────────────────────────────────────────────────────
# Helper: map HTTP response ➜ exception
# ─────────────────────────────────────────────────────────────


def _extract_message(payload: Any, default: str) -> str:
    if isinstance(payload, dict):
        # FinBrain usually returns {"message": "..."}
        return payload.get("message", default)
    return default


def http_error_to_exception(resp) -> FinBrainError:  # expects requests.Response
    """
    Convert a non-2xx ``requests.Response`` into a typed FinBrainError.

    Usage
    -----
    >>> raise http_error_to_exception(resp)
    """
    status = resp.status_code
    try:
        payload: Union[Dict[str, Any], str] = resp.json()
    except ValueError:
        payload = resp.text

    message = _extract_message(payload, f"{status} {resp.reason}")

    if status == 400:
        return BadRequest(message, status_code=status, payload=payload)
    if status == 401:
        return AuthenticationError(message, status_code=status, payload=payload)
    if status == 403:
        return PermissionDenied(message, status_code=status, payload=payload)
    if status == 404:
        return NotFound(message, status_code=status, payload=payload)
    if status == 405:
        return MethodNotAllowed(message, status_code=status, payload=payload)
    if status == 500:
        return ServerError(message, status_code=status, payload=payload)

    # Fallback for undocumented codes (future-proofing)
    return FinBrainError(message, status_code=status, payload=payload)
