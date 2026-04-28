from datetime import datetime, timezone
import pytz

def get_user_today(user_timezone: str):
    try:
        tz = pytz.timezone(user_timezone)
    except Exception:
        tz = pytz.UTC

    utc_now = datetime.now(timezone.utc)   

    user_time = utc_now.astimezone(tz)

    return user_time.date()