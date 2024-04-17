from urllib.parse import urlparse

from dosscanner.crawl import EndpointCrawler
from dosscanner.logger import Logger
from dosscanner.model import Endpoint, MeasuredEndpoint
from dosscanner.mutation.mutator import Mutator
from dosscanner.request import Requestor
from dosscanner.statistics import coefficient_of_variation


class DoSScanner:
    def __init__(self, target: str, mutator: Mutator) -> None:
        self.target = target
        self.mutator = mutator

    def scan_target(self) -> tuple[list[MeasuredEndpoint], list[Endpoint]]:

        # Get a list of endpoints by crawling the target
        Logger.info("Crawler started")
        crawler = EndpointCrawler(
            start_urls=[Endpoint(url=self.target, http_method="GET")],
            allowed_domains=[urlparse(self.target).netloc],
        )
        endpoints = crawler.crawl()

        Logger.debug(
            f"{len(endpoints)} unique endpoints were found by the crawler: {endpoints}"
        )

        # Filter only endpoints with parameters
        endpoints_with_params = [
            endpoint for endpoint in endpoints if len(endpoint.get_url_params()) > 0
        ]

        Logger.info("Mutating endpoints and evaluating DoS score...")
        vulnerable_endpoints = []
        # Iterate over all endpoints to evaluate them
        for endpoint in endpoints_with_params:
            measured_endpoints = []
            # Mutate the endpoint until the generating mutator is empty
            for mutated_endpoint, batch_end in self.mutator.next(endpoint):

                # Add mutation to requests queue
                Requestor.enqueue(mutated_endpoint)

                # If the current batch has ended, measure all collected endpoints and
                # send feedback to the mutator
                if batch_end:
                    batch = Requestor.queue.copy()
                    measurements = Requestor.evaluate_response_time()
                    for endpoint, measurement in zip(batch, measurements):
                        self.mutator.feedback(endpoint, measurement)
                        measured_endpoints.append(
                            MeasuredEndpoint(
                                url=endpoint.url,
                                http_method=endpoint.http_method,
                                measurement=measurement,
                            )
                        )

            # Calculate the coefficient of variation over all mutated versions of the original endpoint
            cv = coefficient_of_variation(
                [endpoint.measurement for endpoint in measured_endpoints]
            )
            Logger.trace(f"Coefficient of variation = {cv}. Endpoint: {endpoint}")

            # Compare coefficient of variation against threshold value
            if cv > 0.6:
                # Find mutation with greatest response time
                max = measured_endpoints[0]
                for measured_endpoint in measured_endpoints:
                    if measured_endpoint.measurement > max.measurement:
                        max = measured_endpoint
                Logger.debug(f"Found vulnerable endpoint: {max}")
                vulnerable_endpoints.append(max)

        return vulnerable_endpoints, endpoints
