import logging
import os
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import items, media, crawl, resources, tasks, proxy
from api.schemas.responses import success

# ── 日志配置 ──
_log_dir = os.getenv("LOG_DIR", "logs")
os.makedirs(_log_dir, exist_ok=True)

_log_file = os.path.join(_log_dir, "web-collector.log")

_handler_file = RotatingFileHandler(_log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
_handler_console = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[_handler_console, _handler_file],
)

app = FastAPI(title="Web Collector API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router, prefix="/api/items", tags=["内容"])
app.include_router(media.router, prefix="/api/media", tags=["媒体"])
app.include_router(crawl.router, prefix="/api/crawl", tags=["爬虫"])
app.include_router(resources.router, prefix="/api/resources", tags=["资源"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["任务"])
app.include_router(proxy.router, prefix="/api/proxy", tags=["代理"])


@app.get("/api/health")
def health():
    return success({"status": "ok"})
