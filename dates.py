import datetime
import typing


def iter_days(start_day: datetime.datetime, num_days: int) -> typing.Generator[datetime.datetime, typing.Any, None]:
    """Iterate over `[start_day, start_day + 1 day, start_day + 2 days, ..., start_day + num_days days)`"""
    for i in range(num_days):
        yield start_day + datetime.timedelta(days=i)


def get_hour(day: datetime.datetime, hour: int) -> datetime.datetime:
    """Returns the top of the given hour on the given day."""
    return day.replace(hour=hour, minute=0, second=0, microsecond=0)
