"""
pdf_writer.py - Enhanced PDF Writer with Original Layout Preservation
גרסה משופרת ששומרת על המבנה המקורי של המסמך
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
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
    """Class for creating PDF attendance reports with layout preservation"""

    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.structure = None
        self.preserve_layout = True

    def write(self, parsed_report, structure: Optional[dict] = None,
              preserve_layout: bool = True):
        """Write report to PDF with optional layout preservation"""
        from attendance_parser import TemplateType

        logger.info(f"Writing PDF to {self.output_path}")
        logger.info(f"Layout preservation: {'ON' if preserve_layout else 'OFF'}")

        # Store structure and preferences
        self.structure = structure
        self.preserve_layout = preserve_layout

        if parsed_report.template_type == TemplateType.DETAILED:
            self._write_detailed_template(parsed_report)
        else:
            self._write_simple_template(parsed_report)

        logger.info(f"✅ PDF written successfully")

    def _get_page_size(self):
        """Get page size from structure or use default"""
        if self.preserve_layout and self.structure:
            width = self.structure.width
            height = self.structure.height
            logger.info(f"Using original page size: {width:.1f} x {height:.1f}")
            return (width, height)
        return A4

    def _get_margins(self):
        """Get margins from structure or use default"""
        if self.preserve_layout and self.structure:
            margins = self.structure.margins
            logger.info(f"Using original margins: T:{margins['top']:.1f}, "
                       f"B:{margins['bottom']:.1f}, L:{margins['left']:.1f}, R:{margins['right']:.1f}")
            return {
                'topMargin': margins['top'],
                'bottomMargin': margins['bottom'],
                'leftMargin': margins['left'],
                'rightMargin': margins['right']
            }
        return {
            'topMargin': 1.5*cm,
            'bottomMargin': 1.5*cm,
            'leftMargin': 1.5*cm,
            'rightMargin': 1.5*cm
        }

    def _get_primary_font(self):
        """Get primary font from structure or use default"""
        if self.preserve_layout and self.structure and self.structure.fonts:
            # Get most common font
            primary_font = self.structure.fonts[0]
            font_name = primary_font.name

            # Map to available fonts
            if 'Arial' in font_name or 'Helvetica' in font_name:
                return 'Arial', primary_font.size
            elif 'Times' in font_name:
                return 'Times-Roman', primary_font.size
            else:
                return 'Arial', primary_font.size

        return 'Arial', 10

    def _get_header_font(self):
        """Get header font (usually bold and larger)"""
        base_font, base_size = self._get_primary_font()

        if self.preserve_layout and self.structure and len(self.structure.fonts) > 1:
            # Look for a larger/bold font
            for font in self.structure.fonts[:3]:
                if font.bold or font.size > base_size:
                    return f"{base_font.split('-')[0]}-Bold", font.size

        return f"{base_font.split('-')[0]}-Bold", base_size * 1.2

    def _get_column_widths_from_structure(self, num_columns: int) -> List[float]:
        """Calculate column widths from original structure"""
        if not self.preserve_layout or not self.structure or not self.structure.columns:
            return None

        columns = self.structure.columns

        # If we have exactly the number of columns we need
        if len(columns) == num_columns:
            widths = [col.width for col in columns]
            logger.info(f"Using original column widths: {[f'{w:.1f}' for w in widths]}")
            return widths

        # If we have more or fewer columns, try to adapt
        logger.warning(f"Column count mismatch: found {len(columns)}, needed {num_columns}")
        return None

    def _get_row_height(self):
        """Get row height from structure"""
        if self.preserve_layout and self.structure:
            row_height = self.structure.row_spacing
            logger.info(f"Using original row height: {row_height:.1f}")
            return row_height
        return 0.6*cm

    def _write_simple_template(self, report):
        """Write simple template with original layout preservation"""
        # Get layout parameters
        page_size = self._get_page_size()
        margins = self._get_margins()
        base_font, base_font_size = self._get_primary_font()
        header_font, header_font_size = self._get_header_font()

        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=page_size,
            **margins
        )

        elements = []

        # Styles
        hebrew_style = ParagraphStyle(
            'Hebrew',
            fontName=base_font,
            fontSize=base_font_size,
            alignment=TA_RIGHT
        )

        title_style = ParagraphStyle(
            'HebrewTitle',
            fontName=header_font,
            fontSize=header_font_size * 1.2,
            alignment=TA_CENTER,
            spaceAfter=15
        )

        # ===== Top Table =====
        metadata = report.metadata

        if metadata.top_table_rows and len(metadata.top_table_rows) > 0:
            top_table_data = []

            for line in metadata.top_table_rows:
                parts = line.split()
                if len(parts) >= 2:
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
                    top_table_data.append([font_manager.process_hebrew_text(line), ''])

            if top_table_data:
                # Calculate widths based on page size
                page_width = page_size[0] - margins['leftMargin'] - margins['rightMargin']
                col_widths = [page_width * 0.7, page_width * 0.3]

                top_table = Table(top_table_data, colWidths=col_widths)
                top_table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), base_font, base_font_size),
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
            # Default top table
            top_table_data = []
            total_hours = metadata.total_hours if metadata.total_hours else sum(r.hours for r in report.records if r.hours)

            if metadata.total_salary:
                top_table_data.append([
                    font_manager.process_hebrew_text('סה"כ לתשלום'),
                    f'{metadata.total_salary:.2f} ₪'
                ])

            top_table_data.append([
                font_manager.process_hebrew_text('סה"כ שעות חודשיות'),
                f'{total_hours:.2f}'
            ])

            if metadata.hourly_rate:
                top_table_data.append([
                    font_manager.process_hebrew_text('מחיר לשעה'),
                    f'{metadata.hourly_rate:.2f} ₪'
                ])

            if top_table_data:
                page_width = page_size[0] - margins['leftMargin'] - margins['rightMargin']
                col_widths = [page_width * 0.65, page_width * 0.35]

                top_table = Table(top_table_data, colWidths=col_widths)
                top_table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, -1), base_font, base_font_size),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(top_table)
                elements.append(Spacer(1, 1*cm))

        # ===== Attendance Table =====
        headers = [
            font_manager.process_hebrew_text(h)
            for h in ['הערות', 'סה"כ', 'שעות עבודה', 'שעת סיום', 'שעת התחלה', 'יום בשבוע', 'תאריך']
        ]

        data = [headers]

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

        # Try to get column widths from structure
        col_widths = self._get_column_widths_from_structure(7)
        if not col_widths:
            # Default widths
            col_widths = [2.5*cm, 1.8*cm, 2*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm]
            logger.info("Using default column widths")

        attendance_table = Table(data, colWidths=col_widths)

        row_height = self._get_row_height()

        attendance_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), header_font, header_font_size * 0.9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 1), (-1, -1), base_font, base_font_size * 0.9),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWHEIGHT', (0, 1), (-1, -1), row_height),
        ]))

        elements.append(attendance_table)

        doc.build(elements)
        logger.info(f"✅ Simple template written with layout preservation")

    def _write_detailed_template(self, report):
        """Write detailed template with original layout preservation"""
        # Get layout parameters
        page_size = self._get_page_size()
        margins = self._get_margins()
        base_font, base_font_size = self._get_primary_font()
        header_font, header_font_size = self._get_header_font()

        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=page_size,
            **margins
        )

        elements = []

        # Styles
        hebrew_style = ParagraphStyle(
            'Hebrew',
            fontName=base_font,
            fontSize=base_font_size,
            alignment=TA_RIGHT
        )

        title_style = ParagraphStyle(
            'HebrewTitle',
            fontName=header_font,
            fontSize=header_font_size * 1.2,
            alignment=TA_CENTER,
            spaceAfter=15
        )

        # Title
        title_text = report.metadata.company_name or "N.B. Human Resources Ltd."
        title = Paragraph(font_manager.process_hebrew_text(title_text), title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*cm))

        # Table headers
        headers = [
            font_manager.process_hebrew_text(h)
            for h in ['שבת','150%', '125%', '100%', 'סה"כ', 'הפסקה', 'סיום', 'התחלה', 'יום', 'תאריך']
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
                font_manager.process_hebrew_text(f"יום {record.location}") if hasattr(record, 'location') and record.location else 'שבת',
                record.date or ''
            ]
            data.append(row)

        # Try to get column widths from structure
        col_widths = self._get_column_widths_from_structure(10)
        if not col_widths:
            # Default widths for detailed template
            col_widths = [1.2*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm, 2*cm]
            logger.info("Using default column widths for detailed template")

        main_table = Table(data, colWidths=col_widths)

        row_height = self._get_row_height()

        main_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), header_font, header_font_size * 0.7),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a4a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONT', (0, 1), (-1, -1), base_font, base_font_size * 0.7),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWHEIGHT', (0, 1), (-1, -1), row_height * 0.8),
        ]))

        elements.append(main_table)
        elements.append(Spacer(1, 0.5*cm))

        # Summary Table
        metadata = report.metadata
        summary_data = [
            [font_manager.process_hebrew_text('ימים'), str(len(report.records))],
            [font_manager.process_hebrew_text('סה"כ שעות'), f'{metadata.total_hours:.1f}' if metadata.total_hours else '0'],
            [font_manager.process_hebrew_text('100% שעות'), f'{metadata.total_hours:.1f}' if metadata.total_hours else '0'],
            [font_manager.process_hebrew_text('125% שעות'), '0'],
            [font_manager.process_hebrew_text('150% שעות'), '0'],
            [font_manager.process_hebrew_text('שעות שבת'), '0'],
            [font_manager.process_hebrew_text('בונוס'), '0'],
            [font_manager.process_hebrew_text('נסיעות'), '0']
        ]

        summary_table = Table(summary_data, colWidths=[3*cm, 3*cm])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), base_font, base_font_size * 0.8),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(summary_table)

        doc.build(elements)
        logger.info(f"✅ Detailed template written with layout preservation")


def write_pdf(output_path: str, parsed_report, structure: Optional[dict] = None,
              preserve_layout: bool = True):
    """Helper function to write PDF with layout preservation"""
    writer = PDFWriter(output_path)
    writer.write(parsed_report, structure, preserve_layout)