"""
Pydantic schemas for the Authentication Log Upload feature.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

REQUIRED_CSV_COLUMNS: list[str] = [
    "timestamp",
    "username",
    "ip_address",
    "country",
    "device",
    "login_status",
    "is_privileged",
]


class LogEventCreate(BaseModel):
    timestamp: datetime
    username: str
    ip_address: str
    country: str
    device: str
    login_status: str
    is_privileged: bool


class LogEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    username: str
    ip_address: str
    country: str
    device: str
    login_status: str
    is_privileged: bool
    created_at: datetime


class LogUploadResponse(BaseModel):
    message: str = Field(..., examples=["Log file uploaded and processed successfully"])
    rows_imported: int = Field(..., examples=[128])
