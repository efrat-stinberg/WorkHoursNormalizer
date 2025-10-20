"""
pdf_reader.py - Unified PDF Reading Layer
Unifies text extraction and structure analysis into a comprehensive module
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import pdfplumber

logger = logging.getLogger(__name__)


@dataclass
class FontInfo:
    """Font information"""
    name: str
    size: float
    bold: bool = False
    italic: bool = False
    count: int = 0


@dataclass
class ColumnInfo:
    """Information about a table column"""
    name: str
    x: float
    width: float
    alignment: str = "left"
    font_size: float = 10.0


@dataclass
class PageStructure:
    """Structure of a report page"""
    page_number: int
    width: float
    height: float
    orientation: str  # portrait/landscape
    margins: Dict[str, float]
    columns: List[ColumnInfo] = field(default_factory=list)
    fonts: List[FontInfo] = field(default_factory=list)
    row_spacing: float = 14.0
    table_bbox: Dict[str, float] = field(default_factory=dict)


@dataclass
class PDFContent:
    """Full PDF content after reading"""
    file_path: str
    text: str
    page_count: int
    structures: List[PageStructure] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PDFReader:
    """Unified PDF reader class with structure analysis"""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        self.content: Optional[PDFContent] = None

    def read(self, analyze_structure: bool = True) -> PDFContent:
        """
        Full PDF reading

        Args:
            analyze_structure: Whether to also analyze the graphical structure

        Returns:
            PDFContent with all information
        """
        logger.info(f"Reading PDF: {self.pdf_path}")

        # Text extraction
        text = self._extract_text()

        # Get page count
        page_count = self._get_page_count()

        # Create basic content object
        self.content = PDFContent(
            file_path=str(self.pdf_path),
            text=text,
            page_count=page_count
        )

        # Analyze structure if requested
        if analyze_structure:
            structures = self._analyze_structure()
            self.content.structures = structures

        logger.info(f"✅ PDF read successfully: {page_count} pages, {len(text)} chars")
        return self.content

    def _extract_text(self) -> str:
        """Text extraction using multiple methods (fallback)"""

        # Attempt 1: PyPDF2
        try:
            text = self._extract_with_pypdf2()
            if text and len(text.strip()) > 100:
                logger.debug("Text extracted with PyPDF2")
                return self._sanitize_text(text)
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")

        # Attempt 2: pdfplumber
        try:
            text = self._extract_with_pdfplumber()
            if text and len(text.strip()) > 100:
                logger.debug("Text extracted with pdfplumber")
                return self._sanitize_text(text)
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")

        # Attempt 3: PyMuPDF
        try:
            text = self._extract_with_pymupdf()
            if text:
                logger.debug("Text extracted with PyMuPDF")
                return self._sanitize_text(text)
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}")

        logger.error("All text extraction methods failed")
        return ""

    def _extract_with_pypdf2(self) -> str:
        """Extraction using PyPDF2"""
        reader = PdfReader(str(self.pdf_path))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)

    def _extract_with_pdfplumber(self) -> str:
        """Extraction using pdfplumber"""
        text_parts = []
        with pdfplumber.open(str(self.pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    def _extract_with_pymupdf(self) -> str:
        """Extraction using PyMuPDF"""
        doc = fitz.open(str(self.pdf_path))
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)

    def _get_page_count(self) -> int:
        """Get number of pages"""
        try:
            doc = fitz.open(str(self.pdf_path))
            count = len(doc)
            doc.close()
            return count
        except Exception:
            return 1

    def _analyze_structure(self) -> List[PageStructure]:
        """Analyze graphical structure of all pages"""
        structures = []

        try:
            doc = fitz.open(str(self.pdf_path))

            for page_num in range(len(doc)):
                structure = self._analyze_page_structure(doc, page_num)
                structures.append(structure)

            doc.close()

        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")

        return structures

    def _analyze_page_structure(self, doc, page_num: int) -> PageStructure:
        """Analyze the structure of a single page"""
        page = doc[page_num]
        width, height = page.rect.width, page.rect.height

        # Extract spans (words with position)
        page_dict = page.get_text("dict")
        spans = []
        fonts_dict = {}

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:  # text only
                continue

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    spans.append(span)

                    # Collect fonts
                    font_key = (
                        span.get("font", ""),
                        round(span.get("size", 10), 1),
                        bool(span.get("flags", 0) & 1),  # bold
                        bool(span.get("flags", 0) & 2)  # italic
                    )
                    fonts_dict[font_key] = fonts_dict.get(font_key, 0) + 1

        # Calculate margins
        margins = self._calculate_margins(spans, width, height)

        # Detect columns
        columns = self._detect_columns(spans, margins, height)

        # Convert fonts to list
        fonts = [
            FontInfo(name=f[0], size=f[1], bold=f[2], italic=f[3], count=count)
            for f, count in sorted(fonts_dict.items(), key=lambda x: -x[1])
        ]

        # Calculate row spacing
        row_spacing = self._calculate_row_spacing(spans)

        # Table bounding box
        table_bbox = self._calculate_table_bbox(columns, spans, margins, height)

        return PageStructure(
            page_number=page_num + 1,
            width=width,
            height=height,
            orientation="landscape" if width > height else "portrait",
            margins=margins,
            columns=columns,
            fonts=fonts,
            row_spacing=row_spacing,
            table_bbox=table_bbox
        )

    def _calculate_margins(self, spans: List[Dict], width: float, height: float) -> Dict[str, float]:
        """Calculate margins from text"""
        if not spans:
            return {"top": 36, "bottom": 36, "left": 36, "right": 36}

        lefts = [s["bbox"][0] for s in spans]
        rights = [s["bbox"][2] for s in spans]
        tops = [s["bbox"][1] for s in spans]
        bottoms = [s["bbox"][3] for s in spans]

        return {
            "top": max(0, min(tops)),
            "bottom": max(0, height - max(bottoms)),
            "left": max(0, min(lefts)),
            "right": max(0, width - max(rights))
        }

    def _detect_columns(self, spans: List[Dict], margins: Dict[str, float],
                        page_height: float) -> List[ColumnInfo]:
        """Detect table columns"""
        if not spans:
            return []

        # Find header spans (top part)
        header_y = margins["top"] + 0.05 * page_height
        header_spans = [s for s in spans if s["bbox"][1] <= header_y]

        if not header_spans:
            header_spans = sorted(spans, key=lambda s: s["bbox"][1])[:15]

        # Group by X
        x_positions = sorted(set(round(s["bbox"][0], 1) for s in header_spans))

        # Create clusters
        clusters = []
        if x_positions:
            current_cluster = [x_positions[0]]
            for x in x_positions[1:]:
                if x - current_cluster[-1] <= 8.0:
                    current_cluster.append(x)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [x]
            clusters.append(current_cluster)

        column_xs = [sum(c) / len(c) for c in clusters]

        # Create columns
        columns = []
        for i, x in enumerate(column_xs):
            # Column width
            next_x = column_xs[i + 1] if i + 1 < len(column_xs) else (margins["right"] + 100)
            col_width = max(20, next_x - x - 4)

            # Column name from nearest header
            name = f"col_{i + 1}"
            for span in header_spans:
                if abs(span["bbox"][0] - x) < col_width / 2:
                    text = span.get("text", "").strip()
                    if text:
                        name = text
                        break

            columns.append(ColumnInfo(
                name=name,
                x=x,
                width=col_width,
                alignment=self._guess_alignment(x, col_width, header_spans)
            ))

        return columns

    def _guess_alignment(self, col_x: float, col_width: float,
                         spans: List[Dict]) -> str:
        """Guess column alignment"""
        # Find spans in this column
        col_spans = [s for s in spans if abs(s["bbox"][0] - col_x) < col_width / 2]

        if not col_spans:
            return "left"

        # Check if most spans start near X
        left_aligned = sum(1 for s in col_spans if abs(s["bbox"][0] - col_x) < 3)

        if left_aligned > len(col_spans) * 0.7:
            return "left"

        return "center"

    def _calculate_row_spacing(self, spans: List[Dict]) -> float:
        """Calculate spacing between rows"""
        if len(spans) < 2:
            return 14.0

        # Get Y positions of all rows
        y_positions = sorted(set(round(s["bbox"][1], 1) for s in spans))

        if len(y_positions) < 2:
            return 14.0

        # Compute gaps
        gaps = [y_positions[i + 1] - y_positions[i] for i in range(len(y_positions) - 1)]

        # Return most common size
        from collections import Counter
        counter = Counter(round(g, 1) for g in gaps)
        return counter.most_common(1)[0][0] if counter else 14.0

    def _calculate_table_bbox(self, columns: List[ColumnInfo], spans: List[Dict],
                              margins: Dict[str, float], height: float) -> Dict[str, float]:
        """Calculate table bounding box"""
        if not columns or not spans:
            return {"x": 0, "y": 0, "width": 0, "height": 0}

        table_left = min(c.x for c in columns)
        table_right = max(c.x + c.width for c in columns)
        table_top = min(s["bbox"][1] for s in spans)
        table_bottom = max(s["bbox"][3] for s in spans)

        return {
            "x": table_left,
            "y": table_top,
            "width": table_right - table_left,
            "height": table_bottom - table_top
        }

    def _sanitize_text(self, text: str) -> str:
        """Sanitize text"""
        if not text:
            return ""

        import re
        text = text.replace("\r", " ").replace("\uFEFF", "").replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{2,}", "\n", text)
        return text.strip()


def read_pdf(pdf_path: str, analyze_structure: bool = True) -> PDFContent:
    """
    Helper function to read PDF

    Args:
        pdf_path: Path to PDF file
        analyze_structure: Whether to analyze graphical structure

    Returns:
        PDFContent with all information
    """
    reader = PDFReader(pdf_path)
    return reader.read(analyze_structure=analyze_structure)
