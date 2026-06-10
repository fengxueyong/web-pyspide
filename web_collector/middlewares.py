import os
import logging

logger = logging.getLogger(__name__)


class ProxyMiddleware:
    """从环境变量 HTTP_PROXY / HTTPS_PROXY 读取代理配置并应用到每个请求。"""

    def process_request(self, request, spider):
        # 优先使用 Spider 或 settings 中指定的 proxy
        if "proxy" in request.meta:
            return

        http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
        https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

        url = request.url
        proxy = None
        if url.startswith("https://") and https_proxy:
            proxy = https_proxy
        elif url.startswith("http://") and http_proxy:
            proxy = http_proxy

        if proxy:
            request.meta["proxy"] = proxy
        else:
            logger.debug(f"未配置代理: {url[:60]}")
