import requests

from dosscanner.model import Endpoint, MeasurementException
from dosscanner.statistics import (
    arithmetic_mean,
    geometric_mean,
    harmonic_mean,
    quadratic_mean,
)


def measure_endpoint(endpoint: Endpoint, count: int = 5, algorithm="arithmetic") -> int:
    """Measures the response time for a specific endpoint by sending multiple requests and calculating a mean response time values from them

    Args:
        endpoint (Endpoint): Endpoint object which is measured
        count (int, optional): Number of request which are made to calculate the mean value. Defaults to 5.
        algorithm (str, optional): Algorithm to use for mean value calculation. Either "arithmetic", "geometric", "harmonic" or "quadratic". Defaults to "arithmetic".

    Raises:
        NotImplementedError: If unknown algorithm is called

    Returns:
        int: Calculated mean response time
    """
    # The first response is always cut out, because the response time includes the resolving of python modules
    # This increases the delay of the first response and is thus excluded from the list
    response_times = [_get_response_time(endpoint) for _ in range(count + 1)][1:]

    if algorithm == "arithmetic":
        measurement = arithmetic_mean(response_times)
    elif algorithm == "geometric":
        measurement = geometric_mean(response_times)
    elif algorithm == "harmonic":
        measurement = harmonic_mean(response_times)
    elif algorithm == "quadratic":
        measurement = quadratic_mean(response_times)
    else:
        raise NotImplementedError(f"Algorithm {algorithm} not implemented!")

    return int(measurement)


def _get_response_time(endpoint: Endpoint) -> int | None:
    """Processes endpoint to get response time in microseconds

    Args:
        endpoint (Endpoint): Endpoint used for request

    Returns:
        int: Response time in microseconds
    """
    if endpoint.http_method == "GET":
        try:
            resp = requests.get(endpoint.url)
        except Exception:
            raise MeasurementException()
        return resp.elapsed.microseconds
