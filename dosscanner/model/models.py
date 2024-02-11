from dataclasses import dataclass


@dataclass
class EndpointItem:
    url: str
    http_method: str


@dataclass
class MeasuredEndpointItem(EndpointItem):
    measurement: float
