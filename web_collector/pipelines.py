import datetime
import json
import logging
from urllib.parse import urlparse

import requests
from pymongo import MongoClient, ASCENDING

from web_collector.items import MediaItem, WebPageItem
from web_collector.storage import MinioStorage
from web_collector.db import get_session, crud

logger = logging.getLogger(__name__)


def _emit_progress(event: str, data: dict):
    """向 stdout 输出进度 JSON，供 CrawlService 读取并推送 WebSocket"""
    line = json.dumps({"event": event, "data": data}, ensure_ascii=False)
    print(f"__CRAWL_PROGRESS__:{line}", flush=True)


class MediaPipeline:
    """下载媒体文件 → 上传 MinIO → 将存储路径写入 Item"""

    def __init__(self, settings):
        self.download_enabled = settings.getbool("MEDIA_DOWNLOAD")
        if self.download_enabled:
            self.storage = MinioStorage(
                endpoint=settings["MINIO_ENDPOINT"],
                access_key=settings["MINIO_ACCESS_KEY"],
                secret_key=settings["MINIO_SECRET_KEY"],
                bucket=settings["MINIO_BUCKET"],
                secure=settings.getbool("MINIO_SECURE"),
            )
        else:
            self.storage = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):
        if not isinstance(item, MediaItem):
            return item

        adapter = item

        if not self.download_enabled:
            adapter["metadata"]["storage"] = "url_only"
            return item

        try:
            data = self._download(item["url"])
            if data is None:
                adapter["metadata"]["storage"] = "download_failed"
                return item

            object_name = self._object_name(item)
            content_type = item.get("mime_type") or ""
            minio_path = self.storage.upload(object_name, data, content_type)

            adapter["metadata"]["storage"] = "minio"
            adapter["metadata"]["minio_path"] = minio_path
            adapter["metadata"]["size_bytes"] = len(data)

        except Exception as e:
            logger.warning(f"下载/上传失败 [{item['url']}]: {e}")
            adapter["metadata"]["storage"] = "error"

        return item

    def _download(self, url, timeout=30):
        resp = requests.get(url, timeout=timeout, stream=True)
        resp.raise_for_status()
        return resp.content

    @staticmethod
    def _object_name(item):
        path = urlparse(item["url"]).path
        ext = ""
        if "." in path:
            ext = path.rsplit(".", 1)[-1].lower()
        name = item.get("filename", "unknown")
        if ext and not name.endswith(f".{ext}"):
            name = f"{name}.{ext}"
        return f"media/{item['media_type']}/{name}"


class MySQLResourcePipeline:
    """将资源记录写入 MySQL t_resources，并输出进度信息"""

    def process_item(self, item, spider):
        task_id = getattr(spider, "task_id", None)
        if not task_id:
            return item

        if isinstance(item, MediaItem):
            self._save_media(item, task_id)

        return item

    def _save_media(self, item, task_id):
        # 同一任务中相同链接去重
        session_check = next(get_session())
        try:
            if crud.resource_exists(session_check, task_id, item["url"]):
                return
        finally:
            session_check.close()

        object_id = item["metadata"].get("minio_path") or item.get("_mongo_id") or item["metadata"].get("object_id") or ""
        res_size = item["metadata"].get("size_bytes", 0)

        session = next(get_session())
        try:
            crud.create_resource(
                session=session,
                scrap_task_id=task_id,
                res_type=item["media_type"],
                website=item["source_page"],
                res_link=item["url"],
                object_id=object_id or None,
                res_size=res_size,
                extension={"alt": item["metadata"].get("alt", "")},
            )
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"MySQL 资源记录失败 [{item['url']}]: {e}")
            return
        finally:
            session.close()

        _emit_progress("resource_found", {
            "task_id": task_id,
            "res_link": item["url"],
            "res_type": item["media_type"],
            "object_id": object_id,
        })



class MongoDBPipeline:
    """将抓取结果存入 MongoDB"""

    def __init__(self, mongo_uri, mongo_database):
        self.mongo_uri = mongo_uri
        self.mongo_database = mongo_database

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_database=crawler.settings.get("MONGO_DATABASE"),
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_database]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        data = dict(item)
        data["extracted_at"] = datetime.datetime.utcnow().isoformat()

        collection = self._pick_collection(item)
        self.db[collection].create_index([("url", ASCENDING)], background=True)
        self.db[collection].replace_one({"url": data["url"]}, data, upsert=True)

        # 保存后取回 MongoDB 文档 _id
        doc = self.db[collection].find_one({"url": data["url"]}, {"_id": 1})
        if doc:
            item["_mongo_id"] = str(doc["_id"])

        # 计算文本内容大小（用于回写 MySQL res_size）
        if isinstance(item, WebPageItem):
            text = item.get("text_content", "") or ""
            item["_content_size"] = len(text.encode("utf-8"))

        return item

    @staticmethod
    def _pick_collection(item):
        name = type(item).__name__
        mapping = {
            "WebPageItem": "web_pages",
            "MediaItem": "media",
        }
        return mapping.get(name, "items")
