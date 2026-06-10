import hashlib
from urllib.parse import urljoin, urlparse

from scrapling import Selector

DOC_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx", ".txt", ".csv",
}


class DocExtractor:
    """提取页面中的文档链接"""

    def extract(self, html: str, url: str) -> list[dict]:
        page = Selector(content=html, url=url)
        docs = []

        for a in page.css("a[href]"):
            href = a.attrib.get("href", "").strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            full_url = urljoin(url, href)
            path = urlparse(full_url).path.lower()

            ext = ""
            if "." in path:
                ext = path.rsplit(".", 1)[-1].split("?")[0].lower()
                if f".{ext}" not in DOC_EXTENSIONS:
                    continue
            else:
                continue

            doc_id = hashlib.md5(full_url.encode()).hexdigest()
            docs.append({
                "id": doc_id,
                "url": full_url,
                "format": ext,
                "text": a.text.strip() or "",
            })

        return docs
