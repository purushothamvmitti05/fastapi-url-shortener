from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class URLBase(BaseModel):
    target_url: str


class URLCreate(URLBase):
    pass


class ClickInfo(BaseModel):
    timestamp: datetime
    referrer: Optional[str] = None

    class Config:
        from_attributes = True


class URLInfo(URLBase):
    short_code: str
    created_at: datetime
    total_clicks: int = 0

    class Config:
        from_attributes = True


class URLStats(URLInfo):
    clicks: List[ClickInfo] = []