from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable

import requests
from ratelimit import limits, sleep_and_retry
from requests.exceptions import Timeout

from dosscanner.model import Endpoint
from dosscanner.statistics import arithmetic_mean


@dataclass
class ResponseData:
    body: str
    url: str


class Requestor:

    headers: dict = {}
    certificate_validation: bool = True
    proxies: dict = {}

    queue: list[Endpoint] = []
    rate_limit: int = 100

    @staticmethod
    def enqueue(endpoint: Endpoint) -> None:
        """Adds endpoint to queue to wait for batched execution

        Args:
            endpoint (Endpoint): Endpoint which is added to queue
        """
        Requestor.queue.append(endpoint)

    @staticmethod
    def evaluate_response_data() -> list[ResponseData]:
        """Evaluates the current queue by iterating over all endpoints in it.
           Saves the response body and original url of it.

        Returns:
            list[ResponseData]: Results from evaluation of queue
        """

        @sleep_and_retry
        @limits(calls=Requestor.rate_limit, period=1)
        def get_response_data(url: str) -> ResponseData:
            """Sends http request and extracts information from response

            Args:
                url (str): Target url of web request

            Returns:
                ResponseData: Information about http response
            """
            print(url)
            try:
                resp = requests.get(
                    url,
                    headers=Requestor.headers,
                    timeout=30,
                    proxies=Requestor.proxies,
                    verify=Requestor.certificate_validation,
                )
            except Exception as exc:
                return ResponseData(body="", url="")

            return ResponseData(body=resp.text, url=resp.url)

        return Requestor._evaluate(get_response_data)

    @staticmethod
    def evaluate_response_time() -> list[int]:
        """Evaluates the current queue by iterating over all endpoints in it.
           Saves the response time in microseconds.

        Returns:
            list[int]: _description_
        """

        @sleep_and_retry
        @limits(calls=Requestor.rate_limit, period=1)
        def get_response_time(url: str) -> int:
            """Sends http request and extracts response time in microseconds

            Args:
                url (str): Target url of web request

            Returns:
                int: Response time in microseconds
            """
            try:
                resp = requests.get(
                    url,
                    headers=Requestor.headers,
                    timeout=60,
                    proxies=Requestor.proxies,
                    verify=Requestor.certificate_validation,
                )
            except Timeout:
                return 60 * 1_000_000
            except Exception as exc:
                return -1

            return resp.elapsed.microseconds

        def measure_endpoint(url: str) -> int:
            """Handles measurement of response time by averaging multiple measurements

            Args:
                url (str): Target url which is measured

            Returns:
                int: Averaged result of measurements
            """
            # Calculate arithmetic mean from multiple responses to get more accurate result
            return arithmetic_mean([get_response_time(url) for _ in range(5)])

        return Requestor._evaluate(measure_endpoint)

    @staticmethod
    def _evaluate(func: Callable) -> list:
        """Generic function to work through queue and call the specified
           function on each element.

        Args:
            func (Callable): Function which is executed for each queue element

        Returns:
            list: Results of function calls
        """
        # If the queue only consists of a small amount of items
        # Skip the overhead of creating a thread pool and just evaluate
        # them one by one
        if len(Requestor.queue) <= 3:
            results = [func(endpoint.url) for endpoint in Requestor.queue]
        else:
            # Evaluate all items from queue
            with ThreadPoolExecutor(max_workers=10) as executor:
                tasks = [endpoint.url for endpoint in Requestor.queue]
                results = list(executor.map(func, tasks))

        # Clear queue after processing it
        Requestor.queue.clear()

        return results
