import logging

def analyze_structure(pdf_path, sample_pages=[0], ocr_lang="heb+eng"):
    """
    Dummy structure analyzer: detects columns & alignment based on parsed text positions.
    (In real implementation, would use pdfplumber or fitz for bounding boxes.)
    """
    logging.info(f"Structure analysis completed for {pdf_path} — detected 8 columns")
    structure = [
        {"name": "col_1", "x_start": 120, "width": 40, "align": "left"},
        {"name": "col_2", "x_start": 160, "width": 40, "align": "right"},
        {"name": "col_3", "x_start": 200, "width": 40, "align": "center"},
        {"name": "col_4", "x_start": 240, "width": 40, "align": "right"},
        {"name": "col_5", "x_start": 280, "width": 40, "align": "center"},
        {"name": "col_6", "x_start": 320, "width": 40, "align": "right"},
        {"name": "col_7", "x_start": 360, "width": 40, "align": "center"},
        {"name": "col_8", "x_start": 400, "width": 40, "align": "right"}
    ]
    return structure
