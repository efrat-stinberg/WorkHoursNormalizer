# Attendance PDF Generator - Complete Solution

This solution provides a comprehensive Python-based system for generating new PDF attendance reports while preserving the exact layout and formatting of the original PDF.

## Features

- **Exact Layout Preservation**: Maintains original PDF structure, fonts, positioning, and formatting
- **Multi-language Support**: Handles Hebrew and English text with proper RTL processing
- **Intelligent Data Variation**: Generates realistic attendance data variations
- **Automatic Structure Detection**: Analyzes input PDFs to detect column structure and formatting
- **Font Management**: Automatic font detection and registration for proper text rendering
- **Flexible Output**: Supports different variation levels (minimal, moderate, significant)

## Architecture

### Core Components

1. **PDF Reader** (`src/pdf_reader.py`): Extracts text content from PDF files
2. **Structure Analyzer** (`src/structure_analyzer.py`): Analyzes PDF layout and structure
3. **Data Generator** (`src/data_generator.py`): Creates realistic attendance data variations
4. **PDF Writer** (`src/pdf_writer.py`): Generates new PDFs with preserved formatting
5. **Font Manager** (`src/font_manager.py`): Handles font detection and RTL text processing
6. **Main Processor** (`src/main.py`): Orchestrates the complete pipeline

### Key Improvements Made

1. **Enhanced PDF Writer**:
   - Preserves exact column positions and widths
   - Maintains original font sizes and styles
   - Handles proper text alignment
   - Supports RTL text processing for Hebrew content

2. **Improved Structure Analysis**:
   - Detects page dimensions and margins
   - Analyzes column structure and positioning
   - Identifies font information and styles
   - Extracts row spacing and table boundaries

3. **Realistic Data Generation**:
   - Generates logical time variations
   - Calculates realistic break times
   - Handles overtime percentages correctly
   - Maintains data consistency

4. **Comprehensive Font Handling**:
   - Automatic font detection and registration
   - Support for Hebrew and English fonts
   - Proper RTL text processing
   - Fallback font management

## Usage

### Basic Usage

```python
from src.main import process_pdf

# Process a PDF file
success = process_pdf(
    input_path="input/attendance.pdf",
    output_path="output/new_attendance.pdf",
    variation_level="moderate"
)
```

### Advanced Usage

```python
from src.pdf_reader import extract_text_from_pdf
from src.structure_analyzer import analyze_structure
from src.data_generator import generate_variation
from src.pdf_writer import export_to_pdf

# Step 1: Extract text
text = extract_text_from_pdf("input/attendance.pdf")

# Step 2: Analyze structure
layout = analyze_structure("input/attendance.pdf")

# Step 3: Parse data (custom implementation)
# ... parse your data ...

# Step 4: Generate variations
new_data = generate_variation(original_data, level="moderate")

# Step 5: Export to PDF
export_to_pdf(new_data, layout, "output/new_attendance.pdf")
```

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure font files are available (optional):
   - Place Arial.ttf in the project root
   - Or use system fonts (automatically detected)

## Configuration

### Variation Levels

- **minimal**: Small time variations (±5 minutes)
- **moderate**: Medium variations (±15 minutes) - Default
- **significant**: Large variations (±30 minutes)

### Font Support

The system automatically detects and uses available fonts:
- Arial (preferred)
- Liberation Sans
- DejaVu Sans
- Times Roman
- Courier

## File Structure

```
workspace/
├── src/
│   ├── main.py                 # Main processing pipeline
│   ├── pdf_reader.py          # PDF text extraction
│   ├── pdf_writer.py          # PDF generation with preserved formatting
│   ├── structure_analyzer.py  # PDF structure analysis
│   ├── data_generator.py      # Realistic data variation generation
│   ├── font_manager.py        # Font detection and RTL processing
│   ├── analyzer.py            # Data parsing utilities
│   └── utils.py               # Common utilities
├── output/                    # Generated PDFs
├── requirements.txt           # Python dependencies
└── test_attendance_generator.py # Test suite
```

## Testing

Run the test suite to validate the solution:

```bash
python test_attendance_generator.py
```

This will test:
- Font handling and Hebrew text processing
- Data generation and variation
- PDF generation with different variation levels

## Key Features

### 1. Exact Layout Preservation
- Maintains original column positions and widths
- Preserves font sizes, styles, and alignment
- Keeps original page dimensions and margins
- Maintains row spacing and table structure

### 2. Hebrew Text Support
- Proper RTL text processing
- Automatic font detection for Hebrew content
- Bidirectional text algorithm support
- Arabic text reshaping

### 3. Realistic Data Generation
- Logical time variations
- Realistic break time calculations
- Proper overtime percentage handling
- Date and day-of-week generation

### 4. Robust Error Handling
- Graceful fallbacks for missing fonts
- Error recovery for malformed data
- Comprehensive logging
- Validation of input parameters

## Dependencies

- `reportlab>=4.0.0`: PDF generation
- `PyMuPDF>=1.23.0`: PDF analysis
- `pdfplumber>=0.9.0`: Alternative PDF processing
- `python-bidi>=0.4.2`: RTL text processing
- `arabic-reshaper>=3.0.0`: Arabic/Hebrew text reshaping
- `python-dateutil>=2.8.0`: Date/time processing

## Notes

- The solution is designed to work with various PDF attendance report formats
- Automatic detection of report types (Hebrew/English)
- Support for both portrait and landscape orientations
- Handles multiple page layouts
- Preserves original formatting completely

This solution provides a robust, production-ready system for generating attendance PDFs while maintaining the exact visual appearance of the original documents.