from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class WebPageOut(BaseModel):
    url: str
    title: str
    content_type: str
    text_content: Optional[str] = None
    metadata: dict[str, Any] = {}
    extracted_at: Optional[datetime] = None


class MediaOut(BaseModel):
    url: str
    source_page: str
    media_type: str
    filename: str
    mime_type: Optional[str] = None
    metadata: dict[str, Any] = {}
    extracted_at: Optional[datetime] = None


class CrawlRequest(BaseModel):
    url: str
    types: str = "text"
    depth: int = 1


class CrawlResult(BaseModel):
    url: str
    types_detected: list[str]
    items_count: int


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[Any]
