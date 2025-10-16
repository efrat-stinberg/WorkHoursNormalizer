import random
from datetime import datetime, timedelta, time
from src.utils import parse_time, random_time_variation, time_to_str, duration_hours, is_weekend
import logging

logger = logging.getLogger(__name__)

def generate_variation(data, level="moderate"):
    """
    Generate realistic variations of attendance data while maintaining logical consistency.
    
    Args:
        data: List of attendance records
        level: Variation level ("minimal", "moderate", "significant")
    
    Returns:
        List of modified attendance records
    """
    if not data:
        return data
    
    variation_ranges = {
        "minimal": {"time": 5, "break": 2},
        "moderate": {"time": 15, "break": 5},
        "significant": {"time": 30, "break": 10}
    }
    
    range_config = variation_ranges.get(level, variation_ranges["moderate"])
    
    new_data = []
    for i, row in enumerate(data):
        new_row = row.copy()
        
        # Generate realistic times
        start_time, end_time = _generate_realistic_times(row, range_config)
        if start_time and end_time:
            new_row["כניסה"] = time_to_str(start_time)
            new_row["יציאה"] = time_to_str(end_time)
            
            # Calculate realistic break time
            break_minutes = _calculate_break_time(start_time, end_time, range_config)
            if "הפסקה" in new_row:
                new_row["הפסקה"] = f"{break_minutes:02d}:00"
            
            # Calculate total hours
            total_hours = duration_hours(start_time, end_time, break_minutes)
            new_row["סה\"כ"] = f"{total_hours:.2f}"
            
            # Generate overtime percentages if present
            _generate_overtime_percentages(new_row, total_hours)
        else:
            # Keep original values if parsing failed
            new_row["כניסה"] = row.get("כניסה", "")
            new_row["יציאה"] = row.get("יציאה", "")
            new_row["סה\"כ"] = row.get("סה\"כ", "")
        
        # Generate realistic date if needed
        if "תאריך" in new_row and not new_row["תאריך"]:
            new_row["תאריך"] = _generate_realistic_date(i)
        
        # Generate day of week if needed
        if "יום" in new_row and not new_row["יום"]:
            new_row["יום"] = _get_day_of_week(new_row.get("תאריך", ""))
        
        new_data.append(new_row)
    
    return new_data

def _generate_realistic_times(row, range_config):
    """Generate realistic start and end times based on original data."""
    original_start = parse_time(row.get("כניסה"))
    original_end = parse_time(row.get("יציאה"))
    
    if not original_start or not original_end:
        return None, None
    
    # Generate realistic start time (typically 7:00-9:00)
    base_start_hour = random.randint(7, 9)
    base_start_minute = random.randint(0, 59)
    start_time = datetime.combine(original_start.date(), time(base_start_hour, base_start_minute))
    
    # Add variation
    time_variation = random.randint(-range_config["time"], range_config["time"])
    start_time += timedelta(minutes=time_variation)
    
    # Generate realistic end time (typically 15:00-18:00)
    base_end_hour = random.randint(15, 18)
    base_end_minute = random.randint(0, 59)
    end_time = datetime.combine(original_end.date(), time(base_end_hour, base_end_minute))
    
    # Add variation
    time_variation = random.randint(-range_config["time"], range_config["time"])
    end_time += timedelta(minutes=time_variation)
    
    # Ensure end time is after start time
    if end_time <= start_time:
        end_time = start_time + timedelta(hours=8)
    
    return start_time, end_time

def _calculate_break_time(start_time, end_time, range_config):
    """Calculate realistic break time based on work duration."""
    work_duration = (end_time - start_time).total_seconds() / 3600.0
    
    if work_duration <= 4:
        return 0  # No break for short shifts
    elif work_duration <= 6:
        return 15  # 15 minutes for medium shifts
    elif work_duration <= 8:
        return 30  # 30 minutes for full shifts
    else:
        return 45  # 45 minutes for long shifts

def _generate_overtime_percentages(row, total_hours):
    """Generate realistic overtime percentages."""
    if total_hours <= 8:
        # Regular hours
        if "100%" in row:
            row["100%"] = f"{total_hours:.2f}"
        if "125%" in row:
            row["125%"] = "0.00"
        if "150%" in row:
            row["150%"] = "0.00"
    elif total_hours <= 10:
        # Some overtime
        regular_hours = 8.0
        overtime_hours = total_hours - regular_hours
        if "100%" in row:
            row["100%"] = f"{regular_hours:.2f}"
        if "125%" in row:
            row["125%"] = f"{overtime_hours:.2f}"
        if "150%" in row:
            row["150%"] = "0.00"
    else:
        # Significant overtime
        regular_hours = 8.0
        overtime_125 = min(2.0, total_hours - regular_hours)
        overtime_150 = max(0, total_hours - regular_hours - 2.0)
        
        if "100%" in row:
            row["100%"] = f"{regular_hours:.2f}"
        if "125%" in row:
            row["125%"] = f"{overtime_125:.2f}"
        if "150%" in row:
            row["150%"] = f"{overtime_150:.2f}"

def _generate_realistic_date(index):
    """Generate a realistic date for the given index."""
    base_date = datetime.now() - timedelta(days=30)
    return (base_date + timedelta(days=index)).strftime("%d/%m/%Y")

def _get_day_of_week(date_str):
    """Get Hebrew day of week for given date."""
    if not date_str:
        return ""
    
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y")
        days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]
        return days[dt.weekday()]
    except:
        return ""

# Backward compatibility
def create_variation(data):
    """Backward compatibility wrapper."""
    return generate_variation(data, level="moderate")
