from scrapling import Selector


def _first(css_result):
    """取 css 返回的第一个元素，没有则返回 None"""
    return css_result[0] if css_result else None


class ContentClassifier:
    """基于 Scrapling 智能解析的页面内容分类器"""

    NEWS_SELECTORS = [
        "article",
        '[role="main"]',
        ".post-content",
        ".article-content",
        ".entry-content",
        ".news-content",
        ".article-body",
        "main article",
        '[itemprop="articleBody"]',
    ]

    def __init__(self, html: str, url: str):
        self.page = Selector(content=html, url=url)
        self.html = html

    def classify(self) -> list[str]:
        """检测页面包含哪些内容类型，返回类型名列表"""
        types = set()

        # -- 图片 --
        images = self.page.css("img[src]")
        img_count = len(images)
        if img_count > 5:
            types.add("gallery")
        if img_count > 0:
            types.add("image")

        # -- 视频 --
        video_selectors = (
            'video[src]',
            'iframe[src*="youtube"]',
            'iframe[src*="bilibili"]',
            'iframe[src*="youku"]',
            'iframe[src*="v.qq.com"]',
        )
        if any(self.page.css(sel) for sel in video_selectors):
            types.add("video")

        # -- 新闻/文章 --
        for sel in self.NEWS_SELECTORS:
            el = _first(self.page.css(sel))
            if el and len(el.text) > 200:
                types.add("news")
                break

        # 标题关键词辅助判断
        title_el = _first(self.page.css("title"))
        if title_el:
            title = title_el.text.strip().lower()
            keywords = ["新闻", "报道", "公告", "通知", "article", "news", "blog"]
            if any(kw in title for kw in keywords):
                types.add("news")

        types.add("text")  # 任何页面都有文本
        return list(types)
