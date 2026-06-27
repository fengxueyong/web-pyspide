"""
花瓣网（huaban.com）专用图片提取器。

花瓣网使用了 Cloudflare 反爬 + JS 动态渲染，通用爬虫难以获取真实页面。
但花瓣网的内部 API 接口（api.huaban.com）没有 Cloudflare 防护，
可以直接返回包含图片地址的 JSON 数据。

该提取器支持两种 URL 格式：
  - 单图: https://huaban.com/pins/{pin_id}
  - 画板: https://huaban.com/boards/{board_id}  （含多张图片）

仅适用于 huaban.com 域名，不干扰通用提取流程。
"""

import hashlib
import logging
import re
from urllib.parse import urlparse

import requests

from web_collector.items import MediaItem

logger = logging.getLogger(__name__)


class HuabanExtractor:
    """花瓣网图片提取器，通过内部 API 获取图片，专用于 huaban.com 域名"""

    def __init__(self):
        # 普通 HTTP 会话即可，花瓣内部 API 没有 Cloudflare 防护
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Referer": "https://huaban.com/",
        })

    def extract(self, url: str) -> list[MediaItem]:
        """
        提取花瓣网页面的图片。

        自动识别 URL 类型：
        - /pins/{id}  → 单张图片
        - /boards/{id} → 画板中所有图片（最多 30 张）

        参数:
            url: 花瓣网 URL

        返回:
            MediaItem 列表
        """
        # 识别 URL 类型并获取对应数据
        pin_id = self._extract_pin_id(url)
        board_id = self._extract_board_id(url)

        if pin_id:
            # 单图模式：调用单图 API
            return self._extract_single_pin(pin_id, url)
        elif board_id:
            # 画板模式：调用画板 API 获取多张图片
            return self._extract_board_pins(board_id, url)
        else:
            logger.error(f"[HuabanExtractor] 无法识别的 URL 格式: {url}")
            return []

    def _extract_single_pin(self, pin_id: str, source_url: str) -> list[MediaItem]:
        """从单图 API 提取图片"""
        api_url = f"https://api.huaban.com/pins/{pin_id}?format=json"
        try:
            resp = self.session.get(api_url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"[HuabanExtractor] 单图 API 请求失败: {api_url} — {e}")
            return []

        pin = data.get("pin") or data
        if not pin:
            return []

        file_info = pin.get("file") or {}
        image_url = file_info.get("url", "")
        if not image_url:
            return []

        item = self._build_media_item(image_url, source_url, pin.get("file", {}),
                                      pin.get("raw_text", ""), pin_id)
        logger.info(f"[HuabanExtractor] {source_url} — 提取到 1 张图片")
        return [item]

    def _extract_board_pins(self, board_id: str, source_url: str) -> list[MediaItem]:
        """从画板 API 提取所有图片"""
        api_url = f"https://api.huaban.com/boards/{board_id}/pins"
        try:
            resp = self.session.get(api_url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"[HuabanExtractor] 画板 API 请求失败: {api_url} — {e}")
            return []

        pins = data.get("pins") or []
        if not pins:
            logger.warning(f"[HuabanExtractor] 画板无数据: {source_url}")
            return []

        results = []
        for pin in pins:
            file_info = pin.get("file") or {}
            image_url = file_info.get("url", "")
            if not image_url:
                continue

            item = self._build_media_item(
                image_url, source_url, file_info,
                pin.get("raw_text", ""),
                str(pin.get("pin_id", ""))
            )
            results.append(item)

        logger.info(f"[HuabanExtractor] {source_url} — 提取到 {len(results)} 张图片")
        return results

    @staticmethod
    def _build_media_item(image_url: str, source_url: str,
                          file_info: dict, alt_text: str,
                          pin_id: str) -> MediaItem:
        """根据图片信息构造 MediaItem"""
        image_id = hashlib.md5(image_url.encode()).hexdigest()[:16]
        width = file_info.get("width", 0)
        height = file_info.get("height", 0)
        mime_type = file_info.get("type", "image/jpeg")
        ext = mime_type.split("/")[-1] if "/" in mime_type else "jpg"

        return MediaItem(
            url=image_url,
            source_page=source_url,
            media_type="image",
            filename=f"{image_id}.{ext}",
            mime_type=mime_type,
            metadata={
                "alt": alt_text,
                "width": str(width),
                "height": str(height),
                "width_int": width,
                "height_int": height,
                "ext": ext,
                "pin_id": pin_id,
                "source": "huaban",
            },
        )

    @staticmethod
    def _extract_pin_id(url: str) -> str | None:
        """从 URL 提取 pin_id（单图），匹配 /pins/<数字>"""
        try:
            match = re.search(r"/pins/(\d+)", urlparse(url).path)
            return match.group(1) if match else None
        except Exception:
            return None

    @staticmethod
    def _extract_board_id(url: str) -> str | None:
        """从 URL 提取 board_id（画板），匹配 /boards/<数字>"""
        try:
            match = re.search(r"/boards/(\d+)", urlparse(url).path)
            return match.group(1) if match else None
        except Exception:
            return None

    @staticmethod
    def is_huaban_url(url: str) -> bool:
        """判断 URL 是否属于花瓣网"""
        try:
            netloc = urlparse(url).netloc.lower()
            return netloc.endswith("huaban.com") or netloc.endswith("huaban.com.cn")
        except Exception:
            return False
