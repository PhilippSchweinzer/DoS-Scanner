import math

import requests

from dosscanner.model import EndpointItem


def measure_endpoint(
    endpoint: EndpointItem, count: int = 10, algorithm="arithmetic"
) -> float:
    """Measures the response time for a specific endpoint by sending multiple requests and calculating a mean response time values from them

    Args:
        endpoint (EndpointItem): Endpoint object which is measured
        count (int, optional): Number of request which are made to calculate the mean value. Defaults to 10.
        algorithm (str, optional): Algorithm to use for mean value calculation. Either "arithmetic", "geometric", "harmonic" or "quadratic". Defaults to "arithmetic".

    Raises:
        NotImplementedError: If unknown algorithm is called

    Returns:
        float: Calculated mean response time
    """
    # The first response is always cut out, because the response time includes the resolving of python modules
    # This increases the delay of the first response and is thus excluded from the list
    response_times = [_get_response_time(endpoint) for _ in range(count + 1)][1:]

    if algorithm == "arithmetic":
        return _arithmetic_mean(response_times)
    elif algorithm == "geometric":
        return _geometric_mean(response_times)
    elif algorithm == "harmonic":
        return _harmonic_mean(response_times)
    elif algorithm == "quadratic":
        return _quadratic_mean(response_times)
    else:
        raise NotImplementedError(f"Algorithm {algorithm} not implemented!")


def _arithmetic_mean(numbers: list) -> float:
    """Calculates arithmetic mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return sum(numbers) / len(numbers)


def _geometric_mean(numbers: list) -> float:
    """Calculates geometric mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return math.pow(math.prod(numbers), 1 / len(numbers))


def _harmonic_mean(numbers: list) -> float:
    """Calculates harmonic mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return len(numbers) / (sum([1 / n for n in numbers]))


def _quadratic_mean(numbers: list) -> float:
    """Calculates quadratic mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return math.sqrt((sum([n**2 for n in numbers]) / len(numbers)))


def _get_response_time(endpoint: EndpointItem) -> int:
    """Processes endpoint to get response time in microseconds

    Args:
        endpoint (EndpointItem): Endpoint used for request

    Returns:
        int: Response time in microseconds
    """
    if endpoint.http_method == "GET":
        resp = requests.get(endpoint.url)
        return resp.elapsed.microseconds


if __name__ == "__main__":
    print(
        measure_endpoint(EndpointItem(url="http://127.0.0.1:5000/", http_method="GET"))
    )
