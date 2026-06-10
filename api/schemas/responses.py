from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── 统一响应模型 ──

class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Any = None


class PaginatedData(BaseModel):
    items: list[Any]
    totalCount: int
    page: int
    pageSize: int


def success(data: Any = None) -> ApiResponse:
    return ApiResponse(code=0, message="success", data=data)


def paginated(items: list[Any], total: int, page: int, page_size: int) -> ApiResponse:
    return ApiResponse(code=0, message="success", data=PaginatedData(
        items=items, totalCount=total, page=page, pageSize=page_size,
    ))


def error(code: int, message: str) -> ApiResponse:
    return ApiResponse(code=code, message=message, data=None)


# ── 业务模型 ──

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
    website: str
    res_type: str = "all"
    depth: int = 1
    link_follow: bool = False
    save_method: str = "download"
    proxy_id: int = Field(default=-1, description="代理配置ID，-1表示不走代理")


class CrawlResponse(BaseModel):
    task_id: int


class CrawlResult(BaseModel):
    url: str
    types_detected: list[str]
    items_count: int


# ── ProxyConfig ──

class ProxyConfigOut(BaseModel):
    id: int
    name: str
    proxy_http: Optional[str] = None
    proxy_https: Optional[str] = None
    username: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class ProxyConfigCreate(BaseModel):
    name: str
    proxy_http: Optional[str] = None
    proxy_https: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class ProxyConfigUpdate(BaseModel):
    name: Optional[str] = None
    proxy_http: Optional[str] = None
    proxy_https: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
