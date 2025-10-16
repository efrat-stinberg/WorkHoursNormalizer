"""
PDF Attendance Data Extractor

This module provides functionality to extract attendance data from PDF files.
It supports both pdfplumber and PyMuPDF libraries for PDF parsing.

Example:
    from pdf_extractor import extract_attendance_data
    
    data = extract_attendance_data('attendance.pdf')
    print(data)
    # Output: [{"date": "2024-05-01", "start": "08:00", "end": "17:00", "break": "00:30"}]
"""

import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Union
from pathlib import Path

# Try to import PDF libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractorError(Exception):
    """Custom exception for PDF extraction errors."""
    pass


class AttendanceExtractor:
    """Main class for extracting attendance data from PDF files."""
    
    def __init__(self, library: str = "auto"):
        """
        Initialize the extractor.
        
        Args:
            library: PDF library to use ("pdfplumber", "pymupdf", or "auto")
        """
        self.library = library
        self._validate_library()
    
    def _validate_library(self):
        """Validate that the requested library is available."""
        if self.library == "pdfplumber" and not PDFPLUMBER_AVAILABLE:
            raise PDFExtractorError("pdfplumber is not installed. Install with: pip install pdfplumber")
        elif self.library == "pymupdf" and not PYMUPDF_AVAILABLE:
            raise PDFExtractorError("PyMuPDF is not installed. Install with: pip install PyMuPDF")
        elif self.library == "auto":
            if not PDFPLUMBER_AVAILABLE and not PYMUPDF_AVAILABLE:
                raise PDFExtractorError("Neither pdfplumber nor PyMuPDF is installed. Install at least one.")
    
    def _get_library(self) -> str:
        """Get the library to use for extraction."""
        if self.library == "auto":
            if PDFPLUMBER_AVAILABLE:
                return "pdfplumber"
            elif PYMUPDF_AVAILABLE:
                return "pymupdf"
        return self.library
    
    def extract_from_pdfplumber(self, pdf_path: Union[str, Path]) -> List[Dict[str, str]]:
        """Extract attendance data using pdfplumber."""
        attendance_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}")
                    text = page.extract_text()
                    
                    if text:
                        page_data = self._parse_text_for_attendance(text)
                        attendance_data.extend(page_data)
        
        except Exception as e:
            logger.error(f"Error processing PDF with pdfplumber: {e}")
            raise PDFExtractorError(f"Failed to extract data with pdfplumber: {e}")
        
        return attendance_data
    
    def extract_from_pymupdf(self, pdf_path: Union[str, Path]) -> List[Dict[str, str]]:
        """Extract attendance data using PyMuPDF."""
        attendance_data = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                logger.info(f"Processing page {page_num + 1}")
                page = doc[page_num]
                text = page.get_text()
                
                if text:
                    page_data = self._parse_text_for_attendance(text)
                    attendance_data.extend(page_data)
            
            doc.close()
        
        except Exception as e:
            logger.error(f"Error processing PDF with PyMuPDF: {e}")
            raise PDFExtractorError(f"Failed to extract data with PyMuPDF: {e}")
        
        return attendance_data
    
    def _parse_text_for_attendance(self, text: str) -> List[Dict[str, str]]:
        """
        Parse text content to extract attendance data.
        
        This method looks for patterns like:
        - Date: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY
        - Time: HH:MM format (24-hour or 12-hour with AM/PM)
        - Keywords: start, end, break, lunch, etc.
        """
        attendance_records = []
        
        # Split text into lines for processing
        lines = text.split('\n')
        
        # Patterns for different date formats
        date_patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
            r'\b(\d{1,2}/\d{1,2}/\d{4})\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b(\d{1,2}-\d{1,2}-\d{4})\b',  # MM-DD-YYYY or DD-MM-YYYY
        ]
        
        # Patterns for time formats
        time_patterns = [
            r'\b(\d{1,2}:\d{2})\s*(AM|PM|am|pm)?\b',  # HH:MM with optional AM/PM
            r'\b(\d{1,2}:\d{2})\b',  # HH:MM
        ]
        
        current_record = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for date patterns
            for pattern in date_patterns:
                date_match = re.search(pattern, line)
                if date_match:
                    date_str = date_match.group(1)
                    # If we have a previous record, save it
                    if current_record and self._is_valid_record(current_record):
                        attendance_records.append(current_record.copy())
                    current_record = {"date": self._normalize_date(date_str)}
                    break
            
            # Look for time patterns with context
            for pattern in time_patterns:
                time_matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in time_matches:
                    time_str = match.group(1)
                    am_pm = match.group(2) if len(match.groups()) > 1 else None
                    normalized_time = self._normalize_time(time_str, am_pm)
                    
                    # Determine time type based on context
                    context = line.lower()
                    if any(keyword in context for keyword in ['start', 'in', 'arrive', 'begin']):
                        current_record['start'] = normalized_time
                    elif any(keyword in context for keyword in ['end', 'out', 'leave', 'finish']):
                        current_record['end'] = normalized_time
                    elif any(keyword in context for keyword in ['break', 'lunch', 'rest']):
                        current_record['break'] = normalized_time
        
        # Add the last record if valid
        if current_record and self._is_valid_record(current_record):
            attendance_records.append(current_record)
        
        return attendance_records
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format."""
        try:
            # Try different date formats
            formats = [
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%m-%d-%Y',
                '%d-%m-%Y',
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return as is
            logger.warning(f"Could not parse date: {date_str}")
            return date_str
        
        except Exception as e:
            logger.warning(f"Error normalizing date {date_str}: {e}")
            return date_str
    
    def _normalize_time(self, time_str: str, am_pm: Optional[str] = None) -> str:
        """Normalize time string to HH:MM format (24-hour)."""
        try:
            # Parse time
            if ':' in time_str:
                hour, minute = time_str.split(':')
                hour = int(hour)
                minute = int(minute)
            else:
                # Handle formats like "8" or "08"
                hour = int(time_str)
                minute = 0
            
            # Handle AM/PM
            if am_pm and am_pm.upper() == 'PM' and hour != 12:
                hour += 12
            elif am_pm and am_pm.upper() == 'AM' and hour == 12:
                hour = 0
            
            # Ensure valid time range
            hour = max(0, min(23, hour))
            minute = max(0, min(59, minute))
            
            return f"{hour:02d}:{minute:02d}"
        
        except Exception as e:
            logger.warning(f"Error normalizing time {time_str}: {e}")
            return time_str
    
    def _is_valid_record(self, record: Dict[str, str]) -> bool:
        """Check if a record has the minimum required fields."""
        return 'date' in record and ('start' in record or 'end' in record)
    
    def extract(self, pdf_path: Union[str, Path]) -> List[Dict[str, str]]:
        """
        Extract attendance data from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing attendance data
            
        Raises:
            PDFExtractorError: If extraction fails
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise PDFExtractorError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise PDFExtractorError(f"File is not a PDF: {pdf_path}")
        
        library = self._get_library()
        logger.info(f"Using {library} to extract data from {pdf_path}")
        
        if library == "pdfplumber":
            return self.extract_from_pdfplumber(pdf_path)
        elif library == "pymupdf":
            return self.extract_from_pymupdf(pdf_path)
        else:
            raise PDFExtractorError(f"Unknown library: {library}")


def extract_attendance_data(pdf_path: Union[str, Path], library: str = "auto") -> List[Dict[str, str]]:
    """
    Convenience function to extract attendance data from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        library: PDF library to use ("pdfplumber", "pymupdf", or "auto")
        
    Returns:
        List of dictionaries containing attendance data
        
    Example:
        >>> data = extract_attendance_data('attendance.pdf')
        >>> print(data)
        [{"date": "2024-05-01", "start": "08:00", "end": "17:00", "break": "00:30"}]
    """
    extractor = AttendanceExtractor(library=library)
    return extractor.extract(pdf_path)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pdf_extractor.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    try:
        data = extract_attendance_data(pdf_file)
        print(f"Extracted {len(data)} attendance records:")
        for record in data:
            print(record)
    except PDFExtractorError as e:
        print(f"Error: {e}")
        sys.exit(1)