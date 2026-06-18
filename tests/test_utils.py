# tests/test_utils.py
import datetime as dt

from finbrain.endpoints._utils import to_datestr
from finbrain.aio.endpoints._utils import to_datestr as to_datestr_aio


def test_to_datestr_date():
    assert to_datestr(dt.date(2025, 1, 15)) == "2025-01-15"


def test_to_datestr_datetime_drops_time():
    # datetime subclasses date — the time component must not leak into the
    # YYYY-MM-DD API parameter.
    assert to_datestr(dt.datetime(2025, 1, 15, 9, 30, 45)) == "2025-01-15"


def test_to_datestr_passthrough_string():
    assert to_datestr("2025-01-15") == "2025-01-15"


def test_async_utils_is_same_callable():
    # async wrapper should re-export the canonical implementation
    assert to_datestr_aio is to_datestr
