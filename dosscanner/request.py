from concurrent.futures import ThreadPoolExecutor

import requests
from ratelimit import limits, sleep_and_retry
from requests.exceptions import Timeout

from dosscanner.model import Endpoint
from dosscanner.statistics import arithmetic_mean


class Requestor:

    queue: list[Endpoint] = []
    rate_limit: int = 100

    @staticmethod
    def enqueue(endpoint: Endpoint) -> None:
        Requestor.queue.append(endpoint)

    @staticmethod
    def evaluate() -> list[int]:

        @sleep_and_retry
        @limits(calls=Requestor.rate_limit, period=1)
        def get_response_time(url: str) -> int:
            try:
                resp = requests.get(url, timeout=60)
            except Timeout:
                return 60 * 1_000_000
            except Exception:
                return -1

            return resp.elapsed.microseconds

        def measure_endpoint(endpoint: Endpoint) -> int:
            # Calculate arithmetic mean from multiple responses to get more accurate result
            return arithmetic_mean([get_response_time(endpoint.url) for _ in range(5)])

        # If the queue only consists of a small amount of items
        # Skip the overhead of creating a thread pool and just evaluate
        # them one by one
        if len(Requestor.queue) <= 3:
            results = [measure_endpoint(endpoint) for endpoint in Requestor.queue]
        else:
            # Evaluate all items from queue
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(measure_endpoint, Requestor.queue))

        # Clear queue after processing it
        Requestor.queue.clear()

        return results
