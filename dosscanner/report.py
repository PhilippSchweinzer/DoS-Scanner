import json

from dosscanner.model import Endpoint, MeasuredEndpoint


def create_report(
    vulnerable_endpoints: MeasuredEndpoint, all_endpoints: Endpoint
) -> str:
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
