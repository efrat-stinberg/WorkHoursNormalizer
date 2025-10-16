import re
from datetime import datetime, timedelta
import random


def parse_time(t):
    """Convert HH:MM string to datetime.time"""
    try:
        return datetime.strptime(t, "%H:%M")
    except Exception:
        return None


def time_to_str(t):
    """Convert datetime/time back to HH:MM"""
    return t.strftime("%H:%M") if t else ""


def random_time_variation(t, minutes_range=(-10, 10)):
    """Return time shifted by a few random minutes"""
    if not t:
        return ""
    delta = timedelta(minutes=random.randint(*minutes_range))
    new_time = t + delta
    return time_to_str(new_time)


def clean_text(text):
    """Basic text normalization"""
    text = text.replace("\r", "").replace("\xa0", " ")
    text = re.sub(r"[ ]+", " ", text)
    return text.strip()
