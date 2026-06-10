import os
from datetime import datetime
from typing import Any, Optional

from pymongo import MongoClient
from sqlalchemy import and_
from sqlalchemy.orm import Session

from web_collector.db import get_session
from web_collector.db.models import Resource, ScrapTask


def _mongo_db():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    return client[os.getenv("MONGO_DATABASE", "web_collector")]


class ResourceService:
    """资源查询业务逻辑"""

    def list_resources(self, website: str, res_type: str,
                       min_time: Optional[datetime], max_time: Optional[datetime],
                       page: int, page_size: int) -> tuple[list[dict], int]:
        """
        联合查询 t_resources + t_scrap_task，返回资源列表和总数。
        """
        session = next(get_session())
        try:
            q = session.query(
                Resource.id,
                Resource.scrap_task_id,
                Resource.website,
                Resource.res_link,
                Resource.parent_link,
                Resource.res_type,
                Resource.object_id,
                Resource.res_size,
                Resource.create_time,
                Resource.update_time,
                Resource.extension,
                ScrapTask.status.label("task_status"),
                ScrapTask.scrap_time.label("task_scrap_time"),
            ).join(
                ScrapTask, Resource.scrap_task_id == ScrapTask.id
            )

            filters = []
            if website:
                filters.append(Resource.website == website)
            if res_type:
                filters.append(Resource.res_type == res_type)
            if min_time is not None and max_time is not None:
                filters.append(Resource.create_time.between(min_time, max_time))
            if filters:
                q = q.filter(and_(*filters))

            total = q.count()
            rows = (
                q.order_by(Resource.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            items = [row._asdict() for row in rows]
            return items, total
        finally:
            session.close()

    def get_resource(self, resource_id: int) -> Optional[dict[str, Any]]:
        """
        查询单个资源，若 object_id 存在则查询对应的存储后端。
        - text/article → MongoDB
        - pic/doc/audio/video → MinIO 路径
        """
        session = next(get_session())
        try:
            resource = session.get(Resource, resource_id)
            if not resource:
                return None

            result = {
                "id": resource.id,
                "scrap_task_id": resource.scrap_task_id,
                "website": resource.website,
                "res_link": resource.res_link,
                "parent_link": resource.parent_link,
                "res_type": resource.res_type,
                "object_id": resource.object_id,
                "res_size": resource.res_size,
                "create_time": resource.create_time.isoformat() if resource.create_time else None,
                "update_time": resource.update_time.isoformat() if resource.update_time else None,
                "extension": resource.extension,
                "storage_data": None,
            }

            if not resource.object_id:
                return result

            # 根据资源类型查询对应存储后端
            if resource.res_type in ("text/article",):
                result["storage_data"] = self._query_mongodb(resource.object_id)
            elif resource.object_id.startswith("web-collector/"):
                # MinIO 路径格式: bucket/path
                result["storage_data"] = {
                    "storage": "minio",
                    "path": resource.object_id,
                }

            return result
        finally:
            session.close()

    @staticmethod
    def _query_mongodb(object_id: str) -> Optional[dict]:
        """根据 object_id 查询 MongoDB"""
        from bson.objectid import ObjectId
        db = _mongo_db()
        try:
            doc = db.web_pages.find_one({"_id": ObjectId(object_id)}, {"html": 0})
            if doc:
                doc["_id"] = str(doc["_id"])
                return doc
        except Exception:
            pass
        # 也尝试按 url 或其他字段匹配
        doc = db.web_pages.find_one({"url": object_id}, {"html": 0})
        if doc:
            doc["_id"] = str(doc["_id"])
            return doc
        return None


resource_service = ResourceService()
