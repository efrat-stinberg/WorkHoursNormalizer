# analyzer.py
# This module parses extracted text into structured data
# and identifies the report type.

import re


def parse_report(text):
    """
    Parse text from a PDF into structured data and identify report type.

    Args:
        text (str): Raw text extracted from PDF.

    Returns:
        tuple:
            data (list of dict): Structured data with columns like date, start, end, total_hours
            report_type (str): Type of report ('type1' or 'type2')
    """
    lines = text.splitlines()
    data = []

    # Step 1: Identify report type based on keywords or header structure
    if "Start" in text and "End" in text:  # Example: type1 has Start/End columns
        report_type = "type1"
    elif "Check-in" in text and "Check-out" in text:  # Example: type2
        report_type = "type2"
    else:
        report_type = "unknown"

    # Step 2: Parse each line into columns (simplified example)
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Example parsing based on spaces or known column patterns
        if report_type == "type1":
            # Assuming format: Date Start End Total
            match = re.match(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})\s+([\d.]+)", line)
            if match:
                date, start, end, total = match.groups()
                data.append({
                    "date": date,
                    "start": start,
                    "end": end,
                    "total_hours": float(total)
                })
        elif report_type == "type2":
            # Different parsing rules for type2
            match = re.match(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})", line)
            if match:
                date, check_in, check_out = match.groups()
                data.append({
                    "date": date,
                    "check_in": check_in,
                    "check_out": check_out
                })

    return data, report_type
