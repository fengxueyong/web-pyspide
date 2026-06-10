import logging

from fastapi import APIRouter

from api.schemas.responses import (
    ProxyConfigOut, ProxyConfigCreate, ProxyConfigUpdate, success, error,
)
from web_collector.db.engine import get_session
from web_collector.db.crud import (
    create_proxy_config, get_proxy_config, list_proxy_configs,
    update_proxy_config, delete_proxy_config,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
def list_proxies():
    """获取所有代理配置列表"""
    session = next(get_session())
    try:
        configs = list_proxy_configs(session)
        return success([ProxyConfigOut(
            id=c.id, name=c.name, proxy_http=c.proxy_http,
            proxy_https=c.proxy_https, username=c.username,
            create_time=c.create_time, update_time=c.update_time,
        ) for c in configs])
    finally:
        session.close()


@router.get("/{proxy_id}")
def get_proxy(proxy_id: int):
    """获取单个代理配置"""
    session = next(get_session())
    try:
        config = get_proxy_config(session, proxy_id)
        if not config:
            return error(4001, "代理配置不存在")
        return success(ProxyConfigOut(
            id=config.id, name=config.name, proxy_http=config.proxy_http,
            proxy_https=config.proxy_https, username=config.username,
            create_time=config.create_time, update_time=config.update_time,
        ))
    finally:
        session.close()


@router.post("")
def create_proxy(req: ProxyConfigCreate):
    """创建代理配置"""
    if not req.name or not req.name.strip():
        return error(1001, "配置名称不能为空")
    if not req.proxy_http and not req.proxy_https:
        return error(1001, "至少配置 HTTP 或 HTTPS 代理地址")

    session = next(get_session())
    try:
        config = create_proxy_config(
            session, name=req.name.strip(),
            proxy_http=req.proxy_http, proxy_https=req.proxy_https,
            username=req.username, password=req.password,
        )
        return success(ProxyConfigOut(
            id=config.id, name=config.name, proxy_http=config.proxy_http,
            proxy_https=config.proxy_https, username=config.username,
            create_time=config.create_time, update_time=config.update_time,
        ))
    finally:
        session.close()


@router.put("/{proxy_id}")
def update_proxy(proxy_id: int, req: ProxyConfigUpdate):
    """更新代理配置"""
    session = next(get_session())
    try:
        config = update_proxy_config(
            session, proxy_id, name=req.name, proxy_http=req.proxy_http,
            proxy_https=req.proxy_https, username=req.username,
            password=req.password,
        )
        if not config:
            return error(4001, "代理配置不存在")
        return success(ProxyConfigOut(
            id=config.id, name=config.name, proxy_http=config.proxy_http,
            proxy_https=config.proxy_https, username=config.username,
            create_time=config.create_time, update_time=config.update_time,
        ))
    finally:
        session.close()


@router.delete("/{proxy_id}")
def delete_proxy(proxy_id: int):
    """删除代理配置"""
    session = next(get_session())
    try:
        if not delete_proxy_config(session, proxy_id):
            return error(4001, "代理配置不存在")
        return success()
    finally:
        session.close()
