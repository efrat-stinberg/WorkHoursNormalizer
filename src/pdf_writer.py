# pdf_writer.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from bidi.algorithm import get_display
import arabic_reshaper
from typing import List, Dict, Any

# Register font (ensure arial.ttf is available)
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

def reverse_text_preserve_rtl(text: str) -> str:
    """
    Reverse letters in text, preserving RTL for Hebrew/Arabic.
    """
    if any("\u0590" <= c <= "\u05FF" for c in text):  # Hebrew range
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    else:
        return text

def create_pdf(output_path: str, data: List[Dict[str, Any]], flip_text: bool = False):
    """
    Create a PDF from structured data.
    Optionally flip all text and handle Hebrew RTL.

    Args:
        output_path (str): Path to save the PDF.
        data (List[Dict]): List of rows (dicts) with column names as keys.
        flip_text (bool): If True, reverse all text and handle Hebrew RTL.
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    c.setFont("Arial", 8)

    # Extract headers from first row
    headers = list(data[0].keys()) if data else []
    y = height - 50

    # Draw headers
    for i, header in enumerate(headers):
        text = reverse_text_preserve_rtl(header) if flip_text else header
        c.drawString(50 + i * 100, y, text)
    y -= 20

    # Draw rows
    for row in data:
        for i, header in enumerate(headers):
            value = str(row[header])
            text = reverse_text_preserve_rtl(value) if flip_text else value
            c.drawString(25 + i * 100, y, text)
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont("Arial", 12)
            y = height - 30

    c.save()
    print(f"✅ PDF saved to {output_path} (flip_text={flip_text})")


# --- Example usage ---
# if __name__ == "__main__":
#     sample_data = [
#         {"תאריך": "01/01/2024", "יום": "ראשון", "סה\"כ": 8},
#         {"תאריך": "02/01/2024", "יום": "שני", "סה\"כ": 7.5},
#         {"תאריך": "03/01/2024", "יום": "שלישי", "סה\"כ": 9},
#     ]
#     create_pdf("output/flipped_table.pdf", sample_data, flip_text=True)
