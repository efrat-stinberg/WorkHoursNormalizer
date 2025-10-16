#!/usr/bin/env python3
"""
Test script for the attendance PDF generator.
Tests the complete pipeline from PDF analysis to new PDF generation.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import process_pdf
from src.utils import clean_text

def setup_logging():
    """Set up logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(name)s: %(message)s"
    )

def create_sample_data():
    """Create sample attendance data for testing."""
    sample_data = [
        {
            "תאריך": "01/01/2024",
            "יום": "ראשון",
            "נ\"ב": "001",
            "זמן עו": "08:00",
            "כניסה": "08:00",
            "יציאה": "17:00",
            "הפסקה": "00:30",
            "סה\"כ": "8.50",
            "100%": "8.50",
            "125%": "0.00",
            "150%": "0.00",
            "שבת": "0.00"
        },
        {
            "תאריך": "02/01/2024",
            "יום": "שני",
            "נ\"ב": "002",
            "זמן עו": "08:00",
            "כניסה": "08:15",
            "יציאה": "17:30",
            "הפסקה": "00:30",
            "סה\"כ": "9.00",
            "100%": "8.00",
            "125%": "1.00",
            "150%": "0.00",
            "שבת": "0.00"
        },
        {
            "תאריך": "03/01/2024",
            "יום": "שלישי",
            "נ\"ב": "003",
            "זמן עו": "08:00",
            "כניסה": "08:30",
            "יציאה": "18:00",
            "הפסקה": "00:45",
            "סה\"כ": "8.75",
            "100%": "8.00",
            "125%": "0.75",
            "150%": "0.00",
            "שבת": "0.00"
        }
    ]
    return sample_data

def test_pdf_generation():
    """Test PDF generation with sample data."""
    print("Testing PDF generation...")
    
    # Create sample data
    sample_data = create_sample_data()
    
    # Test with different variation levels
    variation_levels = ["minimal", "moderate", "significant"]
    
    for level in variation_levels:
        print(f"\nTesting with variation level: {level}")
        
        # Create output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate test PDF
        output_path = output_dir / f"test_attendance_{level}.pdf"
        
        try:
            # Create a simple layout for testing
            layout = {
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
            
            # Import and use the PDF writer directly
            from src.pdf_writer import export_to_pdf
            from src.data_generator import generate_variation
            
            # Generate variations
            varied_data = generate_variation(sample_data, level=level)
            
            # Export to PDF
            export_to_pdf(varied_data, layout, str(output_path))
            
            print(f"✅ Generated PDF: {output_path}")
            print(f"   Records: {len(varied_data)}")
            
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            import traceback
            traceback.print_exc()

def test_font_handling():
    """Test font handling and Hebrew text processing."""
    print("\nTesting font handling...")
    
    try:
        from src.font_manager import font_manager
        
        # Test Hebrew text processing
        hebrew_text = "שלום עולם"
        processed_text = font_manager.process_hebrew_text(hebrew_text)
        print(f"Hebrew text processing: '{hebrew_text}' -> '{processed_text}'")
        
        # Test font detection
        available_fonts = font_manager.get_available_fonts()
        print(f"Available fonts: {available_fonts}")
        
        # Test font name resolution
        font_info = {"font": "Arial", "styles": {"bold": True}}
        font_name = font_manager.get_font_name(font_info)
        print(f"Font name resolution: {font_info} -> {font_name}")
        
        print("✅ Font handling test passed")
        
    except Exception as e:
        print(f"❌ Font handling test failed: {e}")
        import traceback
        traceback.print_exc()

def test_data_generation():
    """Test data generation and variation."""
    print("\nTesting data generation...")
    
    try:
        from src.data_generator import generate_variation
        
        sample_data = create_sample_data()
        
        # Test different variation levels
        for level in ["minimal", "moderate", "significant"]:
            varied_data = generate_variation(sample_data, level=level)
            print(f"Variation level '{level}': {len(varied_data)} records")
            
            # Show first record
            if varied_data:
                first_record = varied_data[0]
                print(f"  First record: {first_record}")
        
        print("✅ Data generation test passed")
        
    except Exception as e:
        print(f"❌ Data generation test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    setup_logging()
    
    print("=" * 60)
    print("Attendance PDF Generator - Test Suite")
    print("=" * 60)
    
    # Test individual components
    test_font_handling()
    test_data_generation()
    test_pdf_generation()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()