from PyPDF2 import PdfReader
# OCR disabled for now but structure is ready
# from pdf2image import convert_from_path
# import pytesseract
from src.utils import sanitize_text


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    If scanned, fallback to OCR (currently disabled).
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    text = sanitize_text(text)
    return text
