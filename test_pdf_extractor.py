"""
Test script for pdf_extractor module.

This script demonstrates how to use the pdf_extractor module and includes
basic tests to verify functionality.
"""

import json
from pdf_extractor import extract_attendance_data, PDFExtractorError


def test_extraction():
    """Test the PDF extraction functionality."""
    print("Testing PDF Extractor...")
    
    # Test with a sample PDF file (you would replace this with an actual PDF)
    test_pdf = "sample_attendance.pdf"
    
    try:
        # Extract data
        data = extract_attendance_data(test_pdf)
        
        print(f"Successfully extracted {len(data)} records:")
        for i, record in enumerate(data, 1):
            print(f"Record {i}: {json.dumps(record, indent=2)}")
        
        return True
    
    except PDFExtractorError as e:
        print(f"Extraction failed: {e}")
        return False
    except FileNotFoundError:
        print(f"Test PDF file not found: {test_pdf}")
        print("Please provide a valid PDF file for testing.")
        return False


def test_with_different_libraries():
    """Test extraction with different PDF libraries."""
    test_pdf = "sample_attendance.pdf"
    
    libraries = ["pdfplumber", "pymupdf", "auto"]
    
    for library in libraries:
        try:
            print(f"\nTesting with {library} library...")
            data = extract_attendance_data(test_pdf, library=library)
            print(f"Successfully extracted {len(data)} records with {library}")
            
        except PDFExtractorError as e:
            print(f"Failed with {library}: {e}")
        except FileNotFoundError:
            print(f"Test PDF file not found: {test_pdf}")
            break


if __name__ == "__main__":
    print("PDF Attendance Extractor - Test Script")
    print("=" * 40)
    
    # Run basic test
    success = test_extraction()
    
    if success:
        # Test with different libraries
        test_with_different_libraries()
    
    print("\nTest completed!")