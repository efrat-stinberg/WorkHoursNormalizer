import re

from src.utils import clean_text


def parse_report(text):
    """
    Parse attendance report (Hebrew type) into structured data.
    """

    text = clean_text(text)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    merged_lines = []
    buffer = ""
    for line in lines:
        if re.match(r"^\d{2}/\d{2}/\d{4}", line):
            if buffer:
                merged_lines.append(buffer.strip())
            buffer = line
        else:
            buffer += " " + line
    if buffer:
        merged_lines.append(buffer.strip())

    headers = ["תאריך", "יום", "נ\"ב", "זמן עו", "כניסה", "יציאה", "הפסקה",
               "סה\"כ", "100%", "125%", "150%", "שבת"]
    data = []

    for line in merged_lines:
        match = re.match(
            r"(\d{2}/\d{2}/\d{4})\s+(\S+)\s+(\S+)?\s+(\S+)?\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})?\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
            line)
        if match:
            values = list(match.groups())
            entry = dict(zip(headers, values))
            data.append(entry)

    print(f"\n✅ זוהו {len(data)} שורות פעילות")
    return data, "attendance_type_hebrew"
