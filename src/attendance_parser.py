"""
attendance_parser.py - Enhanced Attendance Report Parser
Improved parser with flexible recognition and multi-format support
"""

import re
import logging
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Report template types"""
    SIMPLE = "simple"           # Simple template - 5-7 columns
    DETAILED = "detailed"       # Detailed template - 9-11 columns
    UNKNOWN = "unknown"


@dataclass
class AttendanceRecord:
    """Basic attendance record"""
    date: str
    day_of_week: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    hours: Optional[float] = None
    total: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class DetailedAttendanceRecord(AttendanceRecord):
    """Detailed attendance record"""
    location: Optional[str] = None
    break_time: Optional[str] = None
    hours_100: Optional[float] = None  # Regular hours
    hours_125: Optional[float] = None  # 125% (evening)
    hours_150: Optional[float] = None  # 150% (night)
    saturday: Optional[float] = None   # Saturday hours


@dataclass
class ReportMetadata:
    """Report metadata"""
    employee_name: Optional[str] = None
    employee_id: Optional[str] = None
    company_name: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    total_hours: Optional[float] = None
    total_salary: Optional[float] = None
    hourly_rate: Optional[float] = None
    required_hours: Optional[float] = None
    template_type: TemplateType = TemplateType.UNKNOWN
    top_table_rows: List[str] = field(default_factory=list)


@dataclass
class ParsedReport:
    """Fully parsed report"""
    metadata: ReportMetadata
    records: List[AttendanceRecord]
    template_type: TemplateType
    raw_text: str = ""


class FlexiblePatterns:
    """Flexible regex patterns"""

    # Date - supports various formats
    DATE = r'(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})'

    # Time - HH:MM or H:MM
    TIME = r'(\d{1,2}:\d{2})'

    # Decimal number
    DECIMAL = r'([\d]+\.[\d]{1,2})'

    # Hebrew weekdays
    HEBREW_DAY = r'([א-ת]{2,6}י?\'?)'

    # English weekdays
    ENGLISH_DAY = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)'

    # Keywords for recognition
    DETAILED_KEYWORDS = [
        r'125%', r'150%', r'שבת', r'הפסקה', r'break',
        r'מקום', r'location', r'נ\.ב', r'בע[״"\']מ'
    ]

    SIMPLE_KEYWORDS = [
        r'כניסה', r'יציאה', r'התחלה', r'סיום',
        r'start', r'end', r'entry', r'exit'
    ]


class AttendanceParser:
    """Unified enhanced parser for attendance reports"""

    def __init__(self, text: str):
        self.text = self._clean_text(text)
        self.lines = [l.strip() for l in self.text.split("\n") if l.strip()]
        self.metadata = ReportMetadata()
        self.records: List[AttendanceRecord] = []

    def parse(self) -> ParsedReport:
        """Perform full report parsing"""
        logger.info("Starting enhanced attendance report parsing")

        # Identify template type
        template_type = self._identify_template()
        self.metadata.template_type = template_type
        logger.info(f"Template identified: {template_type.value}")

        # Extract metadata
        self._extract_metadata()

        # Parse records according to type
        if template_type == TemplateType.DETAILED:
            self._parse_detailed_records_flexible()
        elif template_type == TemplateType.SIMPLE:
            self._parse_simple_records_flexible()
        else:
            # Try both parsing methods
            logger.warning("Unknown template, trying flexible parsing")
            self._parse_flexible_generic()

        # Compute totals
        self._calculate_totals()

        logger.info(f"✅ Parsed {len(self.records)} records")

        return ParsedReport(
            metadata=self.metadata,
            records=self.records,
            template_type=template_type,
            raw_text=self.text
        )

    def _identify_template(self) -> TemplateType:
        """Improved template type identification"""

        # Method 1: keyword count
        detailed_count = sum(
            1 for pattern in FlexiblePatterns.DETAILED_KEYWORDS
            if re.search(pattern, self.text, re.IGNORECASE)
        )

        simple_count = sum(
            1 for pattern in FlexiblePatterns.SIMPLE_KEYWORDS
            if re.search(pattern, self.text, re.IGNORECASE)
        )

        logger.debug(f"Keyword counts - Detailed: {detailed_count}, Simple: {simple_count}")

        # Method 2: structure analysis - column count estimation
        column_count = self._estimate_column_count()
        logger.debug(f"Estimated columns: {column_count}")

        # Decision logic
        if detailed_count >= 3 or column_count >= 10:
            return TemplateType.DETAILED
        elif simple_count >= 2 or (5 <= column_count <= 7):
            return TemplateType.SIMPLE

        # Try to guess based on line patterns
        for line in self.lines[:30]:
            times = re.findall(FlexiblePatterns.TIME, line)
            decimals = re.findall(FlexiblePatterns.DECIMAL, line)

            if len(times) >= 2 and len(decimals) >= 4:
                return TemplateType.DETAILED
            elif len(times) >= 2 and len(decimals) >= 1:
                return TemplateType.SIMPLE

        return TemplateType.UNKNOWN

    def _estimate_column_count(self) -> int:
        """Estimate number of columns from first lines"""
        max_elements = 0

        for line in self.lines[:20]:
            dates = len(re.findall(FlexiblePatterns.DATE, line))
            times = len(re.findall(FlexiblePatterns.TIME, line))
            decimals = len(re.findall(FlexiblePatterns.DECIMAL, line))
            words = len([w for w in line.split() if len(w) > 1])

            elements = dates + times + decimals + min(words, 3)
            max_elements = max(max_elements, elements)

        return max_elements

    def _extract_metadata(self):
        """Enhanced metadata extraction"""
        patterns = {
            'total_hours': [
                r"(?:סה[\"']כ\s*שעות|Total\s*Hours|סך\s*הכל\s*שעות)[:\s]*([\d.]+)",
                r"(?:ימים|Days)[:\s]*(\d+)",
            ],
            'total_salary': [
                r"(?:סה[\"']כ\s*לתשלום|Total|סך\s*לתשלום)[:\s]*[₪$]?\s*([\d,]+\.?\d*)",
                r"[₪$]\s*([\d,]+\.?\d*)",
            ],
            'hourly_rate': [
                r"(?:מחיר\s*לשעה|Hourly\s*Rate|תעריף)[:\s]*[₪$]?\s*([\d.]+)",
            ],
            'required_hours': [
                r"(?:שעות\s*עבודה\s*למשרה|Required\s*Hours|שעות\s*נדרשות)[:\s]*([\d.]+)",
            ],
            'company_name': [
                r"(.*?בע[״\"'\']מ.*?)(?:\n|\s{3,})",
                r"(.*?Ltd\..*?)(?:\n|\s{3,})",
            ]
        }

        # Search in the first lines
        for line in self.lines[:25]:
            for key, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        value = match.group(1)
                        if key == 'total_hours' and not self.metadata.total_hours:
                            self.metadata.total_hours = self._safe_float(value)
                        elif key == 'total_salary' and not self.metadata.total_salary:
                            self.metadata.total_salary = self._safe_float(value.replace(",", ""))
                        elif key == 'hourly_rate' and not self.metadata.hourly_rate:
                            self.metadata.hourly_rate = self._safe_float(value)
                        elif key == 'required_hours' and not self.metadata.required_hours:
                            self.metadata.required_hours = self._safe_float(value)
                        elif key == 'company_name' and not self.metadata.company_name:
                            self.metadata.company_name = value.strip()

        self._extract_month_year()

    def _extract_month_year(self):
        """Extract month and year from dates"""
        dates = re.findall(FlexiblePatterns.DATE, self.text)
        if dates:
            try:
                first_date = dates[0]
                normalized = first_date.replace(".", "/").replace("-", "/")
                parts = normalized.split("/")

                if len(parts) == 3:
                    day, month, year = parts
                    self.metadata.month = month.zfill(2)

                    if len(year) == 2:
                        year_int = int(year)
                        if year_int > 50:
                            self.metadata.year = f"19{year}"
                        else:
                            self.metadata.year = f"20{year}"
                    else:
                        self.metadata.year = year
            except Exception as e:
                logger.debug(f"Could not parse date: {e}")

    def _parse_simple_records_flexible(self):
        """Flexible parsing for simple template"""
        self.records = []
        merged_lines = self._merge_broken_lines()

        logger.info("Parsing simple records with flexible method")

        for line in merged_lines:
            date_match = re.search(FlexiblePatterns.DATE, line)
            if not date_match:
                continue
            date = date_match.group(1)
            day = self._extract_day(line)
            times = re.findall(FlexiblePatterns.TIME, line)
            if len(times) < 2:
                continue
            start_time, end_time = times[:2]
            decimals = re.findall(FlexiblePatterns.DECIMAL, line)
            total = self._safe_float(decimals[-1]) if decimals else None

            record = AttendanceRecord(
                date=date,
                day_of_week=day,
                start_time=start_time,
                end_time=end_time,
                hours=total,
                total=total
            )

            self.records.append(record)

    def _parse_detailed_records_flexible(self):
        """Flexible parsing for detailed template"""
        self.records = []
        merged_lines = self._merge_broken_lines()

        logger.info("Parsing detailed records with flexible method")

        for line in merged_lines:
            date_match = re.search(FlexiblePatterns.DATE, line)
            if not date_match:
                continue
            date = date_match.group(1)
            day = self._extract_day(line)
            times = re.findall(FlexiblePatterns.TIME, line)
            if len(times) < 2:
                continue
            start_time, end_time = times[:2]
            break_time = times[2] if len(times) >= 3 else None
            decimals = re.findall(FlexiblePatterns.DECIMAL, line)
            location = self._extract_location(line, day)

            record = DetailedAttendanceRecord(
                date=date,
                day_of_week=day,
                location=location,
                start_time=start_time,
                end_time=end_time,
                break_time=break_time,
                total=self._safe_float(decimals[0]) if len(decimals) > 0 else None,
                hours_100=self._safe_float(decimals[1]) if len(decimals) > 1 else None,
                hours_125=self._safe_float(decimals[2]) if len(decimals) > 2 else None,
                hours_150=self._safe_float(decimals[3]) if len(decimals) > 3 else None,
                saturday=self._safe_float(decimals[4]) if len(decimals) > 4 else None,
                hours=self._safe_float(decimals[0]) if len(decimals) > 0 else None
            )

            self.records.append(record)

    def _parse_flexible_generic(self):
        """Generic fallback parsing when template type is unknown"""
        logger.info("Attempting generic flexible parsing")
        self._parse_simple_records_flexible()
        if not self.records:
            self._parse_detailed_records_flexible()

    def _extract_day(self, line: str) -> str:
        """Extract weekday from line"""
        hebrew_match = re.search(FlexiblePatterns.HEBREW_DAY, line)
        if hebrew_match:
            return hebrew_match.group(1)

        english_match = re.search(FlexiblePatterns.ENGLISH_DAY, line, re.IGNORECASE)
        if english_match:
            return english_match.group(1)
        return ""

    def _extract_location(self, line: str, day: str) -> str:
        """Extract location (usually short Hebrew word after the day)"""
        if not day:
            return ""
        day_pos = line.find(day)
        if day_pos == -1:
            return ""
        after_day = line[day_pos + len(day):].strip()
        words = after_day.split()
        if words and len(words[0]) <= 6 and not re.match(r'\d{1,2}:\d{2}', words[0]):
            return words[0]
        return ""

    def _merge_broken_lines(self) -> List[str]:
        """Merge broken lines that were split mid-row"""
        merged = []
        buffer = ""
        for line in self.lines:
            if re.match(FlexiblePatterns.DATE, line):
                if buffer:
                    merged.append(buffer.strip())
                buffer = line
            else:
                buffer += " " + line
        if buffer:
            merged.append(buffer.strip())
        return merged

    def _calculate_totals(self):
        """Compute totals if missing"""
        if not self.metadata.total_hours and self.records:
            total = sum(r.hours for r in self.records if r.hours)
            self.metadata.total_hours = round(total, 2)

        if not self.metadata.total_salary and self.metadata.hourly_rate and self.metadata.total_hours:
            self.metadata.total_salary = round(
                self.metadata.hourly_rate * self.metadata.total_hours, 2
            )

    def _clean_text(self, text: str) -> str:
        """Clean text from special characters"""
        if not text:
            return ""
        text = text.replace("\r", " ").replace("\uFEFF", "").replace("\xa0", " ")
        text = text.replace("״", '"').replace("׳", "'")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _safe_float(self, value: str, default: float = 0.0) -> float:
        """Safely convert to float"""
        if not value:
            return default
        try:
            cleaned = str(value).replace(",", "").replace(" ", "")
            return float(cleaned)
        except (ValueError, AttributeError):
            return default


def parse_attendance_report(text: str) -> ParsedReport:
    """
    Entry point for parsing attendance report text
    """
    parser = AttendanceParser(text)
    return parser.parse()
