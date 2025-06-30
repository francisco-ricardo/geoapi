"""
Time period utilities for the geospatial API.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple


class TimePeriod(Enum):
    """
    Time period enumeration based on requirements.

    Each period has an ID, name, and time range.
    """

    OVERNIGHT = (1, "Overnight", "00:00", "03:59")
    EARLY_MORNING = (2, "Early Morning", "04:00", "06:59")
    AM_PEAK = (3, "AM Peak", "07:00", "09:59")
    MIDDAY = (4, "Midday", "10:00", "12:59")
    EARLY_AFTERNOON = (5, "Early Afternoon", "13:00", "15:59")
    PM_PEAK = (6, "PM Peak", "16:00", "18:59")
    EVENING = (7, "Evening", "19:00", "23:59")

    def __init__(
        self, period_id: int, period_name: str, start_time: str, end_time: str
    ):
        self.id = period_id
        self.period_name = period_name
        self.start_time = start_time
        self.end_time = end_time

    @property
    def start_hour(self) -> int:
        """Get start hour as integer."""
        return int(self.start_time.split(":")[0])

    @property
    def end_hour(self) -> int:
        """Get end hour as integer."""
        return int(self.end_time.split(":")[0])

    @classmethod
    def get_by_id(cls, period_id: int) -> Optional["TimePeriod"]:
        """Get period by ID."""
        for period in cls:
            if period.id == period_id:
                return period
        return None

    @classmethod
    def get_by_name(cls, name: str) -> Optional["TimePeriod"]:
        """Get period by name."""
        for period in cls:
            if period.period_name == name:
                return period
        return None

    @classmethod
    def get_all_periods(cls) -> List["TimePeriod"]:
        """Get all periods."""
        return list(cls)

    @classmethod
    def get_period_mapping(cls) -> Dict[int, str]:
        """Get mapping of period ID to name."""
        return {period.id: period.period_name for period in cls}

    @classmethod
    def get_name_mapping(cls) -> Dict[str, int]:
        """Get mapping of period name to ID."""
        return {period.period_name: period.id for period in cls}


class DayOfWeek(Enum):
    """
    Day of week enumeration.
    """

    MONDAY = (1, "Monday")
    TUESDAY = (2, "Tuesday")
    WEDNESDAY = (3, "Wednesday")
    THURSDAY = (4, "Thursday")
    FRIDAY = (5, "Friday")
    SATURDAY = (6, "Saturday")
    SUNDAY = (7, "Sunday")

    def __init__(self, day_id: int, day_name: str):
        self.id = day_id
        self.day_name = day_name

    @classmethod
    def get_by_id(cls, day_id: int) -> Optional["DayOfWeek"]:
        """Get day by ID."""
        for day in cls:
            if day.id == day_id:
                return day
        return None

    @classmethod
    def get_by_name(cls, name: str) -> Optional["DayOfWeek"]:
        """Get day by name."""
        for day in cls:
            if day.day_name.lower() == name.lower():
                return day
        return None

    @classmethod
    def get_all_days(cls) -> List["DayOfWeek"]:
        """Get all days."""
        return list(cls)


def validate_day_period_params(day: str, period: str) -> Tuple[DayOfWeek, TimePeriod]:
    """
    Validate and convert day and period parameters.

    Args:
        day: Day of week name (e.g., "Monday")
        period: Time period name (e.g., "AM Peak")

    Returns:
        Tuple of (DayOfWeek, TimePeriod) objects

    Raises:
        ValueError: If day or period is invalid
    """
    day_obj = DayOfWeek.get_by_name(day)
    if not day_obj:
        valid_days = [d.day_name for d in DayOfWeek.get_all_days()]
        raise ValueError(f"Invalid day '{day}'. Valid options: {valid_days}")

    period_obj = TimePeriod.get_by_name(period)
    if not period_obj:
        valid_periods = [p.period_name for p in TimePeriod.get_all_periods()]
        raise ValueError(f"Invalid period '{period}'. Valid options: {valid_periods}")

    return day_obj, period_obj
