"""
main.py
דוגמת שימוש: מריץ את כל ה-flow
"""

import logging
from pathlib import Path
from pdf_reader import extract_text_from_pdf
from analyzer import parse_report
from structure_analyzer import analyze_structure, extract_layout_json
from data_generator import create_variation
from pdf_writer import create_pdf

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger("main")

INPUT = "input/a_r_9.pdf"
OUTPUT = "output/va.pdf"

def process_pdf(input_path: str = INPUT, output_path: str = OUTPUT, variation_level: str = "moderate"):
    logger.info("Processing %s -> %s", input_path, output_path)
    # 1. analyze structure (sample first page) and full layout JSON
    layout_json = extract_layout_json(input_path, sample_pages=[0])
    structure = analyze_structure(input_path, sample_pages=[0])
    # 2. extract text (OCR fallback if needed)
    text = extract_text_from_pdf(input_path)
    # 3. parse into rows
    rows, report_type = parse_report(text)
    if not report_type and layout_json.get("report_type"):
        report_type = layout_json["report_type"]
    if not rows:
        logger.warning("No data rows parsed; aborting export.")
        return
    # 4. generate variation
    new_rows = create_variation(rows)
    # 5. write pdf
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    create_pdf(output_path, new_rows, flip_text=True)
    logger.info("Layout JSON: %s", layout_json)
    logger.info("Done. Output at %s", output_path)


if __name__ == "__main__":
    process_pdf()
