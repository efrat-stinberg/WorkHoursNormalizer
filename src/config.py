# """
# config.py - Configuration File
# Central configuration file for the system
# """
#
# from pathlib import Path
#
# # ========== PATHS ==========
#
# # Default directories
# BASE_DIR = Path(__file__).parent.parent
# INPUT_DIR = BASE_DIR / "input"
# OUTPUT_DIR = BASE_DIR / "output"
# FONTS_DIR = BASE_DIR / "fonts"
#
# # Create directories if they don't exist
# INPUT_DIR.mkdir(exist_ok=True)
# OUTPUT_DIR.mkdir(exist_ok=True)
#
# # ========== PDF SETTINGS ==========
#
# # Supported page sizes
# PAGE_SIZES = {
#     "A4": (595, 842),
#     "Letter": (612, 792),
#     "Legal": (612, 1008)
# }
#
# # Default margins (in points)
# DEFAULT_MARGINS = {
#     "top": 36,
#     "bottom": 36,
#     "left": 36,
#     "right": 36
# }
#
# # ========== PARSER SETTINGS ==========
#
# # Supported date formats
# DATE_FORMATS = [
#     "%d/%m/%Y",
#     "%d/%m/%y",
#     "%d.%m.%Y",
#     "%d-%m-%Y",
#     "%Y-%m-%d"
# ]
#
# # Time format
# TIME_FORMAT = "%H:%M"
#
# # Regex timeouts (in seconds)
# REGEX_TIMEOUT = 5
#
# # ========== VARIATION SETTINGS ==========
#
# # Time variation ranges in minutes
# VARIATION_SETTINGS = {
#     "minimal": {
#         "start_minutes": 5,
#         "end_minutes": 5,
#         "break_minutes": 2,
#         "description": "Minimal changes (±5 minutes)"
#     },
#     "moderate": {
#         "start_minutes": 15,
#         "end_minutes": 15,
#         "break_minutes": 5,
#         "description": "Moderate changes (±15 minutes)"
#     },
#     "significant": {
#         "start_minutes": 30,
#         "end_minutes": 30,
#         "break_minutes": 10,
#         "description": "Significant changes (±30 minutes)"
#     }
# }
#
# # Time boundaries
# TIME_BOUNDS = {
#     "earliest_start": "06:00",
#     "latest_start": "10:00",
#     "earliest_end": "14:00",
#     "latest_end": "23:00"
# }
#
# # Break rules
# BREAK_RULES = {
#     "min_hours_for_break": 6,   # Minimum hours required for a break
#     "short_break_minutes": 30,  # Short break duration
#     "long_break_minutes": 45,   # Long break duration
#     "long_break_threshold": 9   # Threshold for long break
# }
#
# # ========== FONT SETTINGS ==========
#
# # Font search paths
# FONT_SEARCH_PATHS = [
#     # Linux
#     "/usr/share/fonts/truetype/liberation/",
#     "/usr/share/fonts/truetype/dejavu/",
#     "/usr/share/fonts/truetype/noto/",
#     # macOS
#     "/System/Library/Fonts/",
#     "/Library/Fonts/",
#     # Windows
#     "C:/Windows/Fonts/",
#     # Local folder
#     str(FONTS_DIR)
# ]
#
# # Font mappings
# FONT_MAPPINGS = {
#     "Arial": ["Arial.ttf", "LiberationSans-Regular.ttf", "DejaVuSans.ttf"],
#     "Arial-Bold": ["Arial-Bold.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
#     "Times-Roman": ["Times-Roman.ttf", "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"],
#     "Courier": ["Courier.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"]
# }
#
# # Default font
# DEFAULT_FONT = "Arial"
# DEFAULT_FONT_SIZE = 10
#
# # ========== LOGGING SETTINGS ==========
#
# # Logging level
# LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
#
# # Log format
# LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
# LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
#
# # Save logs to file
# SAVE_LOGS = False
# LOG_FILE = OUTPUT_DIR / "processing.log"
#
# # ========== TEMPLATE SETTINGS ==========
#
# # Keywords for template detection
# TEMPLATE_KEYWORDS = {
#     "detailed": [
#         "נ.ב", "נ״ב", "בע\"מ", "בע״מ",
#         "125%", "150%", "שבת",
#         "מיקום", "הפסקה"
#     ],
#     "simple": [
#         "כניסה", "יציאה",
#         "סה\"כ", "סה״כ",
#         "שעות עבודה",
#         "התחלה", "סיום"
#     ]
# }
#
# # Template detection threshold (minimum number of keywords)
# TEMPLATE_DETECTION_THRESHOLD = 2
#
# # ========== VALIDATION SETTINGS ==========
#
# # Reasonable working hours ranges
# REASONABLE_HOURS = {
#     "min_daily": 0,
#     "max_daily": 16,
#     "min_monthly": 0,
#     "max_monthly": 400
# }
#
# # Weekend days (0=Sunday, 6=Saturday)
# WEEKEND_DAYS = (4, 5, 6)  # Friday, Saturday, Sunday
#
# # Default hourly rates
# DEFAULT_HOURLY_RATE = 30.65
# DEFAULT_REQUIRED_HOURS = 84.0
#
# # ========== PERFORMANCE SETTINGS ==========
#
# # Max number of pages to analyze structure
# MAX_PAGES_FOR_STRUCTURE = 3
#
# # PDF read timeout (seconds)
# PDF_READ_TIMEOUT = 30
#
# # Text buffer size (characters)
# TEXT_BUFFER_SIZE = 1000000  # 1MB
#
# # ========== DEVELOPMENT SETTINGS ==========
#
# # Debug mode
# DEBUG_MODE = False
#
# # Save intermediate files
# SAVE_INTERMEDIATE_FILES = False
# INTERMEDIATE_DIR = OUTPUT_DIR / "intermediate"
#
# if SAVE_INTERMEDIATE_FILES:
#     INTERMEDIATE_DIR.mkdir(exist_ok=True)
#
# # ========== CONFIG EXPORT ==========
#
# def get_config() -> dict:
#     """Return all configuration values as a dictionary"""
#     return {
#         "paths": {
#             "base_dir": str(BASE_DIR),
#             "input_dir": str(INPUT_DIR),
#             "output_dir": str(OUTPUT_DIR),
#             "fonts_dir": str(FONTS_DIR)
#         },
#         "pdf": {
#             "page_sizes": PAGE_SIZES,
#             "margins": DEFAULT_MARGINS
#         },
#         "parsing": {
#             "date_formats": DATE_FORMATS,
#             "time_format": TIME_FORMAT
#         },
#         "variations": VARIATION_SETTINGS,
#         "fonts": {
#             "default": DEFAULT_FONT,
#             "size": DEFAULT_FONT_SIZE
#         },
#         "logging": {
#             "level": LOG_LEVEL,
#             "save": SAVE_LOGS
#         }
#     }
#
#
# def print_config():
#     """Print current configuration to console"""
#     config = get_config()
#
#     print("=" * 60)
#     print("⚙️  System Configuration")
#     print("=" * 60)
#
#     for section, values in config.items():
#         print(f"\n📁 {section.upper()}:")
#         for key, value in values.items():
#             print(f"   {key}: {value}")
#
#     print("\n" + "=" * 60)
#
#
# if __name__ == "__main__":
#     print_config()
