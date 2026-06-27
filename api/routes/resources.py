import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from api.schemas.responses import success, error, paginated
from web_collector.service.resource_service import resource_service

logger = logging.getLogger(__name__)

router = APIRouter()

VALID_RES_TYPES = {"all", "image", "doc", "video"}


def _parse_time(val: Optional[str]) -> Optional[datetime]:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val)
    except ValueError:
        raise ValueError(f"时间格式错误，应为 ISO 格式: {val}")


@router.get("")
def list_resources(
    website: str = Query(..., description="网址"),
    res_type: str = Query(..., description="资源类型"),
    min_time: Optional[str] = Query(None, description="最小抓取时间（ISO格式）"),
    max_time: Optional[str] = Query(None, description="最大抓取时间（ISO格式）"),
    page: int = Query(..., ge=1, description="当前页"),
    page_size: int = Query(..., ge=1, le=100, description="每页大小"),
):
    """
    资源列表查询（联合 t_resources + t_scrap_task）。
    """
    # ── 校验 ──
    if not website.strip():
        return error(1001, "网址不能为空")
    if res_type not in VALID_RES_TYPES:
        return error(1001, f"不支持的资源类型: {res_type}")

    try:
        min_dt = _parse_time(min_time)
        max_dt = _parse_time(max_time)
    except ValueError as e:
        return error(1001, str(e))

    if (min_dt is None) != (max_dt is None):
        return error(1001, "最小抓取时间和最大抓取时间必须同时为空或同时不为空")
    if min_dt is not None and max_dt is not None and max_dt <= min_dt:
        return error(1001, "最大抓取时间必须大于最小抓取时间")

    # ── 查询 ──
    try:
        items, total = resource_service.list_resources(
            website=website.strip(),
            res_type=res_type,
            min_time=min_dt,
            max_time=max_dt,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.exception("资源列表查询失败")
        return error(3001, f"查询失败: {e}")

    return paginated(items=items, total=total, page=page, page_size=page_size)


@router.get("/{resource_id}")
def get_resource(resource_id: int):
    """
    单个资源查询。返回资源详细信息及对应存储后端的数据。
    """
    if resource_id <= 0:
        return error(1001, "资源ID不合法")

    try:
        data = resource_service.get_resource(resource_id)
    except Exception as e:
        logger.exception("资源详情查询失败")
        return error(3001, f"查询失败: {e}")

    if not data:
        return error(4001, "资源不存在")

    return success(data)
