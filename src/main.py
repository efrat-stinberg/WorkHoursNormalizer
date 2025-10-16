"""
main.py
דוגמת שימוש: מריץ את כל ה-flow
"""

import logging
from pathlib import Path
from pdf_reader import extract_text_from_pdf
from analyzer import parse_report
from structure_analyzer import analyze_structure, extract_layout_json
from data_generator import generate_variation
from pdf_writer import export_to_pdf

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")
logger = logging.getLogger("main")

INPUT = "input/u.pdf"
OUTPUT = "output/vari.pdf"

def process_pdf(input_path: str = INPUT, output_path: str = OUTPUT, variation_level: str = "moderate"):
    """
    Process PDF attendance report and generate new PDF with modified data.
    
    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        variation_level: Level of data variation ("minimal", "moderate", "significant")
    """
    logger.info("Processing %s -> %s", input_path, output_path)
    
    try:
        # 1. Analyze structure and extract layout information
        logger.info("Step 1: Analyzing PDF structure...")
        layout_json = extract_layout_json(input_path, sample_pages=[0])
        structure = analyze_structure(input_path, sample_pages=[0])
        
        # 2. Extract text content
        logger.info("Step 2: Extracting text content...")
        text = extract_text_from_pdf(input_path, ocr_lang="heb+eng")
        
        # 3. Parse attendance data
        logger.info("Step 3: Parsing attendance data...")
        rows, report_type = parse_report(text)
        if not report_type and layout_json.get("report_type"):
            report_type = layout_json["report_type"]
        
        if not rows:
            logger.warning("No data rows parsed; aborting export.")
            return False
        
        logger.info(f"Parsed {len(rows)} attendance records of type: {report_type}")
        
        # 4. Generate data variations
        logger.info(f"Step 4: Generating data variations (level: {variation_level})...")
        new_rows = generate_variation(rows, level=variation_level)
        
        # 5. Generate new PDF with preserved formatting
        logger.info("Step 5: Generating new PDF with preserved formatting...")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        export_to_pdf(new_rows, layout=structure, output_path=output_path)
        
        logger.info("✅ Successfully generated PDF with preserved formatting")
        logger.info(f"Output saved to: {output_path}")
        logger.info(f"Report type: {report_type}")
        logger.info(f"Records processed: {len(new_rows)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return False

if __name__ == "__main__":
    process_pdf()
