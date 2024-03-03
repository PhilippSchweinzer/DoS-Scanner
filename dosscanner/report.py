import json

from dosscanner.model import Endpoint, MeasuredEndpoint


def create_report(
    vulnerable_endpoints: MeasuredEndpoint, all_endpoints: Endpoint
) -> str:
    report = {"vulnerable": []}
    for endpoint in vulnerable_endpoints:
        report["vulnerable"].append(
            {
                "http_method": endpoint.http_method,
                "url": endpoint.url,
                "response_time": "%.1f" % endpoint.measurement,
            }
        )

    report["endpoints"] = []
    for endpoint in all_endpoints:
        report["endpoints"].append(
            {"http_method": endpoint.http_method, "url": endpoint.url}
        )

    return json.dumps(report, indent=4)
