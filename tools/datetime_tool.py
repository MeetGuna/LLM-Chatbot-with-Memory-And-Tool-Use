from langchain.tools import tool
from datetime import datetime
import pytz


@tool
def datetime_tool(timezone: str = "Asia/Kolkata") -> str:
    """
    Returns the current date, time, and day of the week.
    Use this whenever the user asks about the current date, time, or day.
    Optionally accepts a timezone string (e.g. 'Asia/Kolkata', 'UTC', 'US/Eastern').
    Default timezone is Asia/Kolkata (IST).
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return (
            f"Current date & time ({timezone}):\n"
            f"  Date: {now.strftime('%A, %d %B %Y')}\n"
            f"  Time: {now.strftime('%I:%M %p')}\n"
            f"  Day: {now.strftime('%A')}"
        )
    except Exception:
        now = datetime.now()
        return (
            f"Current date & time (local):\n"
            f"  Date: {now.strftime('%A, %d %B %Y')}\n"
            f"  Time: {now.strftime('%I:%M %p')}\n"
            f"  Day: {now.strftime('%A')}"
        )
