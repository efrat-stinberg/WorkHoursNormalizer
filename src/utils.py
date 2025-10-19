"""
utils.py
פונקציות עזר משותפות למערכת:
- המרות תאריכים/שעות
- ולידציות לוגיות
- פונקציות עזר ל-RTL/עברית
"""

import random
from datetime import datetime, timedelta
from datetime import datetime, timedelta, time
from typing import Optional, Tuple
import re
import logging

logger = logging.getLogger("utils")
logger.addHandler(logging.NullHandler())

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%d/%m/%Y"

def time_to_str(dt):
    """Convert datetime to string HH:MM format."""
    return dt.strftime("%H:%M")

# def random_time_variation(time_obj, minutes_variation=15):
#     """
#     Adds a random variation of ±minutes_variation minutes to a datetime time object.
#     Keeps the result within 00:00–23:59.
#     """
#     delta = timedelta(minutes=random.randint(-minutes_variation, minutes_variation))
#     varied = time_obj + delta
#     # keep within day bounds
#     if varied.day != time_obj.day:
#         varied = time_obj.replace(hour=max(0, min(23, varied.hour)),
#                                   minute=max(0, min(59, varied.minute)))
#     return varied
def parse_time(s: Optional[str | datetime]) -> Optional[datetime]:
    """
    Parse "HH:MM" into datetime (today's date).
    If input is already datetime, return it unchanged.
    Returns None on failure.
    """
    if not s:
        return None

    # Already a datetime? Return as-is
    if isinstance(s, datetime):
        return s

    s = s.strip()
    try:
        dt = datetime.strptime(s, TIME_FORMAT)
        return dt
    except Exception:
        logger.debug("parse_time failed for: %s", s)
        return None


def time_to_str(dt: Optional[datetime]) -> str:
    """Convert datetime/time to 'HH:MM' string or empty string."""
    if not dt:
        return ""
    return dt.strftime(TIME_FORMAT)


def clamp_time(dt: datetime, earliest: str = "00:00", latest: str = "23:59") -> datetime:
    """Clamp a datetime's time component into [earliest, latest]."""
    e = datetime.strptime(earliest, TIME_FORMAT)
    l = datetime.strptime(latest, TIME_FORMAT)
    t = dt.replace(year=e.year, month=e.month, day=e.day)
    if t < e:
        return e
    if t > l:
        return l
    return t


def duration_hours(start: datetime, end: datetime, break_minutes: float = 0.0) -> float:
    """
    Return duration in hours between two datetimes minus break (minutes).
    Assumes end >= start; if not, returns 0.
    """
    if not start or not end:
        return 0.0
    delta = (end - start).total_seconds() / 3600.0
    delta -= break_minutes / 60.0
    return max(0.0, round(delta, 2))


def is_weekend(date_str: str) -> bool:
    """Given 'DD/MM/YYYY' returns True if date is Friday/Saturday/Sunday depending on locale.
    Here we check Friday/Saturday as typical Israeli weekend (Friday=4, Saturday=5)."""
    try:
        dt = datetime.strptime(date_str, DATE_FORMAT)
        return dt.weekday() in (4, 5)  # 0=Monday ... 4=Fri,5=Sat
    except Exception:
        return False


def sanitize_text(text: str) -> str:
    """Basic text cleaning: normalize whitespace, remove BOM, CRs."""
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\uFEFF", "").replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def safe_float(s: Optional[str], default: float = 0.0) -> float:
    """Convert string to float safely (handles commas)."""
    if s is None:
        return default
    try:
        s2 = str(s).replace(",", ".")
        return float(s2)
    except Exception:
        return default
