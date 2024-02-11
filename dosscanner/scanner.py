from urllib.parse import urlparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from dosscanner.crawler.spiders import EndpointSpider
from dosscanner.database import connection
from dosscanner.model import EndpointItem, MeasuredEndpointItem
from dosscanner.timer.measure import measure_endpoint


class DoSScanner:
    def __init__(self, target: str, scrapy_settings: dict = None) -> None:
        self.target = target
        self.scrapy_settings = scrapy_settings

    def scan_target(self) -> list[str]:
        # Get a list of endpoints
        endpoints = self._crawl()
        # Analyze the endpoints
        measured_endpoints = self._measure(endpoints)

        return measured_endpoints

    def _crawl(self):
        settings = get_project_settings()
        settings.setdict(self.scrapy_settings)

        process = CrawlerProcess(settings)
        process.crawl(
            EndpointSpider,
            allow_domains=[urlparse(self.target).netloc],
            start_urls=[self.target],
        )
        process.start()

        with connection:
            endpoint_data = [
                row
                for row in connection.execute(
                    "SELECT url, http_method FROM Endpoint"
                ).fetchall()
            ]
            endpoints = []
            for data in endpoint_data:
                endpoints.append(EndpointItem(data[0], data[1]))
            return endpoints

    def _measure(self, endpoints: list[EndpointItem]) -> list[MeasuredEndpointItem]:
        measured_enpoints = []
        for endpoint in endpoints:
            measurement = measure_endpoint(
                endpoint=endpoint, count=10, algorithm="arithmetic"
            )
            measured_enpoints.append(
                MeasuredEndpointItem(endpoint.url, endpoint.http_method, measurement)
            )

        return measured_enpoints
