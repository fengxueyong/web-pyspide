import logging

from fastapi import APIRouter

from api.schemas.responses import success
from web_collector.db import get_session, crud

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/websites")
def list_websites():
    """
    查询所有抓取任务中不重复的网址列表。
    """
    session = next(get_session())
    try:
        websites = crud.list_distinct_websites(session)
    except Exception as e:
        logger.exception("查询网址列表失败")
        return success([])
    finally:
        session.close()

    return success(websites)
