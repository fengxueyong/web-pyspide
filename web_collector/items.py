import scrapy


class WebPageItem(scrapy.Item):
    """文本/新闻类页面内容"""
    url = scrapy.Field()
    title = scrapy.Field()
    content_type = scrapy.Field()      # text / news
    html = scrapy.Field()
    text_content = scrapy.Field()
    metadata = scrapy.Field()
    extracted_at = scrapy.Field()
    depth = scrapy.Field()
    _mongo_id = scrapy.Field()
    _content_size = scrapy.Field()


class MediaItem(scrapy.Item):
    """媒体文件（图片/视频/音频）"""
    url = scrapy.Field()
    source_page = scrapy.Field()
    media_type = scrapy.Field()        # image / video / doc
    filename = scrapy.Field()
    mime_type = scrapy.Field()
    metadata = scrapy.Field()
    extracted_at = scrapy.Field()
    _mongo_id = scrapy.Field()
    _content_size = scrapy.Field()
