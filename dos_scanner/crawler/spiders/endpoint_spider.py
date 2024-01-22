from typing import Any

import scrapy
from scrapy.linkextractors import LinkExtractor

from dos_scanner.crawler.items import EndpointItem


class EndpointSpider(scrapy.Spider):
    name = "EndpointSpider"
    max_depth = 2  # Maximum crawl depth

    def __init__(self, allow_domains: list[str] = None, *args, **kwargs: Any):
        super(EndpointSpider, self).__init__(*args, **kwargs)
        self.allow_domains = allow_domains

    def parse(self, response):
        # Stop crawling if maximum depth is reached
        current_depth = response.meta.get("depth", 0)
        if current_depth >= self.max_depth:
            return

        link_ext = LinkExtractor(
            allow_domains=self.allow_domains,
            deny_extensions=[],
            tags=["a", "area", "form", "base", "link", "input"],
            attrs=["href", "action", "src", "cite"],
        )
        links = link_ext.extract_links(response)

        for link in links:
            yield EndpointItem(url=link.url)

        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse)
