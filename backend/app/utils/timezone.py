from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo

def get_user_today(user_timezone: str) -> date:
    """
    Determine the current date in the user's specific local timezone.
    
    This is critical for ensuring that daily logs (steps, water, etc.) are 
    attributed to the correct day relative to the user, not the server.
    
    Args:
        user_timezone: The IANA timezone string (e.g., 'America/New_York').
        
    Returns:
        A datetime.date object representing the user's local 'today'.
        Defaults to UTC date if the provided timezone is invalid.
    """
    try:
        # Create a ZoneInfo object from the user's preferred timezone string
        tz = ZoneInfo(user_timezone)
    except Exception:
        # Fallback to UTC if the timezone string is unrecognized
        tz = timezone.utc

    # 1. Get the current exact time in UTC (Universal Time)
    # 2. Convert (astimezone) that exact moment to the user's local clock
    user_time = datetime.now(timezone.utc).astimezone(tz)

    # Return only the date part (YYYY-MM-DD)
    return user_time.date()