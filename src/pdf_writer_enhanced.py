"""
מודול ליצירת דוחות נוכחות PDF משומרי תבנית
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from typing import List, Dict
import os
import logging
from attendance_parser import TemplateType, DetailedAttendanceRecord

logger = logging.getLogger(__name__)


class AttendanceReportWriter:
    """מחלקה ליצירת דוחות נוכחות בפורמט PDF"""

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.setup_hebrew_font()

    def setup_hebrew_font(self):
        """הגדרת פונט עברית"""
        try:
            # נסה לטעון Arial אם קיים
            pdfmetrics.registerFont(TTFont('Hebrew', 'arial.ttf'))
            self.hebrew_font = 'Hebrew'
            logger.info("Loaded Hebrew font: arial.ttf")
        except:
            # fallback להלבטיקה
            self.hebrew_font = 'Helvetica'
            logger.warning("Using Helvetica as fallback font")

    def create_template_1_report(self, metadata: Dict, records: List) -> str:
        """
        יצירת דוח בתבנית 1 (פשוטה)
        """
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        elements = []
        styles = getSampleStyleSheet()

        hebrew_style = ParagraphStyle(
            'Hebrew',
            parent=styles['Normal'],
            fontName=self.hebrew_font,
            fontSize=10,
            alignment=TA_RIGHT,
        )

        title_style = ParagraphStyle(
            'HebrewTitle',
            parent=hebrew_style,
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20,
        )

        # כותרת
        title = Paragraph("דוח נוכחות חודשי", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5 * cm))

        # טבלת מידע עליון
        total_salary = metadata.get("total_salary", 0)
        hourly_rate = metadata.get("hourly_rate", 30.65)
        total_hours = metadata.get("total_hours", 0)
        required_hours = metadata.get("required_hours", 84.00)

        header_data = [
            ['סה"כ לתשלום', f'₪ {total_salary:.2f}'],
            ['מחיר לשעה', f'₪ {hourly_rate:.2f}'],
            ['סה"כ שעות החודשית', f'{total_hours:.2f}'],
            ['סה"כ שעות עבודה למשרה', f'{required_hours:.2f}']
        ]

        header_table = Table(header_data, colWidths=[8 * cm, 6 * cm])
        header_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.hebrew_font, 9),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 1 * cm))

        # טבלת נוכחות ראשית
        attendance_header = [['הערות', 'סה"כ', 'שעות עבודה', 'שעת סיום', 'שעת התחלה', 'יום בשבוע', 'תאריך']]
        attendance_data = []

        for record in records:
            row = [
                '',  # הערות
                f'{record.total:.2f}' if hasattr(record, 'total') and record.total else '',
                f'{record.hours:.2f}' if hasattr(record, 'hours') and record.hours else '',
                record.end_time if hasattr(record, 'end_time') else '',
                record.start_time if hasattr(record, 'start_time') else '',
                record.day_of_week if hasattr(record, 'day_of_week') else '',
                record.date if hasattr(record, 'date') else ''
            ]
            attendance_data.append(row)

        # שורות ריקות
        while len(attendance_data) < 20:
            attendance_data.append(['', '', '', '', '', '', ''])

        full_data = attendance_header + attendance_data

        attendance_table = Table(full_data, colWidths=[2.5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 2.5 * cm, 2.5 * cm])
        attendance_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), self.hebrew_font, 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONT', (0, 1), (-1, -1), self.hebrew_font, 8),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWHEIGHT', (0, 1), (-1, -1), 0.6 * cm),
        ]))

        elements.append(attendance_table)

        doc.build(elements)
        logger.info(f"Created Template 1 report: {self.output_path}")
        return self.output_path

    def create_template_2_report(self, metadata: Dict, records: List) -> str:
        """
        יצירת דוח בתבנית 2 (מפורטת)
        """
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm
        )

        elements = []
        styles = getSampleStyleSheet()

        hebrew_style = ParagraphStyle(
            'Hebrew',
            parent=styles['Normal'],
            fontName=self.hebrew_font,
            fontSize=10,
            alignment=TA_RIGHT,
        )

        title_style = ParagraphStyle(
            'HebrewTitle',
            parent=hebrew_style,
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=15,
        )

        # כותרת
        title_text = metadata.get('employee_name', 'נ.ב. תושר כח אדם בע"מ')
        title = Paragraph(title_text, title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3 * cm))

        # טבלת נוכחות מפורטת
        header = [['שבת', '150%', '125%', '100%', 'סה"כ', 'הפסקה', 'יציאה', 'כניסה', 'מקום', 'יום', 'תאריך']]

        attendance_data = []
        for record in records:
            row = [
                f'{record.saturday:.2f}' if hasattr(record, 'saturday') and record.saturday else '0.00',
                f'{record.hours_150:.2f}' if hasattr(record, 'hours_150') and record.hours_150 else '0.00',
                f'{record.hours_125:.2f}' if hasattr(record, 'hours_125') and record.hours_125 else '0.00',
                f'{record.hours_100:.2f}' if hasattr(record, 'hours_100') and record.hours_100 else '0.00',
                f'{record.total:.2f}' if hasattr(record, 'total') and record.total else '0.00',
                record.break_time if hasattr(record, 'break_time') and record.break_time else '00:30',
                record.end_time if hasattr(record, 'end_time') else '00:00',
                record.start_time if hasattr(record, 'start_time') else '00:00',
                record.location if hasattr(record, 'location') and record.location else 'גוב',
                record.day_of_week if hasattr(record, 'day_of_week') else '',
                record.date if hasattr(record, 'date') else ''
            ]
            attendance_data.append(row)

        full_data = header + attendance_data

        col_widths = [1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 2 * cm,
                      2.5 * cm]

        main_table = Table(full_data, colWidths=col_widths)
        main_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), self.hebrew_font, 7),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a4a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 1), (-1, -1), self.hebrew_font, 7),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWHEIGHT', (0, 1), (-1, -1), 0.5 * cm),
        ]))

        elements.append(main_table)
        elements.append(Spacer(1, 0.5 * cm))

        # טבלת סיכום
        total_hours = metadata.get("total_hours", 0)
        summary_data = [
            ['ימים', str(len(records))],
            ['סה"כ שעות', f'{total_hours:.1f}'],
            ['שעות 100%', f'{total_hours:.1f}'],
            ['שעות 125%', '0'],
            ['שעות 150%', '0'],
            ['שעות שבת', '0'],
            ['בונוס', '0'],
            ['נסיעות', '0']
        ]

        summary_table = Table(summary_data, colWidths=[3 * cm, 3 * cm])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.hebrew_font, 8),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(summary_table)

        doc.build(elements)
        logger.info(f"Created Template 2 report: {self.output_path}")
        return self.output_path


def create_report_from_parsed_data(parsed_data: Dict, output_path: str) -> str:
    """
    פונקציה עזר ליצירת דוח מנתונים מפוענחים
    """
    writer = AttendanceReportWriter(output_path)

    metadata = parsed_data['metadata']
    records = parsed_data['records']
    template_type = parsed_data['template_type']

    # המרת metadata ל-dict אם זה dataclass
    if hasattr(metadata, '__dict__'):
        metadata_dict = metadata.__dict__
    else:
        metadata_dict = metadata

    if template_type == TemplateType.TEMPLATE_1:
        return writer.create_template_1_report(metadata_dict, records)
    elif template_type == TemplateType.TEMPLATE_2:
        return writer.create_template_2_report(metadata_dict, records)
    else:
        # fallback לתבנית 1
        logger.warning("Unknown template type, using Template 1 as fallback")
        return writer.create_template_1_report(metadata_dict, records)