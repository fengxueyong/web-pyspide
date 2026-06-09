import hashlib
from urllib.parse import urljoin

from scrapling import Selector


class ImageExtractor:
    """提取页面中的所有图片"""

    def extract(self, html: str, url: str) -> list[dict]:
        page = Selector(content=html, url=url)
        images = []

        for img in page.css("img[src]"):
            src = img.attrib.get("src", "")
            if not src or src.startswith("data:"):
                continue

            full_url = urljoin(url, src)
            image_id = hashlib.md5(full_url.encode()).hexdigest()

            ext = ""
            if "." in full_url:
                ext = full_url.rsplit(".", 1)[-1].split("?")[0].lower()

            images.append(
                {
                    "id": image_id,
                    "url": full_url,
                    "alt": img.attrib.get("alt", ""),
                    "width": img.attrib.get("width", ""),
                    "height": img.attrib.get("height", ""),
                    "format": ext,
                }
            )

        return images
