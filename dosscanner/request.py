from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable

import requests
from ratelimit import limits, sleep_and_retry
from requests.exceptions import Timeout

from dosscanner.model import Endpoint
from dosscanner.statistics import arithmetic_mean


class Requestor:

    headers: dict = {}
    certificate_validation: bool = True
    proxies: dict = {}

    queue: list[Endpoint] = []
    rate_limit: int = 100

    @staticmethod
    def enqueue(endpoint: Endpoint) -> None:
        Requestor.queue.append(endpoint)

    @staticmethod
    def evaluate_response_body() -> list["ResponseData"]:

        @sleep_and_retry
        @limits(calls=Requestor.rate_limit, period=1)
        def get_response_body(url: str) -> str:
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

        return Requestor._evaluate(get_response_body)

    @staticmethod
    def evaluate_response_time() -> list[int]:

        @sleep_and_retry
        @limits(calls=Requestor.rate_limit, period=1)
        def get_response_time(url: str) -> int:
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
            # Calculate arithmetic mean from multiple responses to get more accurate result
            return arithmetic_mean([get_response_time(url) for _ in range(5)])

        return Requestor._evaluate(measure_endpoint)

    @staticmethod
    def _evaluate(func: Callable) -> list:
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


@dataclass
class ResponseData:
    body: str
    url: str
