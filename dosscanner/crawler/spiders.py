from typing import Any

import scrapy
from scrapy.http import Response
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor

from dosscanner.model import EndpointItem


class EndpointSpider(scrapy.Spider):
    name = "EndpointSpider"
    max_depth = 2  # Maximum crawl depth

    def __init__(self, allow_domains: list[str] = None, *args, **kwargs: Any):
        super(EndpointSpider, self).__init__(*args, **kwargs)
        self.allow_domains = allow_domains

    def parse(self, response: Response):
        """Main logic of crawler. Takes response, resolves it and processes the output

        Args:
            response (Response): The response being sent and processed

        Yields:
            An EndpointItem and scrapy.Request object for every link that was found
        """
        # Stop crawling if maximum depth is reached
        current_depth = response.meta.get("depth", 0)
        if current_depth >= self.max_depth:
            return

        link_ext = LinkExtractor(
            allow_domains=self.allow_domains,
            deny_extensions=[],
            tags=[
                "a",
                "audio",
                "area",
                "form",
                "base",
                "blockquote",
                "body",
                "button",
                "del",
                "embed",
                "form",
                "frame",
                "head",
                "iframe",
                "img",
                "input",
                "ins",
                "link",
                "object",
                "q",
                "script",
                "source",
                "video",
            ],
            attrs=["href", "action", "src", "cite", "codebase", "background"],
        )
        links: list[Link] = link_ext.extract_links(response)

        for link in links:
            yield EndpointItem(url=link.url, http_method="GET")

        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parse, method="GET")
