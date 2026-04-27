from __future__ import annotations

from datetime import datetime

import pytz


def get_datetime(timezone: str) -> datetime:
    tz = pytz.timezone(timezone)
    return datetime.now(tz=tz).replace(tzinfo=None)
