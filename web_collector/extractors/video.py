import hashlib
from urllib.parse import urljoin

from scrapling import Selector


class VideoExtractor:
    """提取页面中的视频"""

    def extract(self, html: str, url: str) -> list[dict]:
        page = Selector(content=html, url=url)
        videos = []

        # <video src="...">
        for v in page.css("video[src]"):
            src = v.attrib.get("src", "")
            if src:
                full_url = urljoin(url, src)
                videos.append(self._make_item(full_url, "direct"))

        # <video><source src="..."></video>
        for s in page.css("video source[src]"):
            src = s.attrib.get("src", "")
            if src:
                full_url = urljoin(url, src)
                videos.append(self._make_item(full_url, "source"))

        # iframe 嵌入（YouTube / B站 / 优酷等）
        for iframe in page.css("iframe[src]"):
            src = iframe.attrib.get("src", "")
            if src:
                full_url = urljoin(url, src)
                videos.append(self._make_item(full_url, "embed"))

        return videos

    def _make_item(self, url: str, src_type: str) -> dict:
        vid = hashlib.md5(url.encode()).hexdigest()
        ext = ""
        if "." in url:
            ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
        return {"id": vid, "url": url, "format": ext, "source_type": src_type}
