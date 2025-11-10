"""
config.py - Configuration File
Central configuration file for the system
"""

from pathlib import Path

# ========== PATHS ==========

BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
FONTS_DIR = BASE_DIR / "fonts"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ========== PDF SETTINGS ==========

PAGE_SIZES = {
    "A4": (595, 842),
    "Letter": (612, 792),
    "Legal": (612, 1008)
}

DEFAULT_MARGINS = {
    "top": 36,
    "bottom": 36,
    "left": 36,
    "right": 36
}

# ========== PARSER SETTINGS ==========

DATE_FORMATS = [
    "%d/%m/%Y",
    "%d/%m/%y",
    "%d.%m.%Y",
    "%d-%m-%Y",
    "%Y-%m-%d"
]

TIME_FORMAT = "%H:%M"
REGEX_TIMEOUT = 5

# ========== VARIATION SETTINGS ==========

TIME_VARIATIONS = {
    "minimal": {"start_minutes": 5, "end_minutes": 5, "break_minutes": 2},
    "moderate": {"start_minutes": 15, "end_minutes": 15, "break_minutes": 5},
    "significant": {"start_minutes": 30, "end_minutes": 30, "break_minutes": 10},
}

TIME_BOUNDS = {
    "earliest_start": "06:00",
    "latest_start": "10:00",
    "earliest_end": "14:00",
    "latest_end": "23:00"
}

BREAK_RULES = {
    "min_hours_for_break": 6,
    "short_break_minutes": 30,
    "long_break_minutes": 45,
    "long_break_threshold": 9
}

# ========== FONT SETTINGS ==========

FONT_SEARCH_PATHS = [
    "/usr/share/fonts/truetype/liberation/",
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/truetype/noto/",
    "/System/Library/Fonts/",
    "/Library/Fonts/",
    "C:/Windows/Fonts/",
    str(FONTS_DIR)
]

FONT_MAPPINGS = {
    "Arial": ["Arial.ttf", "LiberationSans-Regular.ttf", "DejaVuSans.ttf"],
    "Arial-Bold": ["Arial-Bold.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
    "Times-Roman": ["Times-Roman.ttf", "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"],
    "Courier": ["Courier.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"]
}

DEFAULT_FONT = "Arial"
DEFAULT_FONT_SIZE = 10

# ========== TEMPLATE SETTINGS ==========

TEMPLATE_KEYWORDS = {
    "detailed": [r'שבת', r'150%', r'125%', r'100%', r'הפסקה'],
    "simple": [r'סה"כ', r'התחלה', r'סיום', r'כניסה', r'יציאה']
}

TEMPLATE_DETECTION_THRESHOLD = 2

# ========== VALIDATION SETTINGS ==========

REASONABLE_HOURS = {
    "min_daily": 0,
    "max_daily": 16,
    "min_monthly": 0,
    "max_monthly": 400
}

WEEKEND_DAYS = (4, 5, 6)
DEFAULT_HOURLY_RATE = 30.65
DEFAULT_REQUIRED_HOURS = 84.0

# ========== LOGGING SETTINGS ==========

LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
SAVE_LOGS = False
LOG_FILE = OUTPUT_DIR / "processing.log"

# ========== PERFORMANCE SETTINGS ==========

MAX_PAGES_FOR_STRUCTURE = 3
PDF_READ_TIMEOUT = 30
TEXT_BUFFER_SIZE = 1000000

# ========== DEVELOPMENT SETTINGS ==========

DEBUG_MODE = False
SAVE_INTERMEDIATE_FILES = False
INTERMEDIATE_DIR = OUTPUT_DIR / "intermediate"

if SAVE_INTERMEDIATE_FILES:
    INTERMEDIATE_DIR.mkdir(exist_ok=True)

# ========== PATTERNS ==========

class Patterns:
    """Central regex patterns used by the parser"""

    # Core field patterns
    DATE = r'(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})'
    TIME = r'(\d{1,2}:\d{2})'
    DECIMAL = r'([\d]+\.[\d]{1,2})'

    # Language-specific day names
    HEBREW_DAY = r'([א-ת]{2,6}י?\'?)'
    ENGLISH_DAY = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)'

    # Keywords from template configuration
    DETAILED_KEYWORDS = TEMPLATE_KEYWORDS["detailed"]
    SIMPLE_KEYWORDS = TEMPLATE_KEYWORDS["simple"]


if __name__ == "__main__":
    print("✅ Configuration module loaded successfully.")
