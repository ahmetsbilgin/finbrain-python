"""
Shared utility functions for async endpoint modules.

This module contains common helper functions used across multiple async endpoint
implementations to avoid code duplication.
"""

from __future__ import annotations
import datetime as _dt


def to_datestr(value: _dt.date | str) -> str:
    """
    Convert datetime.date to ISO format string (YYYY-MM-DD).

    If the input is already a string, it is returned unchanged.
    This allows flexible date parameter handling in API calls.

    Parameters
    ----------
    value : datetime.date or str
        Date value to convert.

    Returns
    -------
    str
        ISO format date string (YYYY-MM-DD).

    Examples
    --------
    >>> from datetime import date
    >>> to_datestr(date(2025, 1, 15))
    '2025-01-15'
    >>> to_datestr("2025-01-15")
    '2025-01-15'
    """
    return value.isoformat() if isinstance(value, _dt.date) else value
