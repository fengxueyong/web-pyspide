import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class WSManager:
    """WebSocket 连接管理器，按 task_id 管理订阅"""

    def __init__(self):
        self._queues: dict[int, list[asyncio.Queue]] = {}

    async def subscribe(self, task_id: int) -> asyncio.Queue:
        """订阅指定任务的更新，返回一个 asyncio.Queue"""
        q: asyncio.Queue = asyncio.Queue()
        self._queues.setdefault(task_id, []).append(q)
        logger.debug(f"WS subscribe task={task_id}, total={len(self._queues[task_id])}")
        return q

    def unsubscribe(self, task_id: int, q: asyncio.Queue):
        """取消订阅"""
        queues = self._queues.get(task_id)
        if queues:
            queues.remove(q)
            if not queues:
                del self._queues[task_id]

    async def notify(self, task_id: int, event: str, data: dict[str, Any]):
        """向订阅该 task 的所有客户端推送消息"""
        message = json.dumps({"event": event, "data": data}, ensure_ascii=False)
        for q in self._queues.get(task_id, []):
            await q.put(message)


ws_manager = WSManager()
