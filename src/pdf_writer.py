"""
pdf_writer.py - PDF Writer with Top Table Support
"""

import logging
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from font_manager import font_manager

# Register fonts
try:
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
except:
    pass

logger = logging.getLogger(__name__)


class PDFWriter:
    """Class for creating PDF attendance reports"""

    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, parsed_report, structure: Optional[dict] = None,
              preserve_layout: bool = True):
        """Write report to PDF"""
        from attendance_parser import TemplateType

        logger.info(f"Writing PDF to {self.output_path}")

        if parsed_report.template_type == TemplateType.DETAILED:
            self._write_detailed_template(parsed_report)
        else:
            self._write_simple_template(parsed_report)

        logger.info(f"✅ PDF written successfully")

    def _write_simple_template(self, report):
        """Write simple template with top table"""
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        elements = []

        # Styles
        hebrew_style = ParagraphStyle(
            'Hebrew',
            fontName='Arial',
            fontSize=10,
            alignment=TA_RIGHT
        )

        title_style = ParagraphStyle(
            'HebrewTitle',
            parent=hebrew_style,
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Arial-Bold'
        )

        # ===== Top Table - Write original content =====
        metadata = report.metadata

        if metadata.top_table_rows and len(metadata.top_table_rows) > 0:
            # Write original table as-is
            top_table_data = []

            for line in metadata.top_table_rows:
                # If row contains numbers, split
                parts = line.split()
                if len(parts) >= 2:
                    # Assume number at end, description at start
                    numbers = [p for p in parts if any(c.isdigit() for c in p)]
                    words = [p for p in parts if p not in numbers]

                    if numbers and words:
                        label = ' '.join(words)
                        value = ' '.join(numbers)
                        top_table_data.append([
                            font_manager.process_hebrew_text(label),
                            value
                        ])
                else:
                    # Row with only description or only number
                    top_table_data.append([font_manager.process_hebrew_text(line), ''])

            if top_table_data:
                top_table = Table(top_table_data, colWidths=[12*cm, 4*cm])
                top_table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), 'Arial', 10),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ]))
                elements.append(top_table)
                elements.append(Spacer(1, 0.8*cm))
        else:
            # If no original table found, write default
            top_table_data = []

            total_hours = metadata.total_hours if metadata.total_hours else sum(r.hours for r in report.records if r.hours)

            if metadata.total_salary:
                top_table_data.append([
                    font_manager.process_hebrew_text('Total Payment'),
                    f'{metadata.total_salary:.2f} ₪'
                ])

            top_table_data.append([
                font_manager.process_hebrew_text('Total Monthly Hours'),
                f'{total_hours:.2f}'
            ])

            if metadata.hourly_rate:
                top_table_data.append([
                    font_manager.process_hebrew_text('Hourly Rate'),
                    f'{metadata.hourly_rate:.2f} ₪'
                ])

            if metadata.required_hours:
                top_table_data.append([
                    font_manager.process_hebrew_text('Total Required Hours'),
                    f'{metadata.required_hours:.2f}'
                ])

            if top_table_data:
                top_table = Table(top_table_data, colWidths=[10*cm, 5*cm])
                top_table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), 'Arial', 10),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ]))
                elements.append(top_table)
                elements.append(Spacer(1, 1*cm))

        # ===== Attendance Table =====
        headers = [
            font_manager.process_hebrew_text(h)
            for h in ['Notes', 'Total', 'Work Hours', 'End Time', 'Start Time', 'Day of Week', 'Date']
        ]

        data = [headers]

        # Add records
        for record in report.records:
            row = [
                record.notes or '',
                f'{record.total:.2f}' if record.total else '',
                f'{record.hours:.2f}' if record.hours else '',
                record.end_time or '',
                record.start_time or '',
                font_manager.process_hebrew_text(record.day_of_week) if record.day_of_week else '',
                record.date or ''
            ]
            data.append(row)

        col_widths = [2.5*cm, 1.8*cm, 2*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm]
        attendance_table = Table(data, colWidths=col_widths)

        attendance_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Arial-Bold', 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 1), (-1, -1), 'Arial', 9),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWHEIGHT', (0, 1), (-1, -1), 0.6*cm),
        ]))

        elements.append(attendance_table)

        doc.build(elements)
        logger.info(f"✅ Simple template written with top table")

    def _write_detailed_template(self, report):
        """Write detailed template"""
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        elements = []

        hebrew_style = ParagraphStyle(
            'Hebrew',
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

        # Title
        title_text = report.metadata.company_name or "N.B. Human Resources Ltd."
        title = Paragraph(font_manager.process_hebrew_text(title_text), title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*cm))

        # Table headers
        headers = [
            font_manager.process_hebrew_text(h)
            for h in ['Saturday', '150%', '125%', '100%', 'Total', 'Break', 'End', 'Start', 'Location', 'Day', 'Date']
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
                font_manager.process_hebrew_text(record.location) if hasattr(record, 'location') and record.location else 'GOV',
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

        # Summary Table
        metadata = report.metadata
        summary_data = [
            [font_manager.process_hebrew_text('Days'), str(len(report.records))],
            [font_manager.process_hebrew_text('Total Hours'), f'{metadata.total_hours:.1f}' if metadata.total_hours else '0'],
            [font_manager.process_hebrew_text('100% Hours'), f'{metadata.total_hours:.1f}' if metadata.total_hours else '0'],
            [font_manager.process_hebrew_text('125% Hours'), '0'],
            [font_manager.process_hebrew_text('150% Hours'), '0'],
            [font_manager.process_hebrew_text('Saturday Hours'), '0'],
            [font_manager.process_hebrew_text('Bonus'), '0'],
            [font_manager.process_hebrew_text('Travel'), '0']
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
        logger.info(f"✅ Detailed template written")


def write_pdf(output_path: str, parsed_report, structure: Optional[dict] = None,
              preserve_layout: bool = True):
    """Helper function to write PDF"""
    writer = PDFWriter(output_path)
    writer.write(parsed_report, structure, preserve_layout)
