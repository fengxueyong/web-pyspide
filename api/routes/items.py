import os

from fastapi import APIRouter, Query
from pymongo import MongoClient

from api.schemas.responses import WebPageOut, paginated, success, error

router = APIRouter()


def _db():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    return client[os.getenv("MONGO_DATABASE", "web_collector")]


@router.get("")
def list_items(
    content_type: str = Query("", description="过滤内容类型: text / news"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    db = _db()
    q = {}
    if content_type:
        q["content_type"] = content_type

    total = db.web_pages.count_documents(q)
    docs = (
        db.web_pages.find(q, {"html": 0})
        .sort("extracted_at", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    items = [WebPageOut(**d) for d in docs]
    return paginated(items=items, total=total, page=page, page_size=page_size)


@router.get("/{url}")
def get_item(url: str):
    db = _db()
    doc = db.web_pages.find_one({"url": url}, {"html": 0})
    if not doc:
        return error(4001, "内容不存在")
    return success(WebPageOut(**doc))
