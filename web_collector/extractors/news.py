from scrapling import Selector


def _first(css_result):
    return css_result[0] if css_result else None


class NewsExtractor:
    """提取新闻/文章类结构化信息"""

    TITLE_SELECTORS = [
        "h1",
        'h1[itemprop="headline"]',
        ".article-title",
        ".post-title",
        ".entry-title",
        ".news-title",
    ]

    DATE_SELECTORS = [
        'meta[property="article:published_time"]',
        'meta[name="pubdate"]',
        'time[itemprop="datePublished"]',
        "time[datetime]",
        ".article-date",
        ".post-date",
        ".publish-date",
    ]

    AUTHOR_SELECTORS = [
        'meta[name="author"]',
        'meta[property="article:author"]',
        '[itemprop="author"]',
        ".article-author",
        ".post-author",
        ".byline",
        ".author-name",
    ]

    BODY_SELECTORS = [
        "article",
        '[itemprop="articleBody"]',
        ".article-content",
        ".post-content",
        ".entry-content",
        ".news-content",
        ".article-body",
    ]

    def extract(self, html: str, url: str) -> dict:
        page = Selector(content=html, url=url)

        # -- 标题 --
        title = ""
        for sel in self.TITLE_SELECTORS:
            el = _first(page.css(sel))
            if el and el.text.strip():
                title = el.text.strip()
                break
        if not title:
            title_el = _first(page.css("title"))
            title = title_el.text.strip() if title_el else ""

        # -- 发布日期 --
        pub_date = ""
        for sel in self.DATE_SELECTORS:
            el = _first(page.css(sel))
            if el:
                if el.tag == "meta":
                    pub_date = el.attrib.get("content", "")
                elif el.tag == "time":
                    pub_date = el.attrib.get("datetime", el.text.strip())
                else:
                    pub_date = el.text.strip()
                if pub_date:
                    break

        # -- 作者 --
        author = ""
        for sel in self.AUTHOR_SELECTORS:
            el = _first(page.css(sel))
            if el:
                if el.tag == "meta":
                    author = el.attrib.get("content", "")
                else:
                    author = el.text.strip()
                if author:
                    break

        # -- 正文 --
        body_text = ""
        for sel in self.BODY_SELECTORS:
            el = _first(page.css(sel))
            if el:
                text = el.text.strip()
                if len(text) > 100:
                    body_text = text
                    break

        og_image = _first(page.css('meta[property="og:image"]'))
        og_desc = _first(page.css('meta[property="og:description"]'))

        return {
            "title": title,
            "url": url,
            "published_date": pub_date,
            "author": author,
            "body_text": body_text[:20000],
            "og_image": og_image.attrib.get("content", "") if og_image else "",
            "og_description": og_desc.attrib.get("content", "") if og_desc else "",
        }
