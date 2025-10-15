# pdf_reader.py
# This module extracts text from PDFs.
# It supports both text-based PDFs and scanned PDFs (images).

from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    If the PDF is scanned, use OCR (Tesseract).

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text.
    """
    # Step 1: Try reading as a text PDF
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    # Step 2: If text is too short, assume scanned PDF and use OCR
    if len(text.strip()) < 50:  # threshold for scanned PDF
        text = ""
        pages = convert_from_path(pdf_path)
        for page in pages:
            text += pytesseract.image_to_string(page, lang="heb+eng")  # Hebrew + English

    return text
