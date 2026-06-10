import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "web_collector"

SPIDER_MODULES = ["web_collector.spiders"]
NEWSPIDER_MODULE = "web_collector.spiders"

ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 1.0
COOKIES_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

ITEM_PIPELINES = {
    "web_collector.pipelines.MediaPipeline": 200,
    "web_collector.pipelines.MongoDBPipeline": 250,
    "web_collector.pipelines.MySQLResourcePipeline": 300,
}

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "web_collector")

# MinIO 对象存储（存图片/视频/音频等二进制文件）
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "admin123456")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "web-collector")

# 媒体文件下载开关（关闭则仅记录 URL，不下传文件）
MEDIA_DOWNLOAD = os.getenv("MEDIA_DOWNLOAD", "false").lower() == "true"

# 爬虫深度
MAX_DEPTH = int(os.getenv("MAX_DEPTH", "2"))

# MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "web_collector")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root123456")
