from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import items, media, crawl, resources, tasks
from api.schemas.responses import success

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


@app.get("/api/health")
def health():
    return success({"status": "ok"})
