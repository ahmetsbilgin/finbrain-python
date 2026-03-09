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
429  Rate Limit Exceeded    → RateLimitError
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
    "RateLimitError",
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
        error_code: str | None = None,
        error_details: dict | None = None,
    ):
        super().__init__(message)
        self.status_code: int | None = status_code
        self.payload: Any | None = payload  # raw JSON/text for debugging
        self.error_code: str | None = error_code
        self.error_details: dict | None = error_details


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


class RateLimitError(FinBrainError):
    """429 - Too many requests. Check X-RateLimit-* response headers."""


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
        # v2 format: {"success": false, "error": {"code": "...", "message": "..."}}
        err = payload.get("error")
        if isinstance(err, dict):
            return err.get("message", default)
        # v1 fallback: {"message": "..."}
        return payload.get("message", default)
    return default


def _extract_error_fields(payload: Any) -> tuple[str | None, dict | None]:
    """Extract error_code and error_details from v2 error envelope."""
    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict):
            return err.get("code"), err.get("details")
    return None, None


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
    error_code, error_details = _extract_error_fields(payload)
    kwargs: dict[str, Any] = dict(
        status_code=status,
        payload=payload,
        error_code=error_code,
        error_details=error_details,
    )

    if status == 400:
        return BadRequest(message, **kwargs)
    if status == 401:
        return AuthenticationError(message, **kwargs)
    if status == 403:
        return PermissionDenied(message, **kwargs)
    if status == 404:
        return NotFound(message, **kwargs)
    if status == 405:
        return MethodNotAllowed(message, **kwargs)
    if status == 429:
        return RateLimitError(message, **kwargs)
    if status == 500:
        return ServerError(message, **kwargs)

    # Fallback for undocumented codes (future-proofing)
    return FinBrainError(message, **kwargs)
