# PDF Attendance Data Extractor

A Python module for extracting structured attendance data from PDF files. Supports both pdfplumber and PyMuPDF libraries for robust PDF processing.

## Features

- **Multiple PDF Libraries**: Supports both pdfplumber and PyMuPDF
- **Flexible Date/Time Parsing**: Handles various date and time formats
- **Structured Output**: Returns data as a list of dictionaries
- **Error Handling**: Comprehensive error handling and logging
- **Easy to Use**: Simple API with automatic library selection

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from pdf_extractor import extract_attendance_data

# Extract attendance data from PDF
data = extract_attendance_data('attendance.pdf')
print(data)
# Output: [{"date": "2024-05-01", "start": "08:00", "end": "17:00", "break": "00:30"}]
```

## Usage

### Basic Usage

```python
from pdf_extractor import extract_attendance_data

# Extract with automatic library selection
data = extract_attendance_data('attendance.pdf')

# Extract with specific library
data = extract_attendance_data('attendance.pdf', library='pdfplumber')
data = extract_attendance_data('attendance.pdf', library='pymupdf')
```

### Advanced Usage

```python
from pdf_extractor import AttendanceExtractor

# Create extractor instance
extractor = AttendanceExtractor(library='pdfplumber')

# Extract data
data = extractor.extract('attendance.pdf')

# Process the data
for record in data:
    print(f"Date: {record['date']}")
    print(f"Start: {record.get('start', 'N/A')}")
    print(f"End: {record.get('end', 'N/A')}")
    print(f"Break: {record.get('break', 'N/A')}")
    print("-" * 20)
```

### Command Line Usage

```bash
python pdf_extractor.py attendance.pdf
```

## Output Format

The module returns a list of dictionaries with the following structure:

```python
[
    {
        "date": "2024-05-01",      # Date in YYYY-MM-DD format
        "start": "08:00",          # Start time in HH:MM format (24-hour)
        "end": "17:00",            # End time in HH:MM format (24-hour)
        "break": "00:30"           # Break duration (optional)
    },
    # ... more records
]
```

## Supported Formats

### Date Formats
- YYYY-MM-DD (2024-05-01)
- MM/DD/YYYY (05/01/2024)
- DD/MM/YYYY (01/05/2024)
- MM-DD-YYYY (05-01-2024)
- DD-MM-YYYY (01-05-2024)

### Time Formats
- HH:MM (24-hour: 08:00, 17:30)
- HH:MM AM/PM (12-hour: 8:00 AM, 5:30 PM)

### Keywords
The parser looks for context keywords to identify time types:
- **Start time**: start, in, arrive, begin
- **End time**: end, out, leave, finish
- **Break time**: break, lunch, rest

## Error Handling

The module includes comprehensive error handling:

```python
from pdf_extractor import extract_attendance_data, PDFExtractorError

try:
    data = extract_attendance_data('attendance.pdf')
except PDFExtractorError as e:
    print(f"Extraction failed: {e}")
except FileNotFoundError:
    print("PDF file not found")
```

## Testing

Run the test script to verify functionality:

```bash
python test_pdf_extractor.py
```

## Dependencies

- `pdfplumber>=0.9.0` - PDF text extraction
- `PyMuPDF>=1.23.0` - Alternative PDF processing
- `python-dateutil>=2.8.0` - Date parsing utilities

## License

This project is open source and available under the MIT License.