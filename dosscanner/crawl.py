from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests import RequestException

from dosscanner.model import Endpoint


class EndpointCrawler:
    def __init__(self, start_urls: list[str], allowed_domains: list[str]) -> None:
        self.allowed_domains = allowed_domains
        self.visited = set()
        self.queue = start_urls

    def crawl(self) -> list[Endpoint]:
        while len(self.queue) != 0:
            url = self.queue.pop(0)

            if url in self.visited:
                continue

            try:
                resp = requests.get(url)
                parsed_urls = self.parse(resp.text)
                # Convert URLs to absolute form
                parsed_urls = [urljoin(resp.url, url) for url in parsed_urls]

                # Filter URLs by allowed domains
                filtered_urls = list(
                    filter(
                        lambda url: urlparse(url).netloc in self.allowed_domains,
                        parsed_urls,
                    )
                )
                self.queue.extend(filtered_urls)
            except RequestException as exc:
                pass

            self.visited.add(url)

        endpoints = []
        for url in self.visited:
            endpoints.append(Endpoint(url=url, http_method="GET"))

        return endpoints

    def parse(self, data: str) -> list[str]:
        urls = []
        soup = BeautifulSoup(data, "html.parser")

        tags = [
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
        ]
        attrs = ["href", "action", "src", "cite", "codebase", "background"]

        for link in soup.find_all(tags):
            # print(link)
            for attr, value in link.attrs.items():
                if attr in attrs:
                    urls.append(value)

        return urls
