#!/usr/bin/env python3
"""
Example usage of the Attendance PDF Generator.
Demonstrates how to use the complete solution to generate new PDFs while preserving formatting.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import process_pdf
from src.pdf_reader import extract_text_from_pdf
from src.structure_analyzer import analyze_structure, extract_layout_json
from src.data_generator import generate_variation
from src.pdf_writer import export_to_pdf
from src.analyzer import parse_report

def setup_logging():
    """Set up logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(name)s: %(message)s"
    )

def example_basic_usage():
    """Example 1: Basic usage with automatic processing."""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Example input and output paths
    input_pdf = "input/sample_attendance.pdf"  # Replace with your PDF
    output_pdf = "output/generated_attendance.pdf"
    
    print(f"Processing: {input_pdf}")
    print(f"Output: {output_pdf}")
    
    # Process the PDF with moderate variation
    success = process_pdf(
        input_path=input_pdf,
        output_path=output_pdf,
        variation_level="moderate"
    )
    
    if success:
        print("✅ PDF generated successfully!")
    else:
        print("❌ PDF generation failed!")

def example_advanced_usage():
    """Example 2: Advanced usage with custom processing."""
    print("\n" + "=" * 60)
    print("Example 2: Advanced Usage")
    print("=" * 60)
    
    input_pdf = "input/sample_attendance.pdf"  # Replace with your PDF
    output_pdf = "output/custom_attendance.pdf"
    
    try:
        # Step 1: Extract text from PDF
        print("Step 1: Extracting text from PDF...")
        text = extract_text_from_pdf(input_pdf)
        print(f"Extracted text length: {len(text)} characters")
        
        # Step 2: Analyze PDF structure
        print("Step 2: Analyzing PDF structure...")
        layout_json = extract_layout_json(input_pdf, sample_pages=[0])
        structure = analyze_structure(input_pdf, sample_pages=[0])
        
        print(f"Detected report type: {layout_json.get('report_type', 'unknown')}")
        print(f"Number of columns: {len(structure.get('columns', []))}")
        
        # Step 3: Parse attendance data
        print("Step 3: Parsing attendance data...")
        rows, report_type = parse_report(text)
        print(f"Parsed {len(rows)} attendance records")
        
        if rows:
            print("Sample record:")
            print(f"  {rows[0]}")
        
        # Step 4: Generate data variations
        print("Step 4: Generating data variations...")
        new_rows = generate_variation(rows, level="moderate")
        print(f"Generated {len(new_rows)} varied records")
        
        # Step 5: Export to PDF
        print("Step 5: Exporting to PDF...")
        Path(output_pdf).parent.mkdir(parents=True, exist_ok=True)
        export_to_pdf(new_rows, structure, output_pdf)
        print(f"✅ PDF exported to: {output_pdf}")
        
    except Exception as e:
        print(f"❌ Error in advanced processing: {e}")
        import traceback
        traceback.print_exc()

def example_custom_data():
    """Example 3: Using custom attendance data."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Data Processing")
    print("=" * 60)
    
    # Create custom attendance data
    custom_data = [
        {
            "תאריך": "01/01/2024",
            "יום": "ראשון",
            "כניסה": "08:00",
            "יציאה": "17:00",
            "הפסקה": "00:30",
            "סה\"כ": "8.50",
            "100%": "8.50",
            "125%": "0.00",
            "150%": "0.00"
        },
        {
            "תאריך": "02/01/2024",
            "יום": "שני",
            "כניסה": "08:15",
            "יציאה": "17:30",
            "הפסקה": "00:30",
            "סה\"כ": "9.00",
            "100%": "8.00",
            "125%": "1.00",
            "150%": "0.00"
        },
        {
            "תאריך": "03/01/2024",
            "יום": "שלישי",
            "כניסה": "08:30",
            "יציאה": "18:00",
            "הפסקה": "00:45",
            "סה\"כ": "8.75",
            "100%": "8.00",
            "125%": "0.75",
            "150%": "0.00"
        }
    ]
    
    # Create custom layout
    custom_layout = {
        "columns": [
            {"name": "תאריך", "x_start": 50, "width": 80, "align": "left", "font_size": 10, "font_style": "normal"},
            {"name": "יום", "x_start": 140, "width": 60, "align": "center", "font_size": 10, "font_style": "normal"},
            {"name": "כניסה", "x_start": 210, "width": 60, "align": "center", "font_size": 10, "font_style": "normal"},
            {"name": "יציאה", "x_start": 280, "width": 60, "align": "center", "font_size": 10, "font_style": "normal"},
            {"name": "סה\"כ", "x_start": 350, "width": 60, "align": "right", "font_size": 10, "font_style": "normal"},
        ],
        "page_info": {
            "dimensions_pt": {"width": 595, "height": 842},
            "margins": {"left": 50, "top": 50, "right": 50, "bottom": 50}
        },
        "row_spacing": 14.0
    }
    
    # Generate variations
    print("Generating variations of custom data...")
    varied_data = generate_variation(custom_data, level="moderate")
    
    # Export to PDF
    output_path = "output/custom_attendance.pdf"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    export_to_pdf(varied_data, custom_layout, output_path)
    
    print(f"✅ Custom PDF generated: {output_path}")
    print(f"Records processed: {len(varied_data)}")

def example_different_variation_levels():
    """Example 4: Testing different variation levels."""
    print("\n" + "=" * 60)
    print("Example 4: Different Variation Levels")
    print("=" * 60)
    
    # Sample data
    sample_data = [
        {
            "תאריך": "01/01/2024",
            "יום": "ראשון",
            "כניסה": "08:00",
            "יציאה": "17:00",
            "סה\"כ": "8.50"
        }
    ]
    
    # Test different variation levels
    levels = ["minimal", "moderate", "significant"]
    
    for level in levels:
        print(f"\nTesting variation level: {level}")
        
        # Generate variations
        varied_data = generate_variation(sample_data, level=level)
        
        # Show the variation
        original = sample_data[0]
        varied = varied_data[0]
        
        print(f"  Original: {original['כניסה']} - {original['יציאה']} ({original['סה\"כ']} hours)")
        print(f"  Varied:   {varied['כניסה']} - {varied['יציאה']} ({varied['סה\"כ']} hours)")

def main():
    """Run all examples."""
    setup_logging()
    
    print("Attendance PDF Generator - Usage Examples")
    print("=" * 60)
    
    # Run examples
    example_custom_data()
    example_different_variation_levels()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nTo use with your own PDFs:")
    print("1. Place your PDF in the 'input/' directory")
    print("2. Update the input_pdf path in the examples")
    print("3. Run the examples or use process_pdf() directly")
    print("\nExample:")
    print("  success = process_pdf('input/your_file.pdf', 'output/new_file.pdf')")

if __name__ == "__main__":
    main()