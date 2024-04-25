from urllib.parse import urlparse

from dosscanner import crawl
from dosscanner.crawl import EndpointCrawler
from dosscanner.logger import Logger
from dosscanner.model import Endpoint, MeasuredEndpoint
from dosscanner.mutation.mutator import Mutator
from dosscanner.request import Requestor
from dosscanner.statistics import coefficient_of_variation


class DoSScanner:
    def __init__(
        self,
        target: str,
        mutator: Mutator,
        crawler: EndpointCrawler,
        endpoint_list: list[str],
    ) -> None:
        self.target = target
        self.mutator = mutator
        self.crawler = crawler
        self.endpoint_list = endpoint_list

    def scan_target(self) -> tuple[list[MeasuredEndpoint], list[Endpoint]]:
        """Scans target for denial of service vulnerabilities

        Returns:
            tuple[list[MeasuredEndpoint], list[Endpoint]]: Result of scan
        """

        # Check which way endpoints are provided and read them
        if self.crawler is not None:
            Logger.info("Crawler started")
            endpoints = self.crawler.crawl()
        else:
            Logger.info("Endpoints read from supplied file")
            endpoints = [
                Endpoint(url=endpoint, http_method="GET")
                for endpoint in self.endpoint_list
            ]
        Logger.debug(f"{len(endpoints)} unique endpoints were found by the crawler")
        Logger.trace(f"All endpoints: {endpoints}")

        # Filter only endpoints with parameters
        endpoints_with_params = [
            endpoint for endpoint in endpoints if len(endpoint.get_url_params()) > 0
        ]

        Logger.info("Mutating endpoints and evaluating DoS score...")
        vulnerable_endpoints = []
        # Iterate over all endpoints to evaluate them
        for endpoint in endpoints_with_params:
            Logger.debug(f"Mutating endpoint {endpoint}")
            measured_endpoints = []
            # Mutate the endpoint until the generating mutator is empty
            for mutated_endpoint, batch_end in self.mutator.next(endpoint):

                Logger.trace(f"Generated mutation: {mutated_endpoint}")

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
            Logger.trace(
                f'Coefficient of variation of endpoint "{endpoint}" was calculated to {cv}'
            )

            # Compare coefficient of variation against threshold value
            if cv > 0.6:
                # Find mutation with greatest response time
                max = measured_endpoints[0]
                for measured_endpoint in measured_endpoints:
                    if measured_endpoint.measurement > max.measurement:
                        max = measured_endpoint
                Logger.info(f"Found vulnerable endpoint: {max}")
                vulnerable_endpoints.append(max)

        return vulnerable_endpoints, endpoints
