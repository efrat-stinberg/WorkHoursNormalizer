"""
data_generator.py - Attendance Data Variation Generator
יוצר וריאציות לוגיות של נתוני נוכחות
"""

import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from copy import deepcopy
from dataclasses import asdict

logger = logging.getLogger(__name__)


class VariationLevel:
    """רמות שינוי"""
    MINIMAL = "minimal"      # שינויים קטנים מאוד (±5 דקות)
    MODERATE = "moderate"    # שינויים בינוניים (±15 דקות)
    SIGNIFICANT = "significant"  # שינויים משמעותיים (±30 דקות)


class AttendanceVariationGenerator:
    """מייצר וריאציות לוגיות של נתוני נוכחות"""

    # הגדרות זמן לפי רמת שינוי
    TIME_VARIATIONS = {
        VariationLevel.MINIMAL: {
            "start_minutes": 5,
            "end_minutes": 5,
            "break_minutes": 2
        },
        VariationLevel.MODERATE: {
            "start_minutes": 15,
            "end_minutes": 15,
            "break_minutes": 5
        },
        VariationLevel.SIGNIFICANT: {
            "start_minutes": 30,
            "end_minutes": 30,
            "break_minutes": 10
        }
    }

    def __init__(self, variation_level: str = VariationLevel.MODERATE):
        self.variation_level = variation_level
        self.config = self.TIME_VARIATIONS.get(
            variation_level,
            self.TIME_VARIATIONS[VariationLevel.MODERATE]
        )

    def generate_variation(self, parsed_report) -> Dict[str, Any]:
        """
        יצירת וריאציה של דוח מפוענח

        Args:
            parsed_report: ParsedReport מהמנתח

        Returns:
            דוח משונה עם וריאציות לוגיות
        """
        logger.info(f"Generating variation with level: {self.variation_level}")

        # העתקה עמוקה כדי לא לשנות את המקור
        varied_report = deepcopy(parsed_report)

        # שינוי הרשומות
        varied_records = []
        for record in varied_report.records:
            varied_record = self._vary_record(record)
            varied_records.append(varied_record)

        varied_report.records = varied_records

        # עדכון סיכומים
        self._recalculate_totals(varied_report)

        logger.info(f"✅ Generated variation with {len(varied_records)} records")
        return varied_report

    def _vary_record(self, record):
        """שינוי רשומה בודדת"""
        # העתקה עמוקה
        varied = deepcopy(record)

        # שינוי זמני כניסה ויציאה
        if varied.start_time:
            varied.start_time = self._vary_time(
                varied.start_time,
                self.config["start_minutes"],
                earliest="06:00",
                latest="10:00"
            )

        if varied.end_time:
            varied.end_time = self._vary_time(
                varied.end_time,
                self.config["end_minutes"],
                earliest=varied.start_time if varied.start_time else "14:00",
                latest="23:00"
            )

        # שינוי זמן הפסקה אם קיים
        if hasattr(varied, 'break_time') and varied.break_time:
            varied.break_time = self._vary_break_time(
                varied.break_time,
                self.config["break_minutes"]
            )

        # חישוב מחדש של סה"כ שעות
        if varied.start_time and varied.end_time:
            break_hours = self._time_to_hours(varied.break_time) if hasattr(varied, 'break_time') and varied.break_time else 0
            total_hours = self._calculate_hours(varied.start_time, varied.end_time, break_hours)
            varied.hours = total_hours
            varied.total = total_hours

            # עדכון אחוזים אם זה דוח מפורט
            if hasattr(varied, 'hours_100'):
                self._recalculate_percentages(varied)

        return varied

    def _vary_time(self, time_str: str, max_variation: int,
                   earliest: str = "00:00", latest: str = "23:59") -> str:
        """
        שינוי זמן בתוך טווח מותר

        Args:
            time_str: זמן בפורמט HH:MM
            max_variation: וריאציה מקסימלית בדקות
            earliest: זמן מוקדם ביותר מותר
            latest: זמן מאוחר ביותר מותר
        """
        try:
            # המרה ל-datetime
            time_obj = datetime.strptime(time_str, "%H:%M")

            # הוספת וריאציה אקראית
            variation = random.randint(-max_variation, max_variation)
            varied_time = time_obj + timedelta(minutes=variation)

            # הגבלה לטווח המותר - עבודה עם שעות ודקות בלבד
            earliest_obj = datetime.strptime(earliest, "%H:%M")
            latest_obj = datetime.strptime(latest, "%H:%M")

            # השוואה לפי שעה ודקה בלבד
            varied_hour_min = varied_time.hour * 60 + varied_time.minute
            earliest_min = earliest_obj.hour * 60 + earliest_obj.minute
            latest_min = latest_obj.hour * 60 + latest_obj.minute

            if varied_hour_min < earliest_min:
                varied_time = earliest_obj
            elif varied_hour_min > latest_min:
                varied_time = latest_obj

            return varied_time.strftime("%H:%M")

        except Exception as e:
            logger.warning(f"Could not vary time {time_str}: {e}")
            return time_str

    def _vary_break_time(self, break_time: str, max_variation: int) -> str:
        """שינוי זמן הפסקה"""
        try:
            time_obj = datetime.strptime(break_time, "%H:%M")
            variation = random.randint(-max_variation, max_variation)
            varied = time_obj + timedelta(minutes=variation)

            # הפסקה לא יכולה להיות שלילית או יותר מ-2 שעות
            if varied.hour > 2:
                varied = time_obj

            return varied.strftime("%H:%M")
        except Exception:
            return break_time

    def _calculate_hours(self, start: str, end: str, break_hours: float = 0) -> float:
        """חישוב מספר שעות עבודה"""
        try:
            start_obj = datetime.strptime(start, "%H:%M")
            end_obj = datetime.strptime(end, "%H:%M")

            # אם הסיום לפני ההתחלה, זה ככה כבר היה ביום למחרת
            if end_obj <= start_obj:
                end_obj += timedelta(days=1)

            duration = (end_obj - start_obj).total_seconds() / 3600
            net_hours = max(0, duration - break_hours)

            return round(net_hours, 2)
        except Exception as e:
            logger.warning(f"Could not calculate hours: {e}")
            return 0.0

    def _time_to_hours(self, time_str: str) -> float:
        """המרת HH:MM לשעות עשרוניות"""
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            return time_obj.hour + time_obj.minute / 60.0
        except Exception:
            return 0.0

    def _recalculate_percentages(self, record):
        """חישוב מחדש של אחוזי שעות (100%, 125%, 150%)"""
        total = record.total or 0

        # כללים פשוטים:
        # - עד 9 שעות = 100%
        # - 9-11 שעות = חלק 125%
        # - מעל 11 = חלק 150%

        if total <= 9:
            record.hours_100 = total
            record.hours_125 = 0
            record.hours_150 = 0
        elif total <= 11:
            record.hours_100 = 9
            record.hours_125 = total - 9
            record.hours_150 = 0
        else:
            record.hours_100 = 9
            record.hours_125 = 2
            record.hours_150 = total - 11

        # עיגול
        record.hours_100 = round(record.hours_100, 2)
        record.hours_125 = round(record.hours_125, 2)
        record.hours_150 = round(record.hours_150, 2)

    def _recalculate_totals(self, report):
        """עדכון סיכומי הדוח"""
        if not report.records:
            return

        # סיכום שעות
        total_hours = sum(r.hours for r in report.records if r.hours)
        report.metadata.total_hours = round(total_hours, 2)

        # עדכון שכר אם יש תעריף
        if report.metadata.hourly_rate:
            report.metadata.total_salary = round(
                report.metadata.hourly_rate * total_hours, 2
            )


def create_variation(parsed_report, variation_level: str = VariationLevel.MODERATE):
    """
    פונקציה עזר ליצירת וריאציה

    Args:
        parsed_report: ParsedReport מהמנתח
        variation_level: רמת השינוי (minimal/moderate/significant)

    Returns:
        דוח משונה
    """
    generator = AttendanceVariationGenerator(variation_level)
    return generator.generate_variation(parsed_report)


def create_multiple_variations(parsed_report, count: int = 3,
                               variation_level: str = VariationLevel.MODERATE) -> List:
    """
    יצירת מספר וריאציות

    Args:
        parsed_report: דוח מקורי
        count: מספר וריאציות
        variation_level: רמת שינוי

    Returns:
        רשימת דוחות משונים
    """
    generator = AttendanceVariationGenerator(variation_level)
    variations = []

    for i in range(count):
        logger.info(f"Creating variation {i+1}/{count}")
        varied = generator.generate_variation(parsed_report)
        variations.append(varied)

    return variations