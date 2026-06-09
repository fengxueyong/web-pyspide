from scrapling import Selector


def _first(css_result):
    return css_result[0] if css_result else None


class TextExtractor:
    """提取页面纯文本内容"""

    def extract(self, html: str, url: str) -> dict:
        page = Selector(content=html, url=url)

        title_el = _first(page.css("title"))
        title_text = title_el.text.strip() if title_el else ""

        meta_desc = _first(
            page.css('meta[name="description"], meta[property="og:description"]')
        )
        description = meta_desc.attrib.get("content", "") if meta_desc else ""

        body = _first(page.css("body"))
        text = body.text.strip() if body else ""

        paragraphs = page.css("p")
        para_texts = [
            p.text.strip()
            for p in paragraphs
            if p.text and len(p.text.strip()) > 10
        ]

        return {
            "title": title_text,
            "description": description,
            "text": text[:10000],
            "paragraphs": para_texts,
            "word_count": len(text),
        }
