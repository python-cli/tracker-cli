from datetime import datetime, timedelta

def parse_flexible_datetime(date_str: str) -> datetime:
    """Parse a date string in various formats, including relative dates and weekdays."""
    try:
        return datetime.fromisoformat(date_str)
    except:
        pass

    date_str = date_str.strip().lower()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Handle relative dates
    if date_str == "now":
        return datetime.now()
    elif date_str == "today":
        return today
    elif date_str == "tomorrow":
        return today + timedelta(days=1)
    elif date_str == "yesterday":
        return today - timedelta(days=1)

    # Handle weekdays (e.g., "monday", "tuesday")
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if date_str in weekdays:
        target_weekday = weekdays.index(date_str)
        current_weekday = today.weekday()
        delta = (current_weekday - target_weekday) % 7
        return today - timedelta(days=delta)

    # Handle MM-DD, MM.DD, MM/DD (assumes current year)
    separators = ['-', '.', '/']
    for sep in separators:
        if sep in date_str:
            parts = date_str.split(sep)
            if len(parts) == 2 and all(part.isdigit() for part in parts):
                month, day = map(int, parts)
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return datetime(today.year, month, day)

    return None
