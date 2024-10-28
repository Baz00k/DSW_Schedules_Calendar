from datetime import datetime
from pytz import timezone

def get_offset_from_timezone(timezone_str: str) -> int:
    """
    Get the offset from the UTC time for the specified timezone.

    :param timezone: The timezone to get the offset for.
    :return: The offset from the UTC time.
    """
    try:
        return int(datetime.now(timezone(timezone_str)).strftime('%z')) // 100
    except ValueError:
        return 0