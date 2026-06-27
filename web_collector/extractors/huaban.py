"""
花瓣网（huaban.com）专用图片提取器。

花瓣网使用了 Cloudflare 反爬 + JS 动态渲染，
通用爬虫的 Scrapling/Playwright 方式难以获取真实内容。

该提取器使用 cloudscraper（绕过 Cloudflare）
直接请求花瓣页面，拿到真实 HTML 后提取图片 URL。
仅适用于 huaban.com 域名，不干扰通用提取流程。
"""

import hashlib
import logging
from urllib.parse import urljoin

import cloudscraper

from web_collector.items import MediaItem

logger = logging.getLogger(__name__)


class HuabanExtractor:
    """花瓣网图片提取器，专用于 huaban.com 域名"""

    # 花瓣网 CDN 域名前缀，用于过滤非图片资源
    IMAGE_DOMAINS = (
        "gd-hbimg-edge.huaban.com",
        "gd-hbimg.huaban.com",
        "img.hbimg.com",
    )

    def __init__(self):
        # cloudscraper：绕过 Cloudflare 验证的 HTTP 客户端
        # 模拟真实浏览器指纹，自动处理 Cloudflare 的 JS 挑战
        self.scraper = cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "mobile": False,
            }
        )

    def extract(self, url: str) -> list[MediaItem]:
        """
        提取花瓣网页面中的所有图片。

        参数:
            url: 花瓣网画板/采集页面 URL（如 https://huaban.com/pins/3071148217）

        返回:
            MediaItem 列表，每条包含图片 URL、类型等元数据
        """
        try:
            # 请求页面，cloudscraper 会自动处理 Cloudflare 验证
            resp = self.scraper.get(url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"[HuabanExtractor] 请求失败: {url} — {e}")
            return []

        html = resp.text
        results = []
        seen = set()

        # 从 HTML 中提取所有 <img> 标签
        # 花瓣网的图片使用 class="hb-image" 或普通 <img>
        from scrapling import Selector
        page = Selector(content=html, url=url)

        for img in page.css("img[src]"):
            # 优先使用 data-src（懒加载图片），降级到 src
            src = (
                img.attrib.get("lazysrc")
                or img.attrib.get("data-src")
                or img.attrib.get("data-original")
                or img.attrib.get("src")
                or ""
            )

            # 过滤掉 base64 内联图片
            if not src or src.startswith("data:") or src.startswith("blob:"):
                continue

            # 转为绝对 URL
            full_url = urljoin(url, src)

            # 去重
            if full_url in seen:
                continue
            seen.add(full_url)

            # 提取文件扩展名
            ext = ""
            if "." in full_url:
                ext = full_url.rsplit(".", 1)[-1].split("?")[0].lower()

            # 生成唯一 ID
            image_id = hashlib.md5(full_url.encode()).hexdigest()[:16]

            results.append(MediaItem(
                url=full_url,
                source_page=url,
                media_type="image",
                filename=f"{image_id}.{ext}" if ext else image_id,
                mime_type=f"image/{ext}" if ext else "image/jpeg",
                metadata={
                    "alt": img.attrib.get("alt", ""),
                    "width": img.attrib.get("width", ""),
                    "height": img.attrib.get("height", ""),
                    "width_int": _safe_int(img.attrib.get("width", 0)),
                    "height_int": _safe_int(img.attrib.get("height", 0)),
                    "ext": ext,
                    "source": "huaban",
                },
            ))

        logger.info(
            f"[HuabanExtractor] {url} — 提取到 {len(results)} 张图片"
        )
        return results

    def is_huaban_url(self, url: str) -> bool:
        """判断 URL 是否属于花瓣网"""
        from urllib.parse import urlparse
        try:
            netloc = urlparse(url).netloc.lower()
            return netloc.endswith("huaban.com") or netloc.endswith("huaban.com.cn")
        except Exception:
            return False


def _safe_int(val) -> int:
    """安全转整数，失败返回 0"""
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0
