"""
Shared utility functions for endpoint modules.

This module contains common helper functions used across multiple endpoint
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
    >>> from datetime import date, datetime
    >>> to_datestr(date(2025, 1, 15))
    '2025-01-15'
    >>> to_datestr(datetime(2025, 1, 15, 9, 30))
    '2025-01-15'
    >>> to_datestr("2025-01-15")
    '2025-01-15'
    """
    # ``datetime`` subclasses ``date``; take the date part so the time
    # component never leaks into the ``YYYY-MM-DD`` API parameter.
    if isinstance(value, _dt.datetime):
        return value.date().isoformat()
    return value.isoformat() if isinstance(value, _dt.date) else value
