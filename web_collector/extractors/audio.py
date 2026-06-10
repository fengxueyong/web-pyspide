import hashlib
from urllib.parse import urljoin

from scrapling import Selector


class AudioExtractor:
    """提取页面中的音频"""

    def extract(self, html: str, url: str) -> list[dict]:
        page = Selector(content=html, url=url)
        audios = []

        # <audio src="...">
        for a in page.css("audio[src]"):
            src = a.attrib.get("src", "")
            if src:
                full_url = urljoin(url, src)
                audios.append(self._make_item(full_url, "direct"))

        # <audio><source src="..."></audio>
        for s in page.css("audio source[src]"):
            src = s.attrib.get("src", "")
            if src:
                full_url = urljoin(url, src)
                audios.append(self._make_item(full_url, "source"))

        return audios

    def _make_item(self, url: str, src_type: str) -> dict:
        aid = hashlib.md5(url.encode()).hexdigest()
        ext = ""
        if "." in url:
            ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
        return {"id": aid, "url": url, "format": ext, "source_type": src_type}
