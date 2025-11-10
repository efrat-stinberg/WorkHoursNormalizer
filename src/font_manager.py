"""
Font Manager for PDF Generation
Handles font detection, registration, and RTL text processing for Hebrew/English content.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
import arabic_reshaper
from bidi.algorithm import get_display

logger = logging.getLogger(__name__)

class FontManager:
    """Manages fonts for PDF generation with Hebrew and English support."""

    def __init__(self):
        self.registered_fonts = {}
        self.font_mappings = {}
        self._register_available_fonts()

    def _register_available_fonts(self):
        """Register all available fonts for Hebrew and English text."""
        font_paths = self._find_font_files()

        for font_name, font_path in font_paths.items():
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                self.registered_fonts[font_name] = font_path
                logger.info(f"Registered font: {font_name}")
            except Exception as e:
                logger.warning(f"Failed to register font {font_name}: {e}")

        # Set up font mappings
        self._setup_font_mappings()

    def _find_font_files(self) -> Dict[str, str]:
        """Find available font files on the system."""
        font_paths = {}

        # Common font locations
        font_dirs = [
            '/usr/share/fonts/truetype/liberation/',
            '/usr/share/fonts/truetype/dejavu/',
            '/usr/share/fonts/truetype/noto/',
            '/System/Library/Fonts/',  # macOS
            'C:/Windows/Fonts/',  # Windows
            './fonts/',  # Local fonts directory
        ]

        # Font name mappings
        font_mappings = {
            'Arial': ['Arial.ttf', 'LiberationSans-Regular.ttf', 'DejaVuSans.ttf'],
            'Arial-Bold': ['Arial-Bold.ttf', 'LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf'],
            'Times-Roman': ['Times-Roman.ttf', 'LiberationSerif-Regular.ttf', 'DejaVuSerif.ttf'],
            'Times-Bold': ['Times-Bold.ttf', 'LiberationSerif-Bold.ttf', 'DejaVuSerif-Bold.ttf'],
            'Courier': ['Courier.ttf', 'LiberationMono-Regular.ttf', 'DejaVuSansMono.ttf'],
        }

        for font_name, font_files in font_mappings.items():
            for font_file in font_files:
                for font_dir in font_dirs:
                    font_path = os.path.join(font_dir, font_file)
                    if os.path.exists(font_path):
                        font_paths[font_name] = font_path
                        break
                if font_name in font_paths:
                    break

        return font_paths

    def _setup_font_mappings(self):
        """Set up font mappings for different text types."""
        # Map font names to their variants
        self.font_mappings = {
            'normal': 'Arial',
            'bold': 'Arial-Bold',
            'italic': 'Arial',  # Fallback to normal if italic not available
            'bold-italic': 'Arial-Bold',
        }

    def process_hebrew_text(self, text: str) -> str:
        """Process Hebrew text for proper RTL display."""
        if not text:
            return text

        # Check if text contains Hebrew characters
        # if not any('\u0590' <= c <= '\u05FF' for c in text):
        if not (self.is_hebrew_text(text)):
            return text

        try:
            # Reshape Arabic/Hebrew text
            reshaped_text = arabic_reshaper.reshape(text)
            # Apply bidirectional algorithm
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            logger.warning(f"Error processing Hebrew text: {e}")
            return text

    def is_hebrew_text(self, text: str) -> bool:
        """Check if text contains Hebrew characters."""
        return any('\u0590' <= c <= '\u05FF' for c in text) if text else False


# Global font manager instance
font_manager = FontManager()