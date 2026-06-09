import os

from fastapi import APIRouter, Query
from pymongo import MongoClient

from api.schemas.responses import MediaOut, PaginatedResponse

router = APIRouter()


def _db():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    return client[os.getenv("MONGO_DATABASE", "web_collector")]


@router.get("")
def list_media(
    media_type: str = Query("", description="过滤类型: image / video / audio"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    db = _db()
    q = {}
    if media_type:
        q["media_type"] = media_type

    total = db.media.count_documents(q)
    docs = (
        db.media.find({})
        .sort("extracted_at", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    items = [MediaOut(**d) for d in docs]
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)
