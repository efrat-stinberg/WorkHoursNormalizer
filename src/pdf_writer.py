"""
pdf_writer.py - Unified PDF Writer
מאחד את pdf_writer.py ו-pdf_writer_enhanced.py המקוריים
משתמש ב-font_manager ובניתוח המבנה
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas as pdf_canvas

from font_manager import font_manager

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Hebrew-supporting fonts
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))


logger = logging.getLogger(__name__)


class PDFWriter:
    """מחלקה מאוחדת ליצירת PDF מדוחות נוכחות"""

    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, parsed_report, structure: Optional[Dict] = None,
              preserve_layout: bool = True):
        """
        כתיבת דוח לPDF

        Args:
            parsed_report: ParsedReport מהמנתח
            structure: מבנה מקורי מה-reader (אופציונלי)
            preserve_layout: האם לשמור על העיצוב המקורי
        """
        from attendance_parser import TemplateType

        logger.info(f"Writing PDF to {self.output_path}")

        # בחירת שיטת כתיבה לפי סוג
        if preserve_layout and structure:
            self._write_with_structure(parsed_report, structure)
        elif parsed_report.template_type == TemplateType.DETAILED:
            self._write_detailed_template(parsed_report)
        else:
            self._write_simple_template(parsed_report)

        logger.info(f"✅ PDF written successfully")

    def _write_simple_template(self, report):
        """כתיבת תבנית פשוטה"""
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        elements = []
        styles = getSampleStyleSheet()

        # סגנון עברי
        hebrew_style = ParagraphStyle(
            'Hebrew',
            parent=styles['Normal'],
            fontName='Arial',
            fontSize=10,
            alignment=TA_RIGHT
        )

        title_style = ParagraphStyle(
            'HebrewTitle',
            parent=hebrew_style,
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Arial-Bold'
        )

        # כותרת
        title_text = font_manager.process_hebrew_text("דוח נוכחות חודשי")
        title = Paragraph(title_text, title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))

        # מידע עליון
        metadata = report.metadata
        info_data = []

        if metadata.total_salary:
            info_data.append([
                font_manager.process_hebrew_text('סה"כ לתשלום'),
                f'₪ {metadata.total_salary:.2f}'
            ])

        if metadata.hourly_rate:
            info_data.append([
                font_manager.process_hebrew_text('מחיר לשעה'),
                f'₪ {metadata.hourly_rate:.2f}'
            ])

        if metadata.total_hours:
            info_data.append([
                font_manager.process_hebrew_text('סה"כ שעות החודשית'),
                f'{metadata.total_hours:.2f}'
            ])

        if metadata.required_hours:
            info_data.append([
                font_manager.process_hebrew_text('סה"כ שעות עבודה למשרה'),
                f'{metadata.required_hours:.2f}'
            ])

        if info_data:
            info_table = Table(info_data, colWidths=[8*cm, 6*cm])
            info_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Arial', 9),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 1*cm))

        # טבלת נוכחות
        headers = [
            font_manager.process_hebrew_text(h)
            for h in ['הערות', 'סה"כ', 'שעות עבודה', 'שעת סיום', 'שעת התחלה', 'יום בשבוע', 'תאריך']
        ]

        data = [headers]

        for record in report.records:
            row = [
                '',  # הערות
                f'{record.total:.2f}' if record.total else '',
                f'{record.hours:.2f}' if record.hours else '',
                record.end_time or '',
                record.start_time or '',
                font_manager.process_hebrew_text(record.day_of_week) if record.day_of_week else '',
                record.date or ''
            ]
            data.append(row)

        # הוספת שורות ריקות
        while len(data) < 22:
            data.append(['', '', '', '', '', '', ''])

        col_widths = [2.5*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm]
        attendance_table = Table(data, colWidths=col_widths)

        attendance_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Arial-Bold', 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 1), (-1, -1), 'Arial', 8),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWHEIGHT', (0, 1), (-1, -1), 0.6*cm),
        ]))

        elements.append(attendance_table)

        doc.build(elements)

    def _write_detailed_template(self, report):
        """כתיבת תבנית מפורטת"""
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        elements = []
        styles = getSampleStyleSheet()

        hebrew_style = ParagraphStyle(
            'Hebrew',
            parent=styles['Normal'],
            fontName='Arial',
            fontSize=10,
            alignment=TA_RIGHT
        )

        title_style = ParagraphStyle(
            'HebrewTitle',
            parent=hebrew_style,
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Arial-Bold'
        )

        # כותרת
        title_text = report.metadata.company_name or "נ.ב. תושר כח אדם בע\"מ"
        title = Paragraph(font_manager.process_hebrew_text(title_text), title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*cm))

        # כותרות טבלה
        headers = [
            font_manager.process_hebrew_text(h)
            for h in ['שבת', '150%', '125%', '100%', 'סה"כ', 'הפסקה', 'יציאה', 'כניסה', 'מקום', 'יום', 'תאריך']
        ]

        data = [headers]

        for record in report.records:
            row = [
                f'{record.saturday:.2f}' if hasattr(record, 'saturday') and record.saturday else '0.00',
                f'{record.hours_150:.2f}' if hasattr(record, 'hours_150') and record.hours_150 else '0.00',
                f'{record.hours_125:.2f}' if hasattr(record, 'hours_125') and record.hours_125 else '0.00',
                f'{record.hours_100:.2f}' if hasattr(record, 'hours_100') and record.hours_100 else '0.00',
                f'{record.total:.2f}' if record.total else '0.00',
                record.break_time if hasattr(record, 'break_time') and record.break_time else '00:30',
                record.end_time or '00:00',
                record.start_time or '00:00',
                font_manager.process_hebrew_text(record.location) if hasattr(record, 'location') and record.location else 'גוב',
                font_manager.process_hebrew_text(record.day_of_week) if record.day_of_week else '',
                record.date or ''
            ]
            data.append(row)

        col_widths = [1.2*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm, 2*cm, 2.5*cm]

        main_table = Table(data, colWidths=col_widths)
        main_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Arial-Bold', 7),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a4a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 1), (-1, -1), 'Arial', 7),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWHEIGHT', (0, 1), (-1, -1), 0.5*cm),
        ]))

        elements.append(main_table)
        elements.append(Spacer(1, 0.5*cm))

        # טבלת סיכום
        metadata = report.metadata
        summary_data = [
            [font_manager.process_hebrew_text('ימים'), str(len(report.records))],
            [font_manager.process_hebrew_text('סה"כ שעות'), f'{metadata.total_hours:.1f}' if metadata.total_hours else '0'],
            [font_manager.process_hebrew_text('שעות 100%'), f'{metadata.total_hours:.1f}' if metadata.total_hours else '0'],
            [font_manager.process_hebrew_text('שעות 125%'), '0'],
            [font_manager.process_hebrew_text('שעות 150%'), '0'],
            [font_manager.process_hebrew_text('שעות שבת'), '0'],
            [font_manager.process_hebrew_text('בונוס'), '0'],
            [font_manager.process_hebrew_text('נסיעות'), '0']
        ]

        summary_table = Table(summary_data, colWidths=[3*cm, 3*cm])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Arial', 8),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(summary_table)

        doc.build(elements)

    def _write_with_structure(self, report, structure: Dict):
        """כתיבה עם שמירה על מבנה מקורי (מתקדם)"""
        # TODO: מימוש מלא בעתיד - כרגע נשתמש בתבנית רגילה
        logger.info("Structure-preserving write requested, falling back to template")

        from attendance_parser import TemplateType
        if report.template_type == TemplateType.DETAILED:
            self._write_detailed_template(report)
        else:
            self._write_simple_template(report)


def write_pdf(output_path: str, parsed_report, structure: Optional[Dict] = None,
              preserve_layout: bool = True):
    """
    פונקציה עזר לכתיבת PDF

    Args:
        output_path: נתיב לשמירה
        parsed_report: דוח מפוענח
        structure: מבנה מקורי (אופציונלי)
        preserve_layout: שמירת עיצוב
    """
    writer = PDFWriter(output_path)
    writer.write(parsed_report, structure, preserve_layout)