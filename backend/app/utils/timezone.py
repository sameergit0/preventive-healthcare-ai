from datetime import datetime
import pytz

def get_user_today(user_timezone: str):
    try:
        tz = pytz.timezone(user_timezone)
    except Exception:
        tz = pytz.UTC 

    return datetime.now(tz).date()