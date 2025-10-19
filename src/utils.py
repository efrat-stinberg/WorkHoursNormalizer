"""
utils.py - Utility Functions
פונקציות עזר משותפות למערכת
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# פורמטים
TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%d/%m/%Y"


def parse_time(time_str: Optional[str]) -> Optional[datetime]:
    """
    המרת מחרוזת זמן ל-datetime

    Args:
        time_str: זמן בפורמט "HH:MM"

    Returns:
        datetime או None במקרה של כשלון
    """
    if not time_str:
        return None

    if isinstance(time_str, datetime):
        return time_str

    try:
        return datetime.strptime(time_str.strip(), TIME_FORMAT)
    except Exception as e:
        logger.debug(f"Failed to parse time '{time_str}': {e}")
        return None


def time_to_str(dt: Optional[datetime]) -> str:
    """
    המרת datetime למחרוזת זמן

    Args:
        dt: datetime object

    Returns:
        מחרוזת בפורמט "HH:MM" או מחרוזת ריקה
    """
    if not dt:
        return ""
    return dt.strftime(TIME_FORMAT)


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    המרת מחרוזת תאריך ל-datetime

    Args:
        date_str: תאריך בפורמט "DD/MM/YYYY"

    Returns:
        datetime או None
    """
    if not date_str:
        return None

    # נסה פורמטים שונים
    formats = [DATE_FORMAT, "%d/%m/%y", "%d.%m.%Y", "%d-%m-%Y"]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except Exception:
            continue

    logger.debug(f"Failed to parse date '{date_str}'")
    return None


def date_to_str(dt: Optional[datetime]) -> str:
    """המרת datetime למחרוזת תאריך"""
    if not dt:
        return ""
    return dt.strftime(DATE_FORMAT)


def clamp_time(dt: datetime, earliest: str = "00:00", latest: str = "23:59") -> datetime:
    """
    הגבלת זמן לטווח מותר

    Args:
        dt: datetime להגבלה
        earliest: זמן מוקדם ביותר
        latest: זמן מאוחר ביותר

    Returns:
        datetime מוגבל
    """
    try:
        earliest_dt = datetime.strptime(earliest, TIME_FORMAT)
        latest_dt = datetime.strptime(latest, TIME_FORMAT)

        # שימוש באותו תאריך
        t = dt.replace(year=earliest_dt.year, month=earliest_dt.month, day=earliest_dt.day)

        if t < earliest_dt:
            return earliest_dt
        if t > latest_dt:
            return latest_dt
        return t
    except Exception as e:
        logger.warning(f"Time clamping failed: {e}")
        return dt


def duration_hours(start: datetime, end: datetime, break_minutes: float = 0.0) -> float:
    """
    חישוב משך זמן בשעות בין שני זמנים

    Args:
        start: זמן התחלה
        end: זמן סיום
        break_minutes: דקות הפסקה

    Returns:
        מספר שעות (עשרוני)
    """
    if not start or not end:
        return 0.0

    # אם הסיום לפני ההתחלה, נניח שזה למחרת
    if end < start:
        end = end + timedelta(days=1)

    delta_seconds = (end - start).total_seconds()
    delta_hours = delta_seconds / 3600.0

    # הפחתת הפסקה
    delta_hours -= break_minutes / 60.0

    return max(0.0, round(delta_hours, 2))


def is_weekend(date_str: str, weekend_days: tuple = (4, 5)) -> bool:
    """
    בדיקה אם תאריך הוא סוף שבוע

    Args:
        date_str: תאריך בפורמט "DD/MM/YYYY"
        weekend_days: tuple של ימים (0=ראשון, 4=שישי, 5=שבת)

    Returns:
        True אם סוף שבוע
    """
    dt = parse_date(date_str)
    if not dt:
        return False

    # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
    return dt.weekday() in weekend_days


def get_day_name_hebrew(date_str: str) -> str:
    """
    קבלת שם יום בעברית

    Args:
        date_str: תאריך

    Returns:
        שם יום בעברית
    """
    dt = parse_date(date_str)
    if not dt:
        return ""

    hebrew_days = {
        0: "שני",
        1: "שלישי",
        2: "רביעי",
        3: "חמישי",
        4: "שישי",
        5: "שבת",
        6: "ראשון"
    }

    return hebrew_days.get(dt.weekday(), "")


def sanitize_text(text: str) -> str:
    """
    ניקוי טקסט מתווים מיוחדים

    Args:
        text: טקסט לניקוי

    Returns:
        טקסט מנוקה
    """
    if not text:
        return ""

    # הסרת תווים בעייתיים
    text = text.replace("\r", " ")
    text = text.replace("\uFEFF", "")  # BOM
    text = text.replace("\xa0", " ")   # non-breaking space

    # נורמליזציה של רווחים
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def safe_float(value: Optional[str], default: float = 0.0) -> float:
    """
    המרה בטוחה למספר עשרוני

    Args:
        value: ערך להמרה
        default: ערך ברירת מחדל

    Returns:
        מספר עשרוני
    """
    if value is None:
        return default

    try:
        # טיפול בפסיקים כנקודה עשרונית
        str_value = str(value).replace(",", ".")
        return float(str_value)
    except (ValueError, AttributeError):
        return default


def safe_int(value: Optional[str], default: int = 0) -> int:
    """
    המרה בטוחה למספר שלם

    Args:
        value: ערך להמרה
        default: ערך ברירת מחדל

    Returns:
        מספר שלם
    """
    if value is None:
        return default

    try:
        return int(float(str(value).replace(",", ".")))
    except (ValueError, AttributeError):
        return default


def format_currency(amount: float, currency: str = "₪") -> str:
    """
    עיצוב סכום כספי

    Args:
        amount: סכום
        currency: סימן מטבע

    Returns:
        מחרוזת מעוצבת
    """
    return f"{currency} {amount:,.2f}"


def validate_time_range(start: str, end: str) -> bool:
    """
    ולידציה שזמן סיום אחרי זמן התחלה

    Args:
        start: זמן התחלה "HH:MM"
        end: זמן סיום "HH:MM"

    Returns:
        True אם תקין
    """
    start_dt = parse_time(start)
    end_dt = parse_time(end)

    if not start_dt or not end_dt:
        return False

    # מותר שהסיום יהיה למחרת (כלומר "לפני" ההתחלה בשעון)
    return True


def calculate_break_from_hours(work_hours: float) -> float:
    """
    חישוב הפסקה סטנדרטית לפי שעות עבודה
    (כלל אצבע: 30 דקות אחרי 6 שעות, 45 אחרי 9)

    Args:
        work_hours: שעות עבודה

    Returns:
        דקות הפסקה
    """
    if work_hours < 6:
        return 0
    elif work_hours < 9:
        return 30
    else:
        return 45


def round_to_quarter(hours: float) -> float:
    """
    עיגול לרבע שעה הקרוב

    Args:
        hours: שעות

    Returns:
        שעות מעוגלות
    """
    return round(hours * 4) / 4


def hours_to_time_string(hours: float) -> str:
    """
    המרת שעות עשרוניות למחרוזת "HH:MM"

    Args:
        hours: שעות עשרוניות (לדוגמה: 8.5)

    Returns:
        מחרוזת "HH:MM"
    """
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}"


def normalize_hebrew_text(text: str) -> str:
    """
    נורמליזציה של טקסט עברי (גרשיים, גרש)

    Args:
        text: טקסט עברי

    Returns:
        טקסט מנורמל
    """
    if not text:
        return ""

    # תחליפי גרשיים
    text = text.replace("״", '"').replace("׳", "'")
    text = text.replace("'", '"')  # גרש בודד

    return text.strip()