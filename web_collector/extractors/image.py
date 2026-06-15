import hashlib
from urllib.parse import urljoin

from scrapling import Selector


class ImageExtractor:
    """提取页面中的所有图片，支持 src 和 data-src（懒加载）"""

    def extract(self, html: str, url: str) -> list[dict]:
        page = Selector(content=html, url=url)
        images = []
        seen = set()

        for img in page.css("img"):
            # 优先用 data-src（懒加载），再降级到 src
            src = (img.attrib.get("lazysrc") or
                   img.attrib.get("data-src") or
                   img.attrib.get("data-original") or
                   img.attrib.get("src") or "")
            if not src or src.startswith("data:") or src.startswith("blob:"):
                continue

            full_url = urljoin(url, src)
            if full_url in seen:
                continue
            seen.add(full_url)

            image_id = hashlib.md5(full_url.encode()).hexdigest()

            ext = ""
            if "." in full_url:
                ext = full_url.rsplit(".", 1)[-1].split("?")[0].lower()

            images.append(
                {
                    "id": image_id,
                    "url": full_url,
                    "alt": (img.attrib.get("alt") or
                            img.attrib.get("data-alt") or ""),
                    "width": (img.attrib.get("width") or
                              img.attrib.get("data-width") or ""),
                    "height": (img.attrib.get("height") or
                               img.attrib.get("data-height") or ""),
                    "format": ext,
                }
            )

        return images
