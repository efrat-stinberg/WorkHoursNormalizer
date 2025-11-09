# """
# utils.py - Utility Functions
# Common helper functions for the system
# """
#
# import re
# import logging
# from datetime import datetime, timedelta
# from typing import Optional
#
# logger = logging.getLogger(__name__)
#
# # Formats
# TIME_FORMAT = "%H:%M"
# DATE_FORMAT = "%d/%m/%Y"
#
#
# def parse_time(time_str: Optional[str]) -> Optional[datetime]:
#     """
#     Convert a time string to a datetime object.
#
#     Args:
#         time_str: Time string in "HH:MM" format.
#
#     Returns:
#         datetime object or None if parsing fails.
#     """
#     if not time_str:
#         return None
#
#     if isinstance(time_str, datetime):
#         return time_str
#
#     try:
#         return datetime.strptime(time_str.strip(), TIME_FORMAT)
#     except Exception as e:
#         logger.debug(f"Failed to parse time '{time_str}': {e}")
#         return None
#
#
# def time_to_str(dt: Optional[datetime]) -> str:
#     """
#     Convert a datetime object to a time string.
#
#     Args:
#         dt: datetime object.
#
#     Returns:
#         String in "HH:MM" format or empty string if None.
#     """
#     if not dt:
#         return ""
#     return dt.strftime(TIME_FORMAT)
#
#
# def parse_date(date_str: Optional[str]) -> Optional[datetime]:
#     """
#     Convert a date string to a datetime object.
#
#     Args:
#         date_str: Date string in "DD/MM/YYYY" format.
#
#     Returns:
#         datetime object or None if parsing fails.
#     """
#     if not date_str:
#         return None
#
#     # Try multiple formats
#     formats = [DATE_FORMAT, "%d/%m/%y", "%d.%m.%Y", "%d-%m-%Y"]
#
#     for fmt in formats:
#         try:
#             return datetime.strptime(date_str.strip(), fmt)
#         except Exception:
#             continue
#
#     logger.debug(f"Failed to parse date '{date_str}'")
#     return None
#
#
# def date_to_str(dt: Optional[datetime]) -> str:
#     """Convert datetime to a date string."""
#     if not dt:
#         return ""
#     return dt.strftime(DATE_FORMAT)
#
#
# def clamp_time(dt: datetime, earliest: str = "00:00", latest: str = "23:59") -> datetime:
#     """
#     Clamp a datetime to a specified allowed range.
#
#     Args:
#         dt: datetime to clamp.
#         earliest: earliest allowed time.
#         latest: latest allowed time.
#
#     Returns:
#         Clamped datetime object.
#     """
#     try:
#         earliest_dt = datetime.strptime(earliest, TIME_FORMAT)
#         latest_dt = datetime.strptime(latest, TIME_FORMAT)
#
#         # Use the same date
#         t = dt.replace(year=earliest_dt.year, month=earliest_dt.month, day=earliest_dt.day)
#
#         if t < earliest_dt:
#             return earliest_dt
#         if t > latest_dt:
#             return latest_dt
#         return t
#     except Exception as e:
#         logger.warning(f"Time clamping failed: {e}")
#         return dt
#
#
# def duration_hours(start: datetime, end: datetime, break_minutes: float = 0.0) -> float:
#     """
#     Calculate duration in hours between two times.
#
#     Args:
#         start: Start time.
#         end: End time.
#         break_minutes: Break duration in minutes.
#
#     Returns:
#         Number of hours (decimal).
#     """
#     if not start or not end:
#         return 0.0
#
#     # If end is before start, assume it's next day
#     if end < start:
#         end = end + timedelta(days=1)
#
#     delta_seconds = (end - start).total_seconds()
#     delta_hours = delta_seconds / 3600.0
#
#     # Subtract break
#     delta_hours -= break_minutes / 60.0
#
#     return max(0.0, round(delta_hours, 2))
#
#
# def is_weekend(date_str: str, weekend_days: tuple = (4, 5)) -> bool:
#     """
#     Check if a date falls on a weekend.
#
#     Args:
#         date_str: Date string in "DD/MM/YYYY" format.
#         weekend_days: Tuple of weekend day numbers (0=Monday, 4=Friday, 5=Saturday).
#
#     Returns:
#         True if the date is a weekend.
#     """
#     dt = parse_date(date_str)
#     if not dt:
#         return False
#
#     return dt.weekday() in weekend_days
#
#
# def get_day_name_hebrew(date_str: str) -> str:
#     """
#     Get the name of the day in Hebrew.
#
#     Args:
#         date_str: Date string.
#
#     Returns:
#         Day name in Hebrew.
#     """
#     dt = parse_date(date_str)
#     if not dt:
#         return ""
#
#     hebrew_days = {
#         0: "שני",
#         1: "שלישי",
#         2: "רביעי",
#         3: "חמישי",
#         4: "שישי",
#         5: "שבת",
#         6: "ראשון"
#     }
#
#     return hebrew_days.get(dt.weekday(), "")
#
#
# def sanitize_text(text: str) -> str:
#     """
#     Clean text from special characters.
#
#     Args:
#         text: Text to clean.
#
#     Returns:
#         Cleaned text.
#     """
#     if not text:
#         return ""
#
#     # Remove problematic characters
#     text = text.replace("\r", " ")
#     text = text.replace("\uFEFF", "")  # BOM
#     text = text.replace("\xa0", " ")   # non-breaking space
#
#     # Normalize spaces
#     text = re.sub(r"[ \t]+", " ", text)
#     text = re.sub(r"\n{3,}", "\n\n", text)
#
#     return text.strip()
#
#
# def safe_float(value: Optional[str], default: float = 0.0) -> float:
#     """
#     Safely convert a value to float.
#
#     Args:
#         value: Value to convert.
#         default: Default value if conversion fails.
#
#     Returns:
#         Float number.
#     """
#     if value is None:
#         return default
#
#     try:
#         # Handle comma as decimal point
#         str_value = str(value).replace(",", ".")
#         return float(str_value)
#     except (ValueError, AttributeError):
#         return default
#
#
# def safe_int(value: Optional[str], default: int = 0) -> int:
#     """
#     Safely convert a value to integer.
#
#     Args:
#         value: Value to convert.
#         default: Default value if conversion fails.
#
#     Returns:
#         Integer number.
#     """
#     if value is None:
#         return default
#
#     try:
#         return int(float(str(value).replace(",", ".")))
#     except (ValueError, AttributeError):
#         return default
#
#
# def format_currency(amount: float, currency: str = "₪") -> str:
#     """
#     Format a monetary amount.
#
#     Args:
#         amount: Amount.
#         currency: Currency symbol.
#
#     Returns:
#         Formatted string.
#     """
#     return f"{currency} {amount:,.2f}"
#
#
# def validate_time_range(start: str, end: str) -> bool:
#     """
#     Validate that end time is after start time.
#
#     Args:
#         start: Start time "HH:MM".
#         end: End time "HH:MM".
#
#     Returns:
#         True if valid.
#     """
#     start_dt = parse_time(start)
#     end_dt = parse_time(end)
#
#     if not start_dt or not end_dt:
#         return False
#
#     # It is allowed for end to be the next day
#     return True
#
#
# def calculate_break_from_hours(work_hours: float) -> float:
#     """
#     Calculate standard break based on work hours.
#     (Rule of thumb: 30 minutes after 6 hours, 45 after 9 hours)
#
#     Args:
#         work_hours: Number of work hours.
#
#     Returns:
#         Break duration in minutes.
#     """
#     if work_hours < 6:
#         return 0
#     elif work_hours < 9:
#         return 30
#     else:
#         return 45
#
#
# def round_to_quarter(hours: float) -> float:
#     """
#     Round hours to the nearest quarter.
#
#     Args:
#         hours: Number of hours.
#
#     Returns:
#         Rounded hours.
#     """
#     return round(hours * 4) / 4
#
#
# def hours_to_time_string(hours: float) -> str:
#     """
#     Convert decimal hours to "HH:MM" string.
#
#     Args:
#         hours: Decimal hours (e.g., 8.5).
#
#     Returns:
#         "HH:MM" string.
#     """
#     total_minutes = int(hours * 60)
#     h = total_minutes // 60
#     m = total_minutes % 60
#     return f"{h:02d}:{m:02d}"
#
#
# def normalize_hebrew_text(text: str) -> str:
#     """
#     Normalize Hebrew text (quotes, apostrophes).
#
#     Args:
#         text: Hebrew text.
#
#     Returns:
#         Normalized text.
#     """
#     if not text:
#         return ""
#
#     # Replace quotation marks
#     text = text.replace("״", '"').replace("׳", "'")
#     text = text.replace("'", '"')  # Single quote
#
#     return text.strip()
