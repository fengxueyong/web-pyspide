import datetime
import logging
from urllib.parse import urlparse

import requests
from pymongo import MongoClient, ASCENDING

from web_collector.items import MediaItem
from web_collector.storage import MinioStorage

logger = logging.getLogger(__name__)


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

        adapter = item  # MediaItem 本身就是 Item 子类

        if not self.download_enabled:
            adapter["metadata"]["storage"] = "url_only"
            return item

        try:
            data = self._download(item["url"])
            if data is None:
                adapter["metadata"]["storage"] = "download_failed"
                return item

            # 上传 MinIO
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
        """生成 MinIO 中的对象路径: media/{type}/{filename}"""
        path = urlparse(item["url"]).path
        ext = ""
        if "." in path:
            ext = path.rsplit(".", 1)[-1].lower()
        name = item.get("filename", "unknown")
        if ext and not name.endswith(f".{ext}"):
            name = f"{name}.{ext}"
        return f"media/{item['media_type']}/{name}"


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
        # 按 URL 去重：同一 URL 的相同类型只保留最新一条
        self.db[collection].create_index(
            [("url", ASCENDING)], background=True
        )
        self.db[collection].replace_one(
            {"url": data["url"]}, data, upsert=True
        )
        return item

    @staticmethod
    def _pick_collection(item):
        name = type(item).__name__
        mapping = {
            "WebPageItem": "web_pages",
            "MediaItem": "media",
        }
        return mapping.get(name, "items")
