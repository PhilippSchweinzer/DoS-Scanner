from urllib.parse import urlparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from dosscanner.crawler.spiders import EndpointSpider
from dosscanner.database import connection
from dosscanner.model import EndpointItem, MeasuredEndpointItem
from dosscanner.mutation.mutators import Mutator
from dosscanner.statistics.statistics import coefficient_of_variation
from dosscanner.timer.measure import measure_endpoint


class DoSScanner:
    def __init__(self, target: str, scrapy_settings: dict = None) -> None:
        self.target = target
        self.scrapy_settings = scrapy_settings
        self.mutator = None

    def set_mutator(self, mutator: Mutator):
        self.mutator = mutator

    def scan_target(self) -> list[str]:
        if self.mutator is None:
            raise Exception("No mutator set!")

        # Get a list of endpoints
        endpoints = self._crawl()

        vulnerable_endpoint = []
        for endpoint in endpoints:
            measured_endpoints = []
            # Mutate the endpoint and measure the response times
            for mutated_endpoint in self.mutator.next(endpoint):
                measured_endpoint = self._measure_endpoint(mutated_endpoint)
                measured_endpoints.append(measured_endpoint)
            # Calculate the coefficient of variation over all mutated versions of the original endpoint
            cv = coefficient_of_variation(
                [endpoint.measurement for endpoint in measured_endpoints]
            )

            if cv > 0.6:
                vulnerable_endpoint.append(endpoint)

        return vulnerable_endpoint

    def _crawl(self) -> list[EndpointItem]:
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

    def _measure_endpoint(self, endpoint: EndpointItem) -> MeasuredEndpointItem:
        measurement = measure_endpoint(
            endpoint=endpoint, count=10, algorithm="arithmetic"
        )
        return MeasuredEndpointItem(endpoint.url, endpoint.http_method, measurement)

    def _measure_endpoints(
        self, endpoints: list[EndpointItem]
    ) -> list[MeasuredEndpointItem]:
        measured_enpoints = []
        for endpoint in endpoints:
            measurement = measure_endpoint(
                endpoint=endpoint, count=10, algorithm="arithmetic"
            )
            measured_enpoints.append(
                MeasuredEndpointItem(endpoint.url, endpoint.http_method, measurement)
            )

        return measured_enpoints
