import json

from dosscanner.model import Endpoint, MeasuredEndpoint


def create_report(
    vulnerable_endpoints: list[MeasuredEndpoint], all_endpoints: list[Endpoint]
) -> str:
    """Creates a json report of the findings in string form.

    Args:
        vulnerable_endpoints (list[MeasuredEndpoint]): All vulnerable endpoints which were found
        all_endpoints (list[Endpoint]): All endpoints which were found

    Returns:
        str: String representation of the resulting report
    """
    report = {"vulnerable_endpoints": []}
    for endpoint in vulnerable_endpoints:
        report["vulnerable_endpoints"].append(
            {
                "http_method": endpoint.http_method,
                "url": endpoint.url,
                "response_time": endpoint.measurement,
            }
        )

    report["crawled_endpoints"] = []
    for endpoint in all_endpoints:
        report["crawled_endpoints"].append(
            {"http_method": endpoint.http_method, "url": endpoint.url}
        )

    return json.dumps(report, indent=4)
