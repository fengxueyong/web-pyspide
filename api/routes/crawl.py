import json
import logging
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter

from api.schemas.responses import CrawlRequest, CrawlResult

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("")
def trigger_crawl(req: CrawlRequest):
    """触发爬虫抓取指定 URL"""
    project_dir = Path(__file__).resolve().parent.parent.parent

    cmd = [
        sys.executable, "-m", "scrapy", "crawl", "universal",
        "-a", f"urls={req.url}",
        "-a", f"content_types={req.types}",
        "-a", f"depth={req.depth}",
    ]

    logger.info(f"启动爬虫: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_dir)

    # 从日志中提取检测到的类型
    detected = []
    for line in result.stdout.splitlines():
        if "检测到:" in line:
            parts = line.split("检测到:")
            if len(parts) > 1:
                detected = json.loads(parts[1].strip())
            break

    return CrawlResult(
        url=req.url,
        types_detected=detected,
        items_count=result.returncode,
    )
