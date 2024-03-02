import sys
from urllib.parse import urlparse

from dosscanner.crawl import EndpointCrawler
from dosscanner.logger import Logger
from dosscanner.measure import measure_endpoint
from dosscanner.model import Endpoint, MeasuredEndpoint
from dosscanner.mutation.mutator import Mutator
from dosscanner.statistics import coefficient_of_variation


class DoSScanner:
    def __init__(self, target: str, mutator: Mutator) -> None:
        self.target = target
        self.mutator = mutator

    def scan_target(self) -> list[str]:

        # Get a list of endpoints by crawling the target
        Logger.info("Starting crawler...")
        crawler = EndpointCrawler(
            start_urls=[self.target], allowed_domains=[urlparse(self.target).netloc]
        )

        endpoints = crawler.crawl()

        Logger.debug(f"{len(endpoints)} unique endpoints were found by the crawler:")
        for endpoint in endpoints:
            Logger.debug(f"{endpoint}")

        Logger.info("Mutating endpoints and evaluating DoS score...")
        vulnerable_endpoints = []
        # Iterate over all endpoints to evaluate them
        for endpoint in endpoints:
            measured_endpoints = []
            # Mutate the endpoint until the generating mutator is empty
            for mutated_endpoint in self.mutator.next(endpoint):
                # Measure the response time of the mutated endpoint
                Logger.trace(f"Mutated endpoint: {mutated_endpoint}")
                measured_endpoint = self._measure_endpoint(mutated_endpoint)
                Logger.trace(f"Measurement for mutated endpoint: {measured_endpoint}")

                # Collect measured endpoint for subsequent calculations
                measured_endpoints.append(measured_endpoint)

                # Send measurement feedback back into the mutator to change its behaviour
                self.mutator.feedback(measured_endpoint.measurement)

            # Calculate the coefficient of variation over all mutated versions of the original endpoint
            cv = coefficient_of_variation(
                [endpoint.measurement for endpoint in measured_endpoints]
            )
            Logger.trace(f"Coefficient of variation = {cv}. Endpoint: {endpoint}")

            # Compare coefficient of variation against threshold value
            if cv > 0.6:
                Logger.debug(f"Found vulnerable endpoint: {endpoint}")
                vulnerable_endpoints.append(endpoint)

        return vulnerable_endpoints

    def _measure_endpoint(self, endpoint: Endpoint) -> MeasuredEndpoint:
        measurement = measure_endpoint(
            endpoint=endpoint, count=10, algorithm="arithmetic"
        )
        return MeasuredEndpoint(endpoint.url, endpoint.http_method, measurement)
