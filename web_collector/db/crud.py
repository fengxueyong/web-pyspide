import datetime
import hashlib

from sqlalchemy.orm import Session

from .models import ScrapTask, Resource


def _md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ── ScrapTask ──

def create_task(session: Session, website: str, res_type: str = "all",
                depth: int = 1, link_follow: bool = False,
                save_method: str = "download",
                extension: dict | None = None) -> ScrapTask:
    task = ScrapTask(
        website=website,
        website_hash=_md5(website),
        res_type=res_type,
        depth=depth,
        link_follow=1 if link_follow else 0,
        save_method=save_method,
        status="running",
        extension=extension,
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
