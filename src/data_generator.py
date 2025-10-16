import random
from datetime import datetime, timedelta
from src.utils import parse_time, random_time_variation, time_to_str


def create_variation(data):
    """
    Create logical variations of attendance data.
    - Slightly modifies entry/exit times
    - Keeps logical order and valid totals
    """
    new_data = []
    for row in data:
        new_row = row.copy()
        start = parse_time(row.get("כניסה"))
        end = parse_time(row.get("יציאה"))

        if start and end:
            new_row["כניסה"] = random_time_variation(start)
            new_row["יציאה"] = random_time_variation(end)
            # compute total
            total_hours = (parse_time(new_row["יציאה"]) -
                           parse_time(new_row["כניסה"])).seconds / 3600.0
            new_row["סה\"כ"] = f"{total_hours:.2f}"
        else:
            new_row["סה\"כ"] = row.get("סה\"כ", "")

        new_data.append(new_row)

    return new_data
