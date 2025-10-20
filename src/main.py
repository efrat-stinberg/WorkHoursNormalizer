"""
main.py - Main Entry Point
Primary entry point for the attendance report processing system
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Import enhanced modules
from pdf_reader import read_pdf
from attendance_parser import parse_attendance_report
from data_generator import create_variation, VariationLevel
from pdf_writer import write_pdf

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


class AttendanceReportProcessor:
    """Main processor for attendance reports"""

    def __init__(self):
        self.pdf_content = None
        self.parsed_report = None
        self.varied_report = None

    def process(self,
                input_path: str,
                output_path: str,
                variation_level: str = VariationLevel.MODERATE,
                preserve_layout: bool = True) -> bool:
        """
        Full processing of an attendance report

        Args:
            input_path: Input PDF file path
            output_path: Output PDF file path
            variation_level: Variation level (minimal/moderate/significant)
            preserve_layout: Preserve original layout

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("="*70)
            logger.info(f"Starting processing: {input_path} → {output_path}")
            logger.info("="*70)

            # Step 1: Read PDF
            logger.info("📖 Step 1/4: Reading PDF and analyzing structure...")
            self.pdf_content = self._read_pdf(input_path)
            if not self.pdf_content:
                return False

            # Step 2: Parse data
            logger.info("🔍 Step 2/4: Parsing attendance data...")
            self.parsed_report = self._parse_report()
            if not self.parsed_report:
                return False

            # Step 3: Generate variation
            logger.info(f"🔄 Step 3/4: Generating variation (level: {variation_level})...")
            self.varied_report = self._create_variation(variation_level)
            if not self.varied_report:
                return False

            # Step 4: Write PDF
            logger.info("📝 Step 4/4: Writing output PDF...")
            success = self._write_pdf(output_path, preserve_layout)

            if success:
                logger.info("="*70)
                logger.info("✅ Processing completed successfully!")
                logger.info(f"   Output saved to: {output_path}")
                logger.info(f"   Records processed: {len(self.varied_report.records)}")
                logger.info(f"   Total hours: {self.varied_report.metadata.total_hours:.2f}")
                logger.info("="*70)
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Processing failed: {e}", exc_info=True)
            return False

    def _read_pdf(self, input_path: str) -> Optional[object]:
        """Read PDF with error handling"""
        try:
            # Check file existence
            path = Path(input_path)
            if not path.exists():
                logger.error(f"Input file not found: {input_path}")
                return None

            if not path.suffix.lower() == '.pdf':
                logger.error(f"Input file is not a PDF: {input_path}")
                return None

            # Read PDF
            content = read_pdf(str(path), analyze_structure=True)

            logger.info(f"   ✓ PDF read successfully")
            logger.info(f"   ✓ Pages: {content.page_count}")
            logger.info(f"   ✓ Text length: {len(content.text)} characters")
            logger.info(f"   ✓ Structures analyzed: {len(content.structures)}")

            return content

        except Exception as e:
            logger.error(f"Failed to read PDF: {e}")
            return None

    def _parse_report(self) -> Optional[object]:
        """Parse the report with error handling"""
        try:
            if not self.pdf_content or not self.pdf_content.text:
                logger.error("No text content to parse")
                return None

            # Parse
            report = parse_attendance_report(self.pdf_content.text)

            if not report.records:
                logger.warning("No attendance records found in document")
                return None

            logger.info(f"   ✓ Template identified: {report.template_type.value}")
            logger.info(f"   ✓ Records found: {len(report.records)}")

            if report.metadata.total_hours:
                logger.info(f"   ✓ Total hours: {report.metadata.total_hours:.2f}")

            return report

        except Exception as e:
            logger.error(f"Failed to parse report: {e}")
            return None

    def _create_variation(self, variation_level: str) -> Optional[object]:
        """Create variation with error handling"""
        try:
            if not self.parsed_report:
                logger.error("No parsed report to vary")
                return None

            # Create variation
            varied = create_variation(self.parsed_report, variation_level)

            logger.info(f"   ✓ Variation created successfully")
            logger.info(f"   ✓ Modified records: {len(varied.records)}")

            # Compare hours
            original_hours = self.parsed_report.metadata.total_hours or 0
            varied_hours = varied.metadata.total_hours or 0
            diff = abs(varied_hours - original_hours)

            logger.info(f"   ✓ Hours difference: {diff:.2f} ({original_hours:.2f} → {varied_hours:.2f})")

            return varied

        except Exception as e:
            logger.error(f"Failed to create variation: {e}")
            return None

    def _write_pdf(self, output_path: str, preserve_layout: bool) -> bool:
        """Write PDF with error handling"""
        try:
            if not self.varied_report:
                logger.error("No varied report to write")
                return False

            # Create output folder
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Get structure if exists
            structure = None
            if self.pdf_content and self.pdf_content.structures:
                structure = self.pdf_content.structures[0] if self.pdf_content.structures else None

            # Write PDF
            write_pdf(
                str(output_path_obj),
                self.varied_report,
                structure=structure,
                preserve_layout=preserve_layout
            )

            logger.info(f"   ✓ PDF written to: {output_path}")

            # Check file size
            if output_path_obj.exists():
                size_kb = output_path_obj.stat().st_size / 1024
                logger.info(f"   ✓ File size: {size_kb:.1f} KB")

            return True

        except Exception as e:
            logger.error(f"Failed to write PDF: {e}")
            return False


def process_pdf(input_path: str = "input/attendance.pdf",
                output_path: str = "output/attendance_varied.pdf",
                variation_level: str = VariationLevel.MODERATE,
                preserve_layout: bool = True) -> bool:
    """
    Helper function to process a report

    Args:
        input_path: Input path
        output_path: Output path
        variation_level: Variation level (minimal/moderate/significant)
        preserve_layout: Preserve layout

    Returns:
        True if successful
    """
    processor = AttendanceReportProcessor()
    return processor.process(input_path, output_path, variation_level, preserve_layout)


def main():
    """Main entry point"""

    # Defaults
    DEFAULT_INPUT = "input/w.pdf"
    DEFAULT_OUTPUT = "output/new2.pdf"

    # Read arguments (simple)
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = DEFAULT_INPUT

    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = DEFAULT_OUTPUT

    if len(sys.argv) > 3:
        variation_level = sys.argv[3]
        if variation_level not in [VariationLevel.MINIMAL, VariationLevel.MODERATE, VariationLevel.SIGNIFICANT]:
            logger.warning(f"Invalid variation level '{variation_level}', using 'moderate'")
            variation_level = VariationLevel.MODERATE
    else:
        variation_level = VariationLevel.MODERATE

    # Process
    success = process_pdf(
        input_path=input_path,
        output_path=output_path,
        variation_level=variation_level,
        preserve_layout=True
    )

    # Exit with code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
