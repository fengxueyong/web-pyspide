from urllib.parse import urlparse, urljoin

import scrapy

from web_collector.items import WebPageItem, MediaItem
from web_collector.extractors import (
    ContentClassifier, TextExtractor, ImageExtractor,
    NewsExtractor, DocExtractor, VideoExtractor, AudioExtractor,
)


class UniversalSpider(scrapy.Spider):
    """通用爬虫：根据 URL 和内容类型自动提取页面内容"""

    name = "universal"

    def __init__(self, urls="", content_types="text", depth=1, task_id=None, *args, **kwargs):
        """
        urls:          逗号分隔的 URL 列表
        content_types: 逗号分隔的目标内容类型 (text,image,news,video,audio)
        depth:         爬取深度（1=仅当前页）
        task_id:       关联的 MySQL 抓取任务 ID（由 CrawlService 传入）
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [u.strip() for u in urls.split(",") if u.strip()]
        self.target_types = [t.strip() for t in content_types.split(",") if t.strip()]
        self.max_depth = int(depth)
        self.task_id = int(task_id) if task_id else None

        self.text_extractor = TextExtractor()
        self.image_extractor = ImageExtractor()
        self.news_extractor = NewsExtractor()
        self.doc_extractor = DocExtractor()
        self.video_extractor = VideoExtractor()
        self.audio_extractor = AudioExtractor()

        # 全局 URL 去重（同一次爬取中相同链接只处理一次）
        self._seen_urls = set()

    def parse(self, response):
        html = response.text
        url = response.url
        cur_depth = response.meta.get("depth", 1)

        # 1. 用 Scrapling 自动分类页面内容
        classifier = ContentClassifier(html, url)
        detected = classifier.classify()
        self.logger.info(f"[{url}] （深度 {cur_depth}/{self.max_depth}）检测到: {detected}")

        # 2. 按目标类型逐一提取
        for ctype in self.target_types:
            if ctype == "text" and "text" in detected:
                yield self._extract_text(html, url)

            if ctype == "news" and "news" in detected:
                yield self._extract_news(html, url)

            if ctype == "image" and ("image" in detected or "gallery" in detected):
                yield from self._extract_images(html, url)

            if ctype == "doc":
                yield from self._extract_docs(html, url)

            if ctype == "video":
                yield from self._extract_videos(html, url)

            if ctype == "audio":
                yield from self._extract_audios(html, url)

        # 3. 链接追踪（深度 > 1 时递归爬取同域名下的链接）
        if cur_depth < self.max_depth:
            yield from self._follow_links(response)

    SKIP_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
                        ".zip", ".rar", ".7z", ".tar", ".gz", ".mp3", ".mp4",
                        ".avi", ".mov", ".wmv", ".jpg", ".jpeg", ".png", ".gif",
                        ".webp", ".svg", ".ico", ".css", ".js", ".json", ".xml"}

    def _follow_links(self, response):
        """提取当前页面中指向同站点的链接并递归爬取"""
        cur_depth = response.meta.get("depth", 1)
        allowed_domains = self._get_allowed_domains(response)

        for a in response.css("a[href]"):
            href = a.attrib.get("href", "").strip()
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            full_url = urljoin(response.url, href)
            # 去碎片
            full_url = full_url.split("#")[0]
            if not full_url or not full_url.startswith("http"):
                continue

            # 跳过非目标域名
            parsed = urlparse(full_url)
            if parsed.netloc not in allowed_domains:
                continue

            # 跳过静态资源文件
            path = parsed.path.lower()
            if any(path.endswith(ext) for ext in self.SKIP_EXTENSIONS):
                continue

            yield scrapy.Request(full_url, callback=self.parse, priority=cur_depth * 10)

    @staticmethod
    def _get_allowed_domains(response):
        """从响应 URL 提取同站点域名列表（含 www 前缀变体）"""
        parsed = urlparse(response.url)
        domains = {parsed.netloc}
        hostname = parsed.hostname or ""
        if hostname.startswith("www."):
            domains.add(hostname[4:])
        else:
            domains.add(f"www.{hostname}")
        return domains

    def _dedup_url(self, url: str) -> bool:
        """返回 True 表示首次见到的 URL，False 表示重复"""
        if url in self._seen_urls:
            return False
        self._seen_urls.add(url)
        return True

    def _extract_text(self, html, url):
        data = self.text_extractor.extract(html, url)
        return WebPageItem(
            url=url,
            title=data["title"],
            content_type="text",
            html=html,
            text_content=data["text"],
            metadata={
                "description": data["description"],
                "word_count": data["word_count"],
            },
        )

    def _extract_news(self, html, url):
        data = self.news_extractor.extract(html, url)
        return WebPageItem(
            url=url,
            title=data["title"],
            content_type="news",
            html=html,
            text_content=data["body_text"],
            metadata={
                "published_date": data["published_date"],
                "author": data["author"],
                "og_image": data["og_image"],
                "og_description": data["og_description"],
            },
        )

    def _extract_docs(self, html, url):
        docs = self.doc_extractor.extract(html, url)
        for doc in docs:
            if not self._dedup_url(doc["url"]):
                continue
            yield MediaItem(
                url=doc["url"],
                source_page=url,
                media_type="doc",
                filename=doc["id"],
                metadata={
                    "format": doc["format"],
                    "text": doc["text"],
                },
            )

    def _extract_videos(self, html, url):
        videos = self.video_extractor.extract(html, url)
        for v in videos:
            if not self._dedup_url(v["url"]):
                continue
            yield MediaItem(
                url=v["url"],
                source_page=url,
                media_type="video",
                filename=v["id"],
                metadata={"format": v["format"], "source_type": v["source_type"]},
            )

    def _extract_audios(self, html, url):
        audios = self.audio_extractor.extract(html, url)
        for a in audios:
            if not self._dedup_url(a["url"]):
                continue
            yield MediaItem(
                url=a["url"],
                source_page=url,
                media_type="audio",
                filename=a["id"],
                metadata={"format": a["format"], "source_type": a["source_type"]},
            )

    def _extract_images(self, html, url):
        images = self.image_extractor.extract(html, url)
        for img in images:
            if not self._dedup_url(img["url"]):
                continue
            yield MediaItem(
                url=img["url"],
                source_page=url,
                media_type="image",
                filename=f"{img['id']}.{img['format']}" if img["format"] else img["id"],
                metadata={
                    "alt": img["alt"],
                    "width": img["width"],
                    "height": img["height"],
                },
            )
