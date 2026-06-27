import asyncio
import json
import logging
import os
import subprocess
import sys
import threading

from web_collector.db import get_session, crud
from web_collector.service.ws_manager import ws_manager

logger = logging.getLogger(__name__)

PROGRESS_PREFIX = "__CRAWL_PROGRESS__:"


# API 资源类型 → 蜘蛛 content_types 映射（仅图片/文档/视频）
RES_TYPE_MAP = {
    "all": "image,video,doc",
    "image": "image",
    "video": "video",
    "doc": "doc",
}


class CrawlService:
    """
    爬虫业务逻辑：创建任务 → 执行爬取 → 更新状态
    多表操作在事务中完成。
    """

    def create_and_start(self, website: str, res_type: str,
                         depth: int, link_follow: bool,
                         save_method: str, proxy_id: int = -1,
                         render_js: bool = True) -> int:
        """
        创建抓取任务并启动后台爬取，返回 task_id。
        事务：写入 t_scrap_task
        """
        session = next(get_session())
        try:
            task = crud.create_task(
                session=session,
                website=website,
                res_type=res_type,
                depth=depth,
                link_follow=link_follow,
                save_method=save_method,
                proxy_id=proxy_id,
            )
            task_id = task.id
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        thread = threading.Thread(
            target=self._run_crawl,
            args=(task_id, website, res_type, depth, proxy_id, render_js),
            daemon=True,
        )
        thread.start()
        return task_id

    def _run_crawl(self, task_id: int, website: str,
                   res_type: str, depth: int, proxy_id: int = -1,
                   render_js: bool = True):
        # 转换资源类型为蜘蛛识别的 content_types
        spider_types = RES_TYPE_MAP.get(res_type, "")
        if not spider_types:
            logger.warning(f"[task={task_id}] 不支持的资源类型: {res_type}，跳过爬取")
            return
        """
        后台执行 Scrapy 爬虫（子进程），
        逐行读取 stdout 中的进度信息并推送 WebSocket。
        """
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        env = os.environ.copy()
        env["CRAWL_TASK_ID"] = str(task_id)
        env["PYTHONUNBUFFERED"] = "1"

        # 根据 proxy_id 配置子进程代理环境变量
        if proxy_id == -1:
            # 不走代理：清除可能继承的代理环境变量
            env.pop("HTTP_PROXY", None)
            env.pop("HTTPS_PROXY", None)
            env.pop("http_proxy", None)
            env.pop("https_proxy", None)
        else:
            # 从数据库读取代理配置
            session = next(get_session())
            try:
                config = crud.get_proxy_config(session, proxy_id)
                if config:
                    if config.proxy_http:
                        env["HTTP_PROXY"] = config.proxy_http
                    if config.proxy_https:
                        env["HTTPS_PROXY"] = config.proxy_https
            except Exception:
                logger.exception(f"[task={task_id}] 读取代理配置失败，不使用代理")
                env.pop("HTTP_PROXY", None)
                env.pop("HTTPS_PROXY", None)
                env.pop("http_proxy", None)
                env.pop("https_proxy", None)
            finally:
                session.close()

        cmd = [
            sys.executable, "-m", "scrapy", "crawl", "universal",
            "-a", f"urls={website}",
            "-a", f"content_types={spider_types}",
            "-a", f"depth={depth}",
            "-a", f"task_id={task_id}",
            "-a", f"render_js={str(render_js).lower()}",
            "-s", f"DEPTH_LIMIT={depth}",
        ]

        logger.info(f"[task={task_id}] 启动爬虫: {' '.join(cmd)}")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, cwd=project_dir, env=env, bufsize=1,
            )

            for line in process.stdout:
                line = line.strip()
                if line.startswith(PROGRESS_PREFIX):
                    payload = line[len(PROGRESS_PREFIX):]
                    try:
                        msg = json.loads(payload)
                        loop.run_until_complete(
                            ws_manager.notify(task_id, msg["event"], msg["data"])
                        )
                    except Exception as e:
                        logger.error(f"[task={task_id}] WS 通知失败: {e}")
                else:
                    logger.info(f"[task={task_id}] {line}")

            process.wait()
            if process.returncode == 0:
                logger.info(f"[task={task_id}] 爬取完成")
            else:
                logger.warning(f"[task={task_id}] 爬虫退出码={process.returncode}，最后200行输出如上")

        except Exception as e:
            logger.error(f"[task={task_id}] 爬虫异常: {e}")

        # 更新任务状态为 finished（事务）
        session = next(get_session())
        try:
            crud.update_task_status(session, task_id, "finished")
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

        # WS 通知任务完成
        try:
            loop.run_until_complete(
                ws_manager.notify(task_id, "task_finished", {"task_id": task_id})
            )
        except Exception as e:
            logger.warning(f"[task={task_id}] WS 通知失败: {e}")
        finally:
            loop.close()


crawl_service = CrawlService()
