from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from dosscanner.logger import Logger
from dosscanner.model import Endpoint
from dosscanner.request import Requestor


class EndpointCrawler:
    def __init__(
        self, start_url: Endpoint, allowed_domains: list[str], max_crawl_depth: int
    ) -> None:
        self.allowed_domains = allowed_domains
        self.visited = []
        self.start_url = start_url
        self.max_crawl_depth = max_crawl_depth

    def crawl(self) -> list[Endpoint]:
        """Starts the crawling process and generates a list of all endpoints which are found.


        Returns:
            list[Endpoint]: All endpoints which were found during the crawler process
        """
        # Initialize crawler with start url and start the process
        Requestor.enqueue(self.start_url)
        self.visited.append(self.start_url)

        crawl_depth = 0
        while len(Requestor.queue) > 0:
            Logger.debug(f"Crawling depth {crawl_depth} reached")
            response_data_list = Requestor.evaluate_response_data()
            for response_data in response_data_list:
                if response_data is None:
                    continue
                parsed_urls = self.parse(response_data.body)
                # Convert URLs to absolute form
                parsed_urls = [
                    urljoin(response_data.endpoint.url, url) for url in parsed_urls
                ]

                # Filter URLs by allowed domains
                filtered_urls = list(
                    filter(
                        lambda url: urlparse(url).netloc in self.allowed_domains,
                        parsed_urls,
                    )
                )

                # Convert URLs to Endpoints objects
                new_endpoints = [
                    Endpoint(url=filtered_url, http_method="GET")
                    for filtered_url in filtered_urls
                ]

                # Add non-visited urls to the Requestor queue
                for new_endpoint in new_endpoints:
                    if new_endpoint not in self.visited:
                        Requestor.enqueue(new_endpoint)
                        self.visited.append(new_endpoint)

            crawl_depth += 1

            # If maximum crawl depth is reached, clear queue and exit loop
            if crawl_depth >= self.max_crawl_depth:
                Requestor.queue.clear()
                break

        # Return all found/visited endpoints
        return self.visited

    def parse(self, data: str) -> list[str]:
        """Parses the response body of an http call and searches for endpoints

        Args:
            data (str): Response body in which endpoints are searched

        Returns:
            list[str]: All found endpoints
        """
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
