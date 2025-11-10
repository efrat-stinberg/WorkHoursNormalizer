"""
data_generator.py - Attendance Data Variation Generator
Generates logical variations of attendance data
"""

import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from copy import deepcopy
from dataclasses import asdict
from config import TIME_VARIATIONS

logger = logging.getLogger(__name__)


class VariationLevel:
    """Levels of variation"""
    MINIMAL = "minimal"       # Very small changes (±5 minutes)
    MODERATE = "moderate"     # Moderate changes (±15 minutes)
    SIGNIFICANT = "significant"  # Significant changes (±30 minutes)


class AttendanceVariationGenerator:
    """Generates logical variations of attendance data"""

    TIME_VARIATIONS = TIME_VARIATIONS

    def __init__(self, variation_level: str = VariationLevel.MODERATE):
        self.variation_level = variation_level
        self.config = self.TIME_VARIATIONS.get(
            variation_level,
            self.TIME_VARIATIONS[VariationLevel.MODERATE]
        )

    def generate_variation(self, parsed_report) -> Dict[str, Any]:
        """
        Generate a variation of a parsed report

        Args:
            parsed_report: ParsedReport object from parser

        Returns:
            Modified report with logical variations
        """
        logger.info(f"Generating variation with level: {self.variation_level}")

        # Deep copy to avoid modifying the original
        varied_report = deepcopy(parsed_report)

        # Modify each record
        varied_records = []
        for record in varied_report.records:
            varied_record = self._vary_record(record)
            varied_records.append(varied_record)

        varied_report.records = varied_records

        # Update totals
        self._recalculate_totals(varied_report)

        logger.info(f"✅ Generated variation with {len(varied_records)} records")
        return varied_report

    def _vary_record(self, record):
        """Modify a single record"""
        varied = deepcopy(record)

        # Modify start and end times
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

        # Modify break time if present
        if hasattr(varied, 'break_time') and varied.break_time:
            varied.break_time = self._vary_break_time(
                varied.break_time,
                self.config["break_minutes"]
            )

        # Recalculate total hours
        if varied.start_time and varied.end_time:
            break_hours = self._time_to_hours(varied.break_time) if hasattr(varied, 'break_time') and varied.break_time else 0
            total_hours = self._calculate_hours(varied.start_time, varied.end_time, break_hours)
            varied.hours = total_hours
            varied.total = total_hours

            # Update overtime percentages if detailed report
            if hasattr(varied, 'hours_100'):
                self._recalculate_percentages(varied)

        return varied

    def _vary_time(self, time_str: str, max_variation: int,
                   earliest: str = "00:00", latest: str = "23:59") -> str:
        """
        Vary time within allowed range

        Args:
            time_str: Time in HH:MM format
            max_variation: Maximum variation in minutes
            earliest: Earliest allowed time
            latest: Latest allowed time
        """
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")

            # Add random variation
            variation = random.randint(-max_variation, max_variation)
            varied_time = time_obj + timedelta(minutes=variation)

            # Keep within allowed range
            earliest_obj = datetime.strptime(earliest, "%H:%M")
            latest_obj = datetime.strptime(latest, "%H:%M")

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
        """Modify break time"""
        try:
            time_obj = datetime.strptime(break_time, "%H:%M")
            variation = random.randint(-max_variation, max_variation)
            varied = time_obj + timedelta(minutes=variation)

            # Break cannot be negative or longer than 2 hours
            if varied.hour > 2:
                varied = time_obj

            return varied.strftime("%H:%M")
        except Exception:
            return break_time

    def _calculate_hours(self, start: str, end: str, break_hours: float = 0) -> float:
        """Calculate number of working hours"""
        try:
            start_obj = datetime.strptime(start, "%H:%M")
            end_obj = datetime.strptime(end, "%H:%M")

            # If end time is earlier than start, it means it passed midnight
            if end_obj <= start_obj:
                end_obj += timedelta(days=1)

            duration = (end_obj - start_obj).total_seconds() / 3600
            net_hours = max(0, duration - break_hours)

            return round(net_hours, 2)
        except Exception as e:
            logger.warning(f"Could not calculate hours: {e}")
            return 0.0

    def _time_to_hours(self, time_str: str) -> float:
        """Convert HH:MM to decimal hours"""
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            return time_obj.hour + time_obj.minute / 60.0
        except Exception:
            return 0.0

    def _recalculate_percentages(self, record):
        """Recalculate overtime percentages (100%, 125%, 150%)"""
        total = record.total or 0

        # Simple logic:
        # - Up to 9 hours = 100%
        # - 9–11 hours = 125%
        # - Above 11 = 150%
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

        record.hours_100 = round(record.hours_100, 2)
        record.hours_125 = round(record.hours_125, 2)
        record.hours_150 = round(record.hours_150, 2)

    def _recalculate_totals(self, report):
        """Update report totals"""
        if not report.records:
            return

        total_hours = sum(r.hours for r in report.records if r.hours)
        report.metadata.total_hours = round(total_hours, 2)

        if report.metadata.hourly_rate:
            report.metadata.total_salary = round(
                report.metadata.hourly_rate * total_hours, 2
            )


def create_variation(parsed_report, variation_level: str = VariationLevel.MODERATE):
    """
    Helper function to create a single variation

    Args:
        parsed_report: ParsedReport from parser
        variation_level: Level of variation (minimal/moderate/significant)

    Returns:
        Modified report
    """
    generator = AttendanceVariationGenerator(variation_level)
    return generator.generate_variation(parsed_report)

