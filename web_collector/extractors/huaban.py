"""
花瓣网（huaban.com）专用图片提取器。

花瓣网使用了 Cloudflare 反爬 + JS 动态渲染，通用爬虫难以获取真实页面。
但花瓣网的内部 API 接口（api.huaban.com）没有 Cloudflare 防护，
可以直接返回包含图片地址的 JSON 数据。

该提取器解析花瓣 URL 中的 pin_id，直接调用内部 API 获取图片信息。
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

        从 URL 中提取 pin_id，调用花瓣内部 API 获取 JSON 数据，
        从中提取图片信息，无需渲染页面或绕过 Cloudflare。

        参数:
            url: 花瓣网采集页面 URL（如 https://huaban.com/pins/3071148217）

        返回:
            MediaItem 列表
        """
        # 1. 从 URL 中提取 pin_id
        pin_id = self._extract_pin_id(url)
        if not pin_id:
            logger.error(f"[HuabanExtractor] 无法从 URL 提取 pin_id: {url}")
            return []

        # 2. 调用花瓣内部 API 获取图片数据
        # 此接口没有 Cloudflare 防护，普通 requests 即可访问
        api_url = f"https://api.huaban.com/pins/{pin_id}?format=json"
        try:
            resp = self.session.get(api_url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"[HuabanExtractor] API 请求失败: {api_url} — {e}")
            return []

        # 3. 解析 JSON，提取图片 URL
        pin = data.get("pin") or data
        if not pin:
            logger.warning(f"[HuabanExtractor] API 返回数据中无 pin 字段: {url}")
            return []

        file_info = pin.get("file")
        if not file_info:
            logger.warning(f"[HuabanExtractor] API 返回数据中无 file 字段: {url}")
            return []

        image_url = file_info.get("url", "")
        if not image_url:
            logger.warning(f"[HuabanExtractor] file 中无 url 字段: {url}")
            return []

        # 4. 构造 MediaItem
        image_id = hashlib.md5(image_url.encode()).hexdigest()[:16]
        width = file_info.get("width", 0)
        height = file_info.get("height", 0)
        mime_type = file_info.get("type", "image/jpeg")
        ext = mime_type.split("/")[-1] if "/" in mime_type else "jpg"

        item = MediaItem(
            url=image_url,
            source_page=url,
            media_type="image",
            filename=f"{image_id}.{ext}",
            mime_type=mime_type,
            metadata={
                "alt": pin.get("raw_text", ""),
                "width": str(width),
                "height": str(height),
                "width_int": width,
                "height_int": height,
                "ext": ext,
                "pin_id": pin_id,
                "board_id": pin.get("board_id", ""),
                "source": "huaban",
            },
        )

        logger.info(
            f"[HuabanExtractor] {url} — 提取到 1 张图片: "
            f"{width}x{height} {mime_type}"
        )
        return [item]

    @staticmethod
    def _extract_pin_id(url: str) -> str | None:
        """
        从花瓣 URL 中提取 pin_id。

        支持的 URL 格式:
        - https://huaban.com/pins/3071148217
        - https://huaban.com/pins/3071148217/
        - https://www.huaban.com/pins/3071148217
        """
        try:
            # 匹配 URL 路径中的 /pins/<数字>
            match = re.search(r"/pins/(\d+)", urlparse(url).path)
            if match:
                return match.group(1)
            return None
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
