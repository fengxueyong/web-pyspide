import datetime
import hashlib

from sqlalchemy.orm import Session

from .models import ScrapTask, Resource, ProxyConfig


def _md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ── ScrapTask ──

def create_task(session: Session, website: str, res_type: str = "all",
                depth: int = 1, link_follow: bool = False,
                save_method: str = "download",
                extension: dict | None = None,
                proxy_id: int = -1) -> ScrapTask:
    task = ScrapTask(
        website=website,
        website_hash=_md5(website),
        res_type=res_type,
        depth=depth,
        link_follow=1 if link_follow else 0,
        save_method=save_method,
        status="running",
        extension=extension,
        proxy_id=proxy_id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_task(session: Session, task_id: int) -> ScrapTask | None:
    return session.get(ScrapTask, task_id)


def list_tasks(session: Session, page: int = 1,
               page_size: int = 20) -> tuple[list[ScrapTask], int]:
    q = session.query(ScrapTask).order_by(ScrapTask.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def update_task_status(session: Session, task_id: int,
                       status: str) -> ScrapTask | None:
    task = session.get(ScrapTask, task_id)
    if not task:
        return None
    task.status = status
    if status == "finished":
        task.scrap_time = datetime.datetime.utcnow()
    elif status == "cancel":
        task.cancel_time = datetime.datetime.utcnow()
    session.commit()
    session.refresh(task)
    return task


def inc_task_res_count(session: Session, task_id: int) -> None:
    task = session.get(ScrapTask, task_id)
    if task:
        task.res_number = (task.res_number or 0) + 1
        session.commit()


def update_task_extension(session: Session, task_id: int,
                          extension: dict) -> ScrapTask | None:
    task = session.get(ScrapTask, task_id)
    if not task:
        return None
    task.extension = extension
    session.commit()
    return task


# ── Resource ──

def create_resource(session: Session, scrap_task_id: int,
                    res_type: str, website: str,
                    res_link: str | None = None,
                    parent_link: str = "-1",
                    object_id: str | None = None,
                    res_size: int = 0,
                    extension: dict | None = None) -> Resource:
    res = Resource(
        scrap_task_id=scrap_task_id,
        res_link=res_link,
        website=website,
        parent_link=parent_link,
        res_type=res_type,
        object_id=object_id,
        res_size=res_size,
        extension=extension,
    )
    session.add(res)
    session.commit()
    session.refresh(res)
    inc_task_res_count(session, scrap_task_id)
    return res


def list_distinct_websites(session: Session) -> list[str]:
    rows = session.query(ScrapTask.website).distinct().all()
    return [row[0] for row in rows]


def list_resources(session: Session, scrap_task_id: int = None,
                   res_type: str = None,
                   page: int = 1,
                   page_size: int = 20) -> tuple[list[Resource], int]:
    q = session.query(Resource).order_by(Resource.id.desc())
    if scrap_task_id is not None:
        q = q.filter(Resource.scrap_task_id == scrap_task_id)
    if res_type:
        q = q.filter(Resource.res_type == res_type)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


# ── ProxyConfig ──

def create_proxy_config(session: Session, name: str,
                        proxy_http: str | None = None,
                        proxy_https: str | None = None,
                        username: str | None = None,
                        password: str | None = None) -> ProxyConfig:
    config = ProxyConfig(
        name=name,
        proxy_http=proxy_http,
        proxy_https=proxy_https,
        username=username,
        password=password,
    )
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


def get_proxy_config(session: Session, proxy_id: int) -> ProxyConfig | None:
    return session.get(ProxyConfig, proxy_id)


def list_proxy_configs(session: Session) -> list[ProxyConfig]:
    return session.query(ProxyConfig).order_by(ProxyConfig.id.desc()).all()


def update_proxy_config(session: Session, proxy_id: int,
                        name: str | None = None,
                        proxy_http: str | None = None,
                        proxy_https: str | None = None,
                        username: str | None = None,
                        password: str | None = None) -> ProxyConfig | None:
    config = session.get(ProxyConfig, proxy_id)
    if not config:
        return None
    if name is not None:
        config.name = name
    if proxy_http is not None:
        config.proxy_http = proxy_http
    if proxy_https is not None:
        config.proxy_https = proxy_https
    if username is not None:
        config.username = username
    if password is not None:
        config.password = password
    session.commit()
    session.refresh(config)
    return config


def delete_proxy_config(session: Session, proxy_id: int) -> bool:
    config = session.get(ProxyConfig, proxy_id)
    if not config:
        return False
    session.delete(config)
    session.commit()
    return True
