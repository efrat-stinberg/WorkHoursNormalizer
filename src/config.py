"""
config.py - Configuration File
קובץ הגדרות מרכזי למערכת
"""

from pathlib import Path

# ========== נתיבים ==========

# תיקיות ברירת מחדל
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
FONTS_DIR = BASE_DIR / "fonts"

# יצירת תיקיות אם לא קיימות
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ========== הגדרות PDF ==========

# גודלי עמוד נתמכים
PAGE_SIZES = {
    "A4": (595, 842),
    "Letter": (612, 792),
    "Legal": (612, 1008)
}

# margins ברירת מחדל (בנקודות)
DEFAULT_MARGINS = {
    "top": 36,
    "bottom": 36,
    "left": 36,
    "right": 36
}

# ========== הגדרות פרסור ==========

# פורמטי תאריך נתמכים
DATE_FORMATS = [
    "%d/%m/%Y",
    "%d/%m/%y",
    "%d.%m.%Y",
    "%d-%m-%Y",
    "%Y-%m-%d"
]

# פורמט זמן
TIME_FORMAT = "%H:%M"

# Regex timeouts (בשניות)
REGEX_TIMEOUT = 5

# ========== הגדרות וריאציות ==========

# טווחי שינוי בדקות
VARIATION_SETTINGS = {
    "minimal": {
        "start_minutes": 5,
        "end_minutes": 5,
        "break_minutes": 2,
        "description": "שינויים מינימליים (±5 דקות)"
    },
    "moderate": {
        "start_minutes": 15,
        "end_minutes": 15,
        "break_minutes": 5,
        "description": "שינויים בינוניים (±15 דקות)"
    },
    "significant": {
        "start_minutes": 30,
        "end_minutes": 30,
        "break_minutes": 10,
        "description": "שינויים משמעותיים (±30 דקות)"
    }
}

# גבולות זמן
TIME_BOUNDS = {
    "earliest_start": "06:00",
    "latest_start": "10:00",
    "earliest_end": "14:00",
    "latest_end": "23:00"
}

# כללי הפסקות
BREAK_RULES = {
    "min_hours_for_break": 6,  # שעות מינימום להפסקה
    "short_break_minutes": 30,  # הפסקה קצרה
    "long_break_minutes": 45,  # הפסקה ארוכה
    "long_break_threshold": 9  # סף להפסקה ארוכה
}

# ========== הגדרות פונטים ==========

# נתיבי חיפוש פונטים
FONT_SEARCH_PATHS = [
    # Linux
    "/usr/share/fonts/truetype/liberation/",
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/truetype/noto/",
    # macOS
    "/System/Library/Fonts/",
    "/Library/Fonts/",
    # Windows
    "C:/Windows/Fonts/",
    # תיקייה מקומית
    str(FONTS_DIR)
]

# מיפוי פונטים
FONT_MAPPINGS = {
    "Arial": ["Arial.ttf", "LiberationSans-Regular.ttf", "DejaVuSans.ttf"],
    "Arial-Bold": ["Arial-Bold.ttf", "LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
    "Times-Roman": ["Times-Roman.ttf", "LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"],
    "Courier": ["Courier.ttf", "LiberationMono-Regular.ttf", "DejaVuSansMono.ttf"]
}

# פונט ברירת מחדל
DEFAULT_FONT = "Arial"
DEFAULT_FONT_SIZE = 10

# ========== הגדרות לוגים ==========

# רמת logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# פורמט לוג
LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# שמירת לוגים לקובץ
SAVE_LOGS = False
LOG_FILE = OUTPUT_DIR / "processing.log"

# ========== הגדרות תבניות ==========

# מילות מפתח לזיהוי תבניות
TEMPLATE_KEYWORDS = {
    "detailed": [
        "נ.ב", "נ״ב", "בע\"מ", "בע״מ",
        "125%", "150%", "שבת",
        "מיקום", "הפסקה"
    ],
    "simple": [
        "כניסה", "יציאה",
        "סה\"כ", "סה״כ",
        "שעות עבודה",
        "התחלה", "סיום"
    ]
}

# סף לזיהוי תבנית (מספר מילות מפתח מינימלי)
TEMPLATE_DETECTION_THRESHOLD = 2

# ========== הגדרות ולידציה ==========

# טווחי שעות סבירים
REASONABLE_HOURS = {
    "min_daily": 0,
    "max_daily": 16,
    "min_monthly": 0,
    "max_monthly": 400
}

# ימי סוף שבוע (0=ראשון, 6=שבת)
WEEKEND_DAYS = (4, 5, 6)  # שישי, שבת, ראשון

# תעריפים ברירת מחדל
DEFAULT_HOURLY_RATE = 30.65
DEFAULT_REQUIRED_HOURS = 84.0

# ========== הגדרות ביצועים ==========

# מספר עמודים מקסימלי לניתוח מבנה
MAX_PAGES_FOR_STRUCTURE = 3

# timeout לקריאת PDF (בשניות)
PDF_READ_TIMEOUT = 30

# גודל buffer לטקסט (תווים)
TEXT_BUFFER_SIZE = 1000000  # 1MB

# ========== הגדרות פיתוח ==========

# מצב debug
DEBUG_MODE = False

# שמירת קבצי ביניים
SAVE_INTERMEDIATE_FILES = False
INTERMEDIATE_DIR = OUTPUT_DIR / "intermediate"

if SAVE_INTERMEDIATE_FILES:
    INTERMEDIATE_DIR.mkdir(exist_ok=True)


# ========== ייצוא הגדרות ==========

def get_config() -> dict:
    """החזרת כל ההגדרות כ-dictionary"""
    return {
        "paths": {
            "base_dir": str(BASE_DIR),
            "input_dir": str(INPUT_DIR),
            "output_dir": str(OUTPUT_DIR),
            "fonts_dir": str(FONTS_DIR)
        },
        "pdf": {
            "page_sizes": PAGE_SIZES,
            "margins": DEFAULT_MARGINS
        },
        "parsing": {
            "date_formats": DATE_FORMATS,
            "time_format": TIME_FORMAT
        },
        "variations": VARIATION_SETTINGS,
        "fonts": {
            "default": DEFAULT_FONT,
            "size": DEFAULT_FONT_SIZE
        },
        "logging": {
            "level": LOG_LEVEL,
            "save": SAVE_LOGS
        }
    }


def print_config():
    """הדפסת ההגדרות הנוכחיות"""
    config = get_config()

    print("=" * 60)
    print("⚙️  הגדרות מערכת")
    print("=" * 60)

    for section, values in config.items():
        print(f"\n📁 {section.upper()}:")
        for key, value in values.items():
            print(f"   {key}: {value}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_config()