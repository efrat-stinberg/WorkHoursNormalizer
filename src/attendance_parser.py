"""
attendance_parser.py - Unified Attendance Report Parser
מאחד את analyzer.py ו-attendance_parser.py המקורי
"""

import re
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """סוגי תבניות דוח"""
    SIMPLE = "simple"           # תבנית פשוטה - תאריך, יום, כניסה, יציאה, סה"כ
    DETAILED = "detailed"       # תבנית מפורטת - עם אחוזי שעות, הפסקות, מיקום
    UNKNOWN = "unknown"


@dataclass
class AttendanceRecord:
    """רשומת נוכחות בסיסית"""
    date: str
    day_of_week: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    hours: Optional[float] = None
    total: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class DetailedAttendanceRecord(AttendanceRecord):
    """רשומת נוכחות מפורטת"""
    location: Optional[str] = None
    break_time: Optional[str] = None
    hours_100: Optional[float] = None  # שעות רגילות
    hours_125: Optional[float] = None  # 125% (ערב)
    hours_150: Optional[float] = None  # 150% (לילה)
    saturday: Optional[float] = None   # שעות שבת


@dataclass
class ReportMetadata:
    """מטא-דאטה של הדוח"""
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


@dataclass
class ParsedReport:
    """דוח מפוענח מלא"""
    metadata: ReportMetadata
    records: List[AttendanceRecord]
    template_type: TemplateType
    raw_text: str = ""


class AttendanceParser:
    """מנתח מאוחד לדוחות נוכחות"""

    # תבניות regex לזיהוי
    PATTERNS = {
        # תבניות תאריך
        "date": r"(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4})",

        # תבנית פשוטה: תאריך יום כניסה יציאה סה"כ
        "simple_row": r"(\d{1,2}/\d{1,2}/\d{2,4})\s+([א-ת\w]+)\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})\s+([\d.]+)",

        # תבנית מפורטת: תאריך יום מקום כניסה יציאה הפסקה סה"כ 100% 125% 150% שבת
        "detailed_row": r"(\d{2}/\d{2}/\d{4})\s+([א-ת\s]+?)\s+([א-ת]+)\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",

        # מילות מפתח
        "total_hours": r"(?:סה[\"']כ\s*שעות|Total\s*Hours)[:\s]*([\d.]+)",
        "total_salary": r"(?:סה[\"']כ\s*לתשלום|Total)[:\s]*[₪$]?\s*([\d,]+\.?\d*)",
        "hourly_rate": r"(?:מחיר\s*לשעה|Hourly\s*Rate)[:\s]*[₪$]?\s*([\d.]+)",
        "required_hours": r"(?:שעות\s*עבודה\s*למשרה|Required\s*Hours)[:\s]*([\d.]+)",
    }

    # מילות מפתח לזיהוי תבניות
    TEMPLATE_KEYWORDS = {
        TemplateType.DETAILED: [
            "נ.ב", "בע\"מ", "125%", "150%", "שבת", "מיקום", "הפסקה"
        ],
        TemplateType.SIMPLE: [
            "כניסה", "יציאה", "סה\"כ", "שעות עבודה"
        ]
    }

    def __init__(self, text: str):
        self.text = self._clean_text(text)
        self.lines = [l.strip() for l in self.text.split("\n") if l.strip()]
        self.metadata = ReportMetadata()
        self.records: List[AttendanceRecord] = []

    def parse(self) -> ParsedReport:
        """פרסור מלא של הדוח"""
        logger.info("Starting attendance report parsing")

        # זיהוי סוג תבנית
        template_type = self._identify_template()
        self.metadata.template_type = template_type

        # חילוץ מטא-דאטה
        self._extract_metadata()

        # פרסור רשומות לפי סוג
        if template_type == TemplateType.DETAILED:
            self._parse_detailed_records()
        elif template_type == TemplateType.SIMPLE:
            self._parse_simple_records()
        else:
            # נסה את שתי השיטות
            logger.warning("Unknown template, trying both methods")
            self._parse_simple_records()
            if not self.records:
                self._parse_detailed_records()

        # חישוב סיכומים
        self._calculate_totals()

        logger.info(f"✅ Parsed {len(self.records)} records, template: {template_type.value}")

        return ParsedReport(
            metadata=self.metadata,
            records=self.records,
            template_type=template_type,
            raw_text=self.text
        )

    def _identify_template(self) -> TemplateType:
        """זיהוי אוטומטי של סוג התבנית"""
        text_lower = self.text.lower()

        # ספירת מילות מפתח
        detailed_score = sum(
            1 for kw in self.TEMPLATE_KEYWORDS[TemplateType.DETAILED]
            if kw.lower() in text_lower
        )

        simple_score = sum(
            1 for kw in self.TEMPLATE_KEYWORDS[TemplateType.SIMPLE]
            if kw.lower() in text_lower
        )

        # בדיקה אם יש עמודות עם אחוזים
        has_percentages = bool(re.search(r"(100%|125%|150%)", self.text))

        if detailed_score >= 3 or has_percentages:
            return TemplateType.DETAILED
        elif simple_score >= 2:
            return TemplateType.SIMPLE

        # ניסיון זיהוי לפי מבנה שורה
        for line in self.lines[:30]:
            if re.search(self.PATTERNS["detailed_row"], line):
                return TemplateType.DETAILED
            if re.search(self.PATTERNS["simple_row"], line):
                return TemplateType.SIMPLE

        return TemplateType.UNKNOWN

    def _extract_metadata(self):
        """חילוץ מטא-דאטה מהכותרת"""
        # חיפוש בשורות הראשונות
        for line in self.lines[:20]:
            # שם חברה / עובד
            if any(word in line for word in ["בע\"מ", "בע״מ", "Ltd", "Inc"]):
                self.metadata.company_name = line.strip()

            # סה"כ שעות
            match = re.search(self.PATTERNS["total_hours"], line)
            if match:
                self.metadata.total_hours = self._safe_float(match.group(1))

            # סכום לתשלום
            match = re.search(self.PATTERNS["total_salary"], line)
            if match:
                self.metadata.total_salary = self._safe_float(match.group(1).replace(",", ""))

            # מחיר לשעה
            match = re.search(self.PATTERNS["hourly_rate"], line)
            if match:
                self.metadata.hourly_rate = self._safe_float(match.group(1))

            # שעות נדרשות
            match = re.search(self.PATTERNS["required_hours"], line)
            if match:
                self.metadata.required_hours = self._safe_float(match.group(1))

        # ניחוש חודש ושנה מהתאריכים
        dates = re.findall(self.PATTERNS["date"], self.text)
        if dates:
            try:
                first_date = dates[0].replace(".", "/").replace("-", "/")
                parts = first_date.split("/")
                if len(parts) == 3:
                    self.metadata.month = parts[1]
                    self.metadata.year = parts[2] if len(parts[2]) == 4 else f"20{parts[2]}"
            except Exception as e:
                logger.debug(f"Could not parse date: {e}")

    def _parse_simple_records(self):
        """פרסור תבנית פשוטה"""
        self.records = []

        # מיזוג שורות שנשברו
        merged_lines = self._merge_broken_lines()

        for line in merged_lines:
            match = re.search(self.PATTERNS["simple_row"], line)
            if match:
                try:
                    record = AttendanceRecord(
                        date=match.group(1),
                        day_of_week=match.group(2),
                        start_time=match.group(3),
                        end_time=match.group(4),
                        hours=self._safe_float(match.group(5)),
                        total=self._safe_float(match.group(5))
                    )
                    self.records.append(record)
                except Exception as e:
                    logger.debug(f"Failed to parse simple record: {e}")
                    continue

        logger.info(f"Parsed {len(self.records)} simple records")

    def _parse_detailed_records(self):
        """פרסור תבנית מפורטת"""
        self.records = []

        # מיזוג שורות שנשברו
        merged_lines = self._merge_broken_lines()

        for line in merged_lines:
            match = re.search(self.PATTERNS["detailed_row"], line)
            if match:
                try:
                    record = DetailedAttendanceRecord(
                        date=match.group(1),
                        day_of_week=match.group(2).strip(),
                        location=match.group(3),
                        start_time=match.group(4),
                        end_time=match.group(5),
                        break_time=match.group(6),
                        total=self._safe_float(match.group(7)),
                        hours_100=self._safe_float(match.group(8)),
                        hours_125=self._safe_float(match.group(9)),
                        hours_150=self._safe_float(match.group(10)),
                        saturday=self._safe_float(match.group(11)),
                        hours=self._safe_float(match.group(7))
                    )
                    self.records.append(record)
                except Exception as e:
                    logger.debug(f"Failed to parse detailed record: {e}")
                    continue

        logger.info(f"Parsed {len(self.records)} detailed records")

    def _merge_broken_lines(self) -> List[str]:
        """מיזוג שורות שנשברו באמצע"""
        merged = []
        buffer = ""

        for line in self.lines:
            # בדיקה אם השורה מתחילה בתאריך
            if re.match(r"^\d{1,2}[\/\.-]\d{1,2}", line):
                if buffer:
                    merged.append(buffer.strip())
                buffer = line
            else:
                # המשך של שורה קודמת
                buffer += " " + line

        if buffer:
            merged.append(buffer.strip())

        return merged

    def _calculate_totals(self):
        """חישוב סיכומים אם לא נמצאו בטקסט"""
        if not self.metadata.total_hours and self.records:
            total = sum(r.hours for r in self.records if r.hours)
            self.metadata.total_hours = round(total, 2)

        # חישוב שכר אם יש תעריף
        if not self.metadata.total_salary and self.metadata.hourly_rate and self.metadata.total_hours:
            self.metadata.total_salary = round(
                self.metadata.hourly_rate * self.metadata.total_hours, 2
            )

    def _clean_text(self, text: str) -> str:
        """ניקוי טקסט מתווים מיוחדים"""
        if not text:
            return ""

        text = text.replace("\r", " ").replace("\uFEFF", "").replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _safe_float(self, value: str, default: float = 0.0) -> float:
        """המרה בטוחה למספר"""
        if not value:
            return default
        try:
            return float(value.replace(",", "."))
        except (ValueError, AttributeError):
            return default


def parse_attendance_report(text: str) -> ParsedReport:
    """
    פונקציה עזר לפרסור דוח נוכחות

    Args:
        text: טקסט הדוח

    Returns:
        ParsedReport עם כל הנתונים
    """
    parser = AttendanceParser(text)
    return parser.parse()