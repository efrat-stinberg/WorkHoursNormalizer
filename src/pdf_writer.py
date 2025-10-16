# pdf_writer.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter, legal
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.colors import black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from typing import List, Dict, Any, Optional
import logging
import os
from font_manager import font_manager

logger = logging.getLogger(__name__)

def reverse_text_preserve_rtl(text: str) -> str:
    """
    Reverse letters in text, preserving RTL for Hebrew/Arabic.
    """
    if not text:
        return text
    return font_manager.process_hebrew_text(text)

def get_page_size(page_info: Dict[str, Any]) -> tuple:
    """Get page size tuple from page info."""
    size_name = page_info.get("page_size", "A4")
    orientation = page_info.get("orientation", "portrait")
    
    size_map = {
        "A4": A4,
        "Letter": letter,
        "Legal": legal
    }
    
    width, height = size_map.get(size_name, A4)
    
    if orientation == "landscape":
        return (height, width)
    return (width, height)

def get_font_name(font_info: Dict[str, Any]) -> str:
    """Get appropriate font name from font info."""
    font_name = font_info.get("font", "").lower()
    
    # Map common font names to available fonts
    if "arial" in font_name or "helvetica" in font_name:
        return "Arial"
    elif "times" in font_name:
        return "Times-Roman"
    elif "courier" in font_name or "monospace" in font_name:
        return "Courier"
    else:
        return "Arial"  # Default fallback

def is_hebrew_text(text: str) -> bool:
    """Check if text contains Hebrew characters."""
    return font_manager.is_hebrew_text(text)

def export_to_pdf(data: List[Dict[str, Any]], layout: Dict[str, Any], output_path: str):
    """
    Create a PDF from structured data while preserving exact layout and formatting.
    
    Args:
        data: List of rows (dicts) with column names as keys
        layout: Layout information from structure analyzer
        output_path: Path to save the PDF
    """
    if not data:
        logger.warning("No data to export")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Extract page information
    page_info = layout.get("page_info", {})
    page_width = page_info.get("dimensions_pt", {}).get("width", 595)
    page_height = page_info.get("dimensions_pt", {}).get("height", 842)
    
    # Create canvas
    c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
    
    # Set up margins
    margins = page_info.get("margins", {})
    margin_left = margins.get("left", 50)
    margin_top = margins.get("top", 50)
    margin_bottom = margins.get("bottom", 50)
    
    current_y = page_height - margin_top
    
    # Extract headers from first row
    headers = list(data[0].keys()) if data else []
    
    # Get column information
    columns = layout.get("columns", [])
    if not columns:
        # Fallback: distribute columns evenly
        col_width = (page_width - margin_left - margins.get("right", 50)) / len(headers)
        for i, header in enumerate(headers):
            columns.append({
                'name': header,
                'x_start': margin_left + i * col_width,
                'width': col_width,
                'align': 'left',
                'font_size': 10,
                'font_style': 'normal'
            })
    
    # Draw headers with proper formatting
    for i, col in enumerate(columns):
        if i < len(headers):
            header_text = headers[i]
            if is_hebrew_text(header_text):
                header_text = reverse_text_preserve_rtl(header_text)
            
            # Get font information
            font_name = font_manager.get_font_name({
                'font': 'Arial',
                'styles': {'bold': col.get('font_style') == 'bold'}
            })
            font_size = col.get('font_size', 10)
            
            c.setFont(font_name, font_size)
            
            # Calculate text position based on alignment
            text_x = col['x_start']
            if col['align'] == 'center':
                text_x += col['width'] / 2
            elif col['align'] == 'right':
                text_x += col['width']
            
            c.drawString(text_x, current_y, header_text)
    
    # Get row spacing
    row_spacing = layout.get("row_spacing", 14.0)
    current_y -= row_spacing
    
    # Draw data rows
    for row in data:
        for i, col in enumerate(columns):
            if i < len(headers) and headers[i] in row:
                value = str(row[headers[i]])
                if is_hebrew_text(value):
                    value = reverse_text_preserve_rtl(value)
                
                # Get font information
                font_name = font_manager.get_font_name({
                    'font': 'Arial',
                    'styles': {'bold': col.get('font_style') == 'bold'}
                })
                font_size = col.get('font_size', 10)
                
                c.setFont(font_name, font_size)
                
                # Calculate text position based on alignment
                text_x = col['x_start']
                if col['align'] == 'center':
                    text_x += col['width'] / 2
                elif col['align'] == 'right':
                    text_x += col['width']
                
                c.drawString(text_x, current_y, value)
        
        current_y -= row_spacing
        
        # Check if we need a new page
        if current_y < margin_bottom:
            c.showPage()
            current_y = page_height - margin_top
    
    c.save()
    logger.info(f"✅ PDF saved to {output_path}")

def create_pdf(output_path: str, data: List[Dict[str, Any]], flip_text: bool = False):
    """
    Legacy function for backward compatibility.
    """
    # Create a simple layout for backward compatibility
    layout = []
    if data:
        headers = list(data[0].keys())
        col_width = 100
        for i, header in enumerate(headers):
            layout.append({
                'name': header,
                'x_start': 50 + i * col_width,
                'width': col_width,
                'align': 'left'
            })
    
    export_to_pdf(data, layout, output_path)


# --- Example usage ---
if __name__ == "__main__":
    sample_data = [
        {"תאריך": "01/01/2024", "יום": "ראשון", "סה\"כ": 8},
        {"תאריך": "02/01/2024", "יום": "שני", "סה\"כ": 7.5},
        {"תאריך": "03/01/2024", "יום": "שלישי", "סה\"כ": 9},
    ]
    create_pdf("output/flipped_table.pdf", sample_data, flip_text=True)
