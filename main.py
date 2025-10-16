import logging
from src.pdf_reader import extract_text_from_pdf
from src.analyzer import parse_report
from src.structure_analyzer import analyze_structure
from src.data_generator import create_variation
from src.pdf_writer import create_pdf as export_to_pdf


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s")

pdf_path = "input/u.pdf"

# 1️⃣ ניתוח מבנה PDF
structure = analyze_structure(pdf_path, sample_pages=[0, 1])

# 2️⃣ חילוץ טקסט
text = extract_text_from_pdf(pdf_path)

# 3️⃣ פירוק לשורות נתונים
data, report_type = parse_report(text)

# 4️⃣ יצירת גרסה מחודשת
new_data = create_variation(data)

# 5️⃣ כתיבה חזרה ל-PDF
export_to_pdf(output_path="output/variant.pdf", data=new_data, flip_text=True)
