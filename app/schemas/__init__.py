"""
Pydantic schemas for API serialization and validation.
"""

from .link import LinkBase, LinkCreate, LinkUpdate, LinkResponse, LinkList
from .speed_record import SpeedRecordBase, SpeedRecordCreate, SpeedRecordUpdate, SpeedRecord, SpeedRecordList

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
