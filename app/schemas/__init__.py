"""
Pydantic schemas for API serialization and validation.
"""

from .link import LinkBase, LinkCreate, LinkList, LinkResponse, LinkUpdate
from .speed_record import (
    SpeedRecord,
    SpeedRecordBase,
    SpeedRecordCreate,
    SpeedRecordList,
    SpeedRecordUpdate,
)

__all__ = [
    # Link schemas
    "LinkBase",
    "LinkCreate",
    "LinkUpdate",
    "LinkResponse",
    "LinkList",
    # SpeedRecord schemas
    "SpeedRecordBase",
    "SpeedRecordCreate",
    "SpeedRecordUpdate",
    "SpeedRecord",
    "SpeedRecordList",
]
