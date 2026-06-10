import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.schemas.responses import (
    CrawlRequest, CrawlResponse, success, error,
)
from web_collector.service.crawl_service import crawl_service
from web_collector.service.ws_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


VALID_RES_TYPES = {"all", "text/article", "image", "doc", "audio", "video"}
VALID_SAVE_METHODS = {"only_record", "download"}


def _validate(req: CrawlRequest) -> str | None:
    """参数校验，返回 None 表示通过，否则返回错误描述"""
    if not req.website or not req.website.strip():
        return "网址不能为空"

    if req.res_type not in VALID_RES_TYPES:
        return f"不支持的资源类型: {req.res_type}"

    if req.depth not in (1, 2, 3):
        return "抓取深度只能为 1/2/3"

    if req.depth > 1 and not req.link_follow:
        return "抓取深度大于 1 时必须跟随链接"

    if req.save_method not in VALID_SAVE_METHODS:
        return f"不支持的保存方式: {req.save_method}"

    return None


@router.post("")
def trigger_crawl(req: CrawlRequest):
    """
    创建抓取任务并启动爬虫。
    - 校验所有参数
    - 写入 t_scrap_task（事务）
    - 后台启动 Scrapy 爬虫
    - 返回 task_id
    """
    err = _validate(req)
    if err:
        return error(1001, err)

    try:
        task_id = crawl_service.create_and_start(
            website=req.website.strip(),
            res_type=req.res_type,
            depth=req.depth,
            link_follow=req.link_follow,
            save_method=req.save_method,
            proxy_id=req.proxy_id,
        )
    except Exception as e:
        logger.exception("创建抓取任务失败")
        return error(3001, f"创建任务失败: {e}")

    return success(CrawlResponse(task_id=task_id))


@router.websocket("/ws/{task_id}")
async def crawl_ws(websocket: WebSocket, task_id: int):
    """
    WebSocket 端点：实时推送指定任务的抓取进度。
    每发现一个资源推送一条 {"event":"resource_found","data":{...}}
    任务完成后推送 {"event":"task_finished","data":{"task_id":...}}
    """
    await websocket.accept()
    q = await ws_manager.subscribe(task_id)
    try:
        while True:
            message = await q.get()
            await websocket.send_text(message)
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.unsubscribe(task_id, q)
