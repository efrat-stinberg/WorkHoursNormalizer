# מערכת עיבוד דוחות נוכחות - Attendance Report Processor

מערכת לעיבוד אוטומטי של דוחות נוכחות בפורמט PDF, יצירת וריאציות בזמני עבודה, ויצירת דוח חדש.

---

## 🧾 תיאור הפרויקט
המערכת מאפשרת:
- קריאה ופרסור של קבצי PDF עם דוחות נוכחות  
- זיהוי אוטומטי של סוג התבנית (פשוטה / מפורטת)  
- יצירת וריאציות לוגיות בזמני כניסה, יציאה והפסקות  
- יצירת PDF חדש עם הנתונים המשתנים  
- תמיכה מלאה בעברית וב-RTL  

---

## ⚙️ דרישות מערכת
- **Python** 3.8 ומעלה  
- **pip** (מנהל חבילות של Python)  
- מערכת הפעלה: Windows / Linux / macOS  

---
---

## 🧩 התקנה

### 1️⃣ הורדת הפרויקט  
העתק את כל קבצי הפרויקט לתיקייה במחשב שלך.

### 2️⃣ יצירת סביבה וירטואלית (מומלץ)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
````

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ התקנת תלויות

```bash
pip install -r requirements.txt
```

התקנה זו תוריד ותתקין את החבילות הבאות:

* **PyMuPDF** – קריאת PDF
* **PyPDF2** – חילוץ טקסט מ-PDF
* **pdfplumber** – ניתוח מבנה PDF
* **reportlab** – יצירת PDF
* **arabic-reshaper**, **python-bidi** – תמיכה בעברית ו-RTL

---

## 📁 מבנה תיקיות

```
project/
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # נקודת כניסה ראשית
│   ├── pdf_reader.py            # קריאת PDF
│   ├── attendance_parser.py     # פרסור נתונים
│   ├── data_generator.py        # יצירת וריאציות
│   ├── pdf_writer.py            # כתיבת PDF
│   ├── font_manager.py          # ניהול פונטים
│   ├── structure_analyzer.py    # ניתוח מבנה
│   ├── config.py                # הגדרות כלליות
│   └── utils.py                 # פונקציות עזר
│
├── input/                       # קבצי PDF לעיבוד
├── output/                      # קבצי פלט
├── fonts/                       # פונטים (אופציונלי)
│
├── requirements.txt             # רשימת תלויות
└── README.md                    # קובץ זה
```

> ℹ️ התיקיות `input/` ו-`output/` ייווצרו אוטומטית בהרצה הראשונה.

---

## ▶️ הרצת התוכנית

### שימוש בסיסי (ברירת מחדל)

```bash
cd src
python main.py
```

התוכנית תעבד את הקבצים הבאים:

* קובץ קלט: `input/w.pdf`
* קובץ פלט: `output/new.pdf`

```
```
