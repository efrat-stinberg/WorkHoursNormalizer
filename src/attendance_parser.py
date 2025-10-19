"""
attendance_parser.py - Enhanced Attendance Report Parser
פרסור משופר עם זיהוי גמיש ותמיכה בפורמטים שונים
"""

import re
import logging
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """סוגי תבניות דוח"""
    SIMPLE = "simple"           # תבנית פשוטה - 5-7 עמודות
    DETAILED = "detailed"       # תבנית מפורטת - 9-11 עמודות
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
    top_table_rows: List[str] = field(default_factory=list)


@dataclass
class ParsedReport:
    """דוח מפוענח מלא"""
    metadata: ReportMetadata
    records: List[AttendanceRecord]
    template_type: TemplateType
    raw_text: str = ""


class FlexiblePatterns:
    """תבניות regex גמישות"""

    # תאריכים - תומך בפורמטים שונים
    DATE = r'(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})'

    # זמן - HH:MM או H:MM
    TIME = r'(\d{1,2}:\d{2})'

    # מספר עשרוני
    DECIMAL = r'([\d]+\.[\d]{1,2})'

    # ימים בעברית
    HEBREW_DAY = r'([א-ת]{2,6}י?\'?)'

    # ימים באנגלית
    ENGLISH_DAY = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)'

    # מילות מפתח לזיהוי
    DETAILED_KEYWORDS = [
        r'125%', r'150%', r'שבת', r'הפסקה', r'break',
        r'מקום', r'location', r'נ\.ב', r'בע[״"\']מ'
    ]

    SIMPLE_KEYWORDS = [
        r'כניסה', r'יציאה', r'התחלה', r'סיום',
        r'start', r'end', r'entry', r'exit'
    ]


class AttendanceParser:
    """מנתח מאוחד משופר לדוחות נוכחות"""

    def __init__(self, text: str):
        self.text = self._clean_text(text)
        self.lines = [l.strip() for l in self.text.split("\n") if l.strip()]
        self.metadata = ReportMetadata()
        self.records: List[AttendanceRecord] = []

    def parse(self) -> ParsedReport:
        """פרסור מלא של הדוח"""
        logger.info("Starting enhanced attendance report parsing")

        # זיהוי סוג תבנית
        template_type = self._identify_template()
        self.metadata.template_type = template_type
        logger.info(f"Template identified: {template_type.value}")

        # חילוץ מטא-דאטה
        self._extract_metadata()

        # פרסור רשומות לפי סוג
        if template_type == TemplateType.DETAILED:
            self._parse_detailed_records_flexible()
        elif template_type == TemplateType.SIMPLE:
            self._parse_simple_records_flexible()
        else:
            # נסה את שתי השיטות
            logger.warning("Unknown template, trying flexible parsing")
            self._parse_flexible_generic()

        # חישוב סיכומים
        self._calculate_totals()

        logger.info(f"✅ Parsed {len(self.records)} records")

        return ParsedReport(
            metadata=self.metadata,
            records=self.records,
            template_type=template_type,
            raw_text=self.text
        )

    def _identify_template(self) -> TemplateType:
        """זיהוי משופר של סוג התבנית"""

        # שיטה 1: ספירת מילות מפתח
        detailed_count = sum(
            1 for pattern in FlexiblePatterns.DETAILED_KEYWORDS
            if re.search(pattern, self.text, re.IGNORECASE)
        )

        simple_count = sum(
            1 for pattern in FlexiblePatterns.SIMPLE_KEYWORDS
            if re.search(pattern, self.text, re.IGNORECASE)
        )

        logger.debug(f"Keyword counts - Detailed: {detailed_count}, Simple: {simple_count}")

        # שיטה 2: ניתוח מבנה - ספירת עמודות
        column_count = self._estimate_column_count()
        logger.debug(f"Estimated columns: {column_count}")

        # החלטה
        if detailed_count >= 3 or column_count >= 10:
            return TemplateType.DETAILED
        elif simple_count >= 2 or (5 <= column_count <= 7):
            return TemplateType.SIMPLE

        # ניסיון זיהוי לפי מבנה שורה
        for line in self.lines[:30]:
            # ספירת זמנים ומספרים בשורה
            times = re.findall(FlexiblePatterns.TIME, line)
            decimals = re.findall(FlexiblePatterns.DECIMAL, line)

            if len(times) >= 2 and len(decimals) >= 4:
                return TemplateType.DETAILED
            elif len(times) >= 2 and len(decimals) >= 1:
                return TemplateType.SIMPLE

        return TemplateType.UNKNOWN

    def _estimate_column_count(self) -> int:
        """הערכת מספר עמודות מהשורה הראשונה"""
        # מצא שורה עם הכי הרבה מרכיבים
        max_elements = 0

        for line in self.lines[:20]:
            # ספור תאריכים, זמנים, מספרים
            dates = len(re.findall(FlexiblePatterns.DATE, line))
            times = len(re.findall(FlexiblePatterns.TIME, line))
            decimals = len(re.findall(FlexiblePatterns.DECIMAL, line))
            words = len([w for w in line.split() if len(w) > 1])

            # הערכה: תאריך + זמנים + מספרים + כמה מילים
            elements = dates + times + decimals + min(words, 3)
            max_elements = max(max_elements, elements)

        return max_elements

    def _extract_metadata(self):
        """חילוץ מטא-דאטה משופר"""

        # תבניות חיפוש משופרות
        patterns = {
            'total_hours': [
                r"(?:סה[\"']כ\s*שעות|Total\s*Hours|סך\s*הכל\s*שעות)[:\s]*([\d.]+)",
                r"(?:ימים|Days)[:\s]*(\d+)",  # fallback
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

        # חיפוש בשורות הראשונות
        for line in self.lines[:25]:
            # סה"כ שעות
            for pattern in patterns['total_hours']:
                match = re.search(pattern, line, re.IGNORECASE)
                if match and not self.metadata.total_hours:
                    self.metadata.total_hours = self._safe_float(match.group(1))
                    logger.debug(f"Found total_hours: {self.metadata.total_hours}")

            # סכום לתשלום
            for pattern in patterns['total_salary']:
                match = re.search(pattern, line, re.IGNORECASE)
                if match and not self.metadata.total_salary:
                    self.metadata.total_salary = self._safe_float(match.group(1).replace(",", ""))
                    logger.debug(f"Found total_salary: {self.metadata.total_salary}")

            # מחיר לשעה
            for pattern in patterns['hourly_rate']:
                match = re.search(pattern, line, re.IGNORECASE)
                if match and not self.metadata.hourly_rate:
                    self.metadata.hourly_rate = self._safe_float(match.group(1))
                    logger.debug(f"Found hourly_rate: {self.metadata.hourly_rate}")

            # שעות נדרשות
            for pattern in patterns['required_hours']:
                match = re.search(pattern, line, re.IGNORECASE)
                if match and not self.metadata.required_hours:
                    self.metadata.required_hours = self._safe_float(match.group(1))

            # שם חברה
            for pattern in patterns['company_name']:
                match = re.search(pattern, line)
                if match and not self.metadata.company_name:
                    self.metadata.company_name = match.group(1).strip()
                    logger.debug(f"Found company: {self.metadata.company_name}")

        # ניחוש חודש ושנה מהתאריכים
        self._extract_month_year()

    def _extract_month_year(self):
        """חילוץ חודש ושנה מהתאריכים"""
        dates = re.findall(FlexiblePatterns.DATE, self.text)
        if dates:
            try:
                first_date = dates[0]
                # נורמליזציה - החלף . ו- ב-/
                normalized = first_date.replace(".", "/").replace("-", "/")
                parts = normalized.split("/")

                if len(parts) == 3:
                    day, month, year = parts
                    self.metadata.month = month.zfill(2)

                    # תיקון שנה
                    if len(year) == 2:
                        year_int = int(year)
                        if year_int > 50:
                            self.metadata.year = f"19{year}"
                        else:
                            self.metadata.year = f"20{year}"
                    else:
                        self.metadata.year = year

                    logger.debug(f"Extracted date: {self.metadata.month}/{self.metadata.year}")
            except Exception as e:
                logger.debug(f"Could not parse date: {e}")

    def _parse_simple_records_flexible(self):
        """פרסור גמיש לתבנית פשוטה"""
        self.records = []
        merged_lines = self._merge_broken_lines()

        logger.info("Parsing simple records with flexible method")

        for line in merged_lines:
            # שלב 1: מצא תאריך
            date_match = re.search(FlexiblePatterns.DATE, line)
            if not date_match:
                continue

            date = date_match.group(1)

            # שלב 2: מצא יום
            day = self._extract_day(line)

            # שלב 3: מצא זמנים (כניסה, יציאה)
            times = re.findall(FlexiblePatterns.TIME, line)
            if len(times) < 2:
                logger.debug(f"Skipping line - not enough times: {line[:50]}")
                continue

            start_time = times[0]
            end_time = times[1]

            # שלב 4: מצא סה"כ שעות (המספר האחרון)
            decimals = re.findall(FlexiblePatterns.DECIMAL, line)
            total = self._safe_float(decimals[-1]) if decimals else None

            # יצירת רשומה
            record = AttendanceRecord(
                date=date,
                day_of_week=day,
                start_time=start_time,
                end_time=end_time,
                hours=total,
                total=total
            )

            self.records.append(record)
            logger.debug(f"Parsed simple: {date} {day} {start_time}-{end_time} = {total}h")

        logger.info(f"✓ Parsed {len(self.records)} simple records")

    def _parse_detailed_records_flexible(self):
        """פרסור גמיש לתבנית מפורטת"""
        self.records = []
        merged_lines = self._merge_broken_lines()

        logger.info("Parsing detailed records with flexible method")

        for line in merged_lines:
            # שלב 1: תאריך
            date_match = re.search(FlexiblePatterns.DATE, line)
            if not date_match:
                continue

            date = date_match.group(1)

            # שלב 2: יום
            day = self._extract_day(line)

            # שלב 3: כל הזמנים בשורה
            times = re.findall(FlexiblePatterns.TIME, line)
            if len(times) < 2:
                continue

            # בתבנית מפורטת: כניסה, יציאה, הפסקה (אם יש 3 זמנים)
            start_time = times[0]
            end_time = times[1]
            break_time = times[2] if len(times) >= 3 else None

            # שלב 4: כל המספרים
            decimals = re.findall(FlexiblePatterns.DECIMAL, line)

            # שלב 5: מיקום (מילה עברית אחרי היום)
            location = self._extract_location(line, day)

            # שלב 6: יצירת רשומה מפורטת
            # בדרך כלל: סה"כ, 100%, 125%, 150%, שבת
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
            logger.debug(f"Parsed detailed: {date} {day} {start_time}-{end_time} = {record.total}h")

        logger.info(f"✓ Parsed {len(self.records)} detailed records")

    def _parse_flexible_generic(self):
        """פרסור גנרי כשלא ידוע סוג התבנית"""
        logger.info("Attempting generic flexible parsing")

        # נסה פשוט קודם
        self._parse_simple_records_flexible()

        if not self.records:
            # נסה מפורט
            self._parse_detailed_records_flexible()

        if not self.records:
            logger.warning("Could not parse any records with flexible methods")

    def _extract_day(self, line: str) -> str:
        """חילוץ שם יום מהשורה"""
        # נסה עברית
        hebrew_match = re.search(FlexiblePatterns.HEBREW_DAY, line)
        if hebrew_match:
            return hebrew_match.group(1)

        # נסה אנגלית
        english_match = re.search(FlexiblePatterns.ENGLISH_DAY, line, re.IGNORECASE)
        if english_match:
            return english_match.group(1)

        return ""

    def _extract_location(self, line: str, day: str) -> str:
        """חילוץ מיקום (בדרך כלל מילה עברית קצרה אחרי היום)"""
        if not day:
            return ""

        # חפש אחרי היום
        day_pos = line.find(day)
        if day_pos == -1:
            return ""

        after_day = line[day_pos + len(day):].strip()

        # קח את המילה הראשונה (עד רווח או זמן)
        words = after_day.split()
        if words and len(words[0]) <= 6:
            # בדוק שזה לא זמן
            if not re.match(r'\d{1,2}:\d{2}', words[0]):
                return words[0]

        return ""

    def _merge_broken_lines(self) -> List[str]:
        """מיזוג שורות שנשברו באמצע"""
        merged = []
        buffer = ""

        for line in self.lines:
            # בדיקה אם השורה מתחילה בתאריך
            if re.match(FlexiblePatterns.DATE, line):
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
            logger.debug(f"Calculated total_hours: {self.metadata.total_hours}")

        # חישוב שכר אם יש תעריף
        if not self.metadata.total_salary and self.metadata.hourly_rate and self.metadata.total_hours:
            self.metadata.total_salary = round(
                self.metadata.hourly_rate * self.metadata.total_hours, 2
            )
            logger.debug(f"Calculated total_salary: {self.metadata.total_salary}")

    def _clean_text(self, text: str) -> str:
        """ניקוי טקסט מתווים מיוחדים"""
        if not text:
            return ""

        text = text.replace("\r", " ").replace("\uFEFF", "").replace("\xa0", " ")
        # נורמליזציה של גרשיים
        text = text.replace("״", '"').replace("׳", "'")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _safe_float(self, value: str, default: float = 0.0) -> float:
        """המרה בטוחה למספר"""
        if not value:
            return default
        try:
            # הסר פסיקים והחלף בנקודה
            cleaned = str(value).replace(",", "").replace(" ", "")
            return float(cleaned)
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