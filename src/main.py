"""
main.py
דוגמת שימוש: מריץ את כל ה-flow
"""

import logging
from pathlib import Path
from pdf_reader import extract_text_from_pdf
from analyzer import parse_report
from structure_analyzer import analyze_structure
from data_generator import generate_variation
from pdf_writer import export_to_pdf

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger("main")

INPUT = "input/u.pdf"
OUTPUT = "output/vari.pdf"

def process_pdf(input_path: str = INPUT, output_path: str = OUTPUT, variation_level: str = "moderate"):
    logger.info("Processing %s -> %s", input_path, output_path)
    # 1. analyze structure (sample first page)
    structure = analyze_structure(input_path, sample_pages=[0])
    # 2. extract text (OCR fallback if needed)
    text = extract_text_from_pdf(input_path, ocr_lang="heb+eng")
    # 3. parse into rows
    rows, report_type = parse_report(text)
    if not rows:
        logger.warning("No data rows parsed; aborting export.")
        return
    # 4. generate variation
    new_rows = generate_variation(rows, level=variation_level)
    # 5. write pdf
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    export_to_pdf(new_rows, layout=structure, output_path=output_path)
    logger.info("Done. Output at %s", output_path)

if __name__ == "__main__":
    process_pdf()
