"""
מערכת לזיהוי, חילוץ וכתיבה של דוחות נוכחות - שני סוגי תבניות
"""

import pdfplumber
import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """סוגי תבניות הדוח"""
    TEMPLATE_1 = "simple"  # תבנית פשוטה
    TEMPLATE_2 = "detailed"  # תבנית מפורטת
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


@dataclass
class DetailedAttendanceRecord(AttendanceRecord):
    """רשומת נוכחות מפורטת (תבנית 2)"""
    location: Optional[str] = None
    break_time: Optional[str] = None
    hours_100: Optional[float] = None
    hours_125: Optional[float] = None
    hours_150: Optional[float] = None
    saturday: Optional[float] = None


@dataclass
class ReportMetadata:
    """מטא-דאטה של הדוח"""
    employee_name: Optional[str] = None
    employee_id: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    total_hours: Optional[float] = None
    total_salary: Optional[float] = None
    hourly_rate: Optional[float] = 30.65
    required_hours: Optional[float] = 84.00
    template_type: TemplateType = TemplateType.UNKNOWN


class AttendanceReportParser:
    """מחלקה ראשית לניתוח דוחות נוכחות"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text_content = ""
        self.metadata = ReportMetadata()
        self.records = []

    def extract_text(self) -> str:
        """חילוץ טקסט מה-PDF"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text_parts.append(page.extract_text())
                self.text_content = "\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            self.text_content = ""
        return self.text_content

    def identify_template(self) -> TemplateType:
        """זיהוי סוג התבנית"""
        text = self.text_content.lower()

        # מילות מפתח לתבנית 2
        template2_keywords = [
            "תושר כח אדם",
            "נ.ב. תושר",
            "בע\"מ",
            "125%",
            "150%"
        ]

        # בדיקה לתבנית 2
        if any(keyword in text for keyword in template2_keywords):
            self.metadata.template_type = TemplateType.TEMPLATE_2
            logger.info("Identified template type: TEMPLATE_2 (detailed)")
            return TemplateType.TEMPLATE_2

        # תבנית 1 - בדיקות נוספות
        template1_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}\s+[א-ת]+\s+\d{1,2}:\d{2}',
            r'סה"כ.*שעות.*החודשית',
            r'סה"כ.*עבודה.*למשרה'
        ]

        if any(re.search(pattern, text) for pattern in template1_patterns):
            self.metadata.template_type = TemplateType.TEMPLATE_1
            logger.info("Identified template type: TEMPLATE_1 (simple)")
            return TemplateType.TEMPLATE_1

        self.metadata.template_type = TemplateType.UNKNOWN
        logger.warning("Could not identify template type")
        return TemplateType.UNKNOWN

    def parse_template_1(self):
        """ניתוח תבנית 1 - דוח פשוט"""
        lines = self.text_content.split('\n')

        # חילוץ מטא-דאטה
        for line in lines[:15]:
            if 'סה"כ' in line and '₪' in line:
                numbers = re.findall(r'[\d,]+\.?\d*', line)
                if numbers:
                    try:
                        self.metadata.total_salary = float(numbers[-1].replace(',', ''))
                    except:
                        pass

            if 'מחיר לשעה' in line:
                numbers = re.findall(r'[\d.]+', line)
                if numbers:
                    try:
                        self.metadata.hourly_rate = float(numbers[-1])
                    except:
                        pass

        # חילוץ רשומות נוכחות - תבנית גמישה יותר
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s+([א-ת]+)\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})\s+([\d.]+)',
            r'(\d{1,2}/\d{1,2}/\d{2,4})\s+([א-ת]+)\s+.*?(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})\s+([\d.]+)'
        ]

        for line in lines:
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        record = AttendanceRecord(
                            date=match.group(1),
                            day_of_week=match.group(2),
                            start_time=match.group(3),
                            end_time=match.group(4),
                            hours=float(match.group(5)),
                            total=float(match.group(5))
                        )
                        self.records.append(record)
                        break
                    except:
                        continue

        # חישוב סה"כ שעות
        if self.records:
            self.metadata.total_hours = sum(r.hours for r in self.records if r.hours)

        logger.info(f"Parsed {len(self.records)} records from template 1")

    def parse_template_2(self):
        """ניתוח תבנית 2 - דוח מפורט"""
        lines = self.text_content.split('\n')

        # חילוץ כותרת
        for line in lines[:5]:
            if 'תושר' in line or 'בע"מ' in line:
                self.metadata.employee_name = line.strip()

        # חילוץ רשומות - פורמט מורכב
        date_pattern = r'(\d{2}/\d{2}/\d{4})\s+([א-ת\s]+?)\s+([א-ת]+)\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'

        for line in lines:
            match = re.search(date_pattern, line)
            if match:
                try:
                    record = DetailedAttendanceRecord(
                        date=match.group(1),
                        day_of_week=match.group(2).strip(),
                        location=match.group(3),
                        start_time=match.group(4),
                        end_time=match.group(5),
                        break_time=match.group(6),
                        total=float(match.group(7)),
                        hours_100=float(match.group(8)),
                        hours_125=float(match.group(9)),
                        hours_150=float(match.group(10)),
                        saturday=float(match.group(11))
                    )
                    self.records.append(record)
                except:
                    continue

        # חילוץ סיכום
        summary_pattern = r'סה"כ שעות\s+([\d.]+)'
        match = re.search(summary_pattern, self.text_content)
        if match:
            try:
                self.metadata.total_hours = float(match.group(1))
            except:
                pass

        logger.info(f"Parsed {len(self.records)} records from template 2")

    def parse(self) -> Dict:
        """ניתוח מלא של הדוח"""
        self.extract_text()
        template_type = self.identify_template()

        if template_type == TemplateType.TEMPLATE_1:
            self.parse_template_1()
        elif template_type == TemplateType.TEMPLATE_2:
            self.parse_template_2()
        else:
            logger.warning("Unknown template type - attempting generic parsing")
            self.parse_template_1()  # fallback

        return {
            'metadata': self.metadata,
            'records': self.records,
            'template_type': template_type
        }


def parse_attendance_report(pdf_path: str) -> Dict:
    """
    פונקציה ראשית לניתוח דוח נוכחות

    Args:
        pdf_path: נתיב לקובץ PDF

    Returns:
        מילון עם מטא-דאטה ורשומות
    """
    parser = AttendanceReportParser(pdf_path)
    result = parser.parse()
    return result