import scrapy

from web_collector.items import WebPageItem, MediaItem
from web_collector.extractors import ContentClassifier, TextExtractor, ImageExtractor, NewsExtractor


class UniversalSpider(scrapy.Spider):
    """通用爬虫：根据 URL 和内容类型自动提取页面内容"""

    name = "universal"

    def __init__(self, urls="", content_types="text", depth=1, *args, **kwargs):
        """
        urls:          逗号分隔的 URL 列表
        content_types: 逗号分隔的目标内容类型 (text,image,news,video,audio)
        depth:         爬取深度（1=仅当前页）
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [u.strip() for u in urls.split(",") if u.strip()]
        self.target_types = [t.strip() for t in content_types.split(",") if t.strip()]
        self.max_depth = int(depth)

        self.text_extractor = TextExtractor()
        self.image_extractor = ImageExtractor()
        self.news_extractor = NewsExtractor()

    def parse(self, response):
        html = response.text
        url = response.url

        # 1. 用 Scrapling 自动分类页面内容
        classifier = ContentClassifier(html, url)
        detected = classifier.classify()
        self.logger.info(f"[{url}] 检测到: {detected}")

        # 2. 按目标类型逐一提取
        for ctype in self.target_types:
            if ctype == "text" and "text" in detected:
                yield self._extract_text(html, url)

            if ctype == "news" and "news" in detected:
                yield self._extract_news(html, url)

            if ctype == "image" and ("image" in detected or "gallery" in detected):
                yield from self._extract_images(html, url)

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

    def _extract_images(self, html, url):
        images = self.image_extractor.extract(html, url)
        for img in images:
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
