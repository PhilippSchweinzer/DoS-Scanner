from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from dosscanner.model import Endpoint
from dosscanner.request import Requestor


class EndpointCrawler:
    def __init__(self, start_urls: list[Endpoint], allowed_domains: list[str]) -> None:
        self.allowed_domains = allowed_domains
        self.visited = set()
        self.start_urls = start_urls

    def crawl(self) -> list[Endpoint]:

        for start_url in self.start_urls:
            Requestor.enqueue(start_url)
            self.visited.add(start_url.url)

        while len(Requestor.queue) > 0:
            response_data_list = Requestor.evaluate_response_body()
            for response_data in response_data_list:
                parsed_urls = self.parse(response_data.body)
                # Convert URLs to absolute form
                parsed_urls = [urljoin(response_data.url, url) for url in parsed_urls]

                # Filter URLs by allowed domains
                filtered_urls = list(
                    filter(
                        lambda url: urlparse(url).netloc in self.allowed_domains,
                        parsed_urls,
                    )
                )

                # Add non-visited urls to the Requestor queue
                for filtered_url in filtered_urls:
                    if filtered_url not in self.visited:
                        Requestor.enqueue(Endpoint(url=filtered_url, http_method="GET"))
                        self.visited.add(filtered_url)

        endpoints = []
        print(self.visited)
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
            for attr, value in link.attrs.items():
                if attr in attrs:
                    urls.append(value)

        return urls
