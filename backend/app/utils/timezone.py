from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def get_user_today(user_timezone: str):
    """
    Get the current date in the user's local timezone.
    Defaults to UTC if the timezone is invalid.
    """
    try:
        tz = ZoneInfo(user_timezone)
    except Exception:
        tz = timezone.utc

    # Get current UTC time and convert to user timezone
    user_time = datetime.now(timezone.utc).astimezone(tz)

    return user_time.date()