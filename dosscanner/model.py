from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlparse


class MeasurementException(Exception):
    pass


@dataclass
class Endpoint:
    url: str
    http_method: str

    def __repr__(self) -> str:
        return self.http_method + " " + self.url

    def get_url_params(self) -> dict:
        url_parts = urlparse(self.url)
        return dict(parse_qsl(url_parts.query))

    def set_url_params(self, params: dict) -> None:
        url_parts = urlparse(self.url)
        self.url = url_parts._replace(query=urlencode(params)).geturl()


@dataclass
class MeasuredEndpoint(Endpoint):
    measurement: int

    def __repr__(self) -> str:
        return (f"Response time: {self.measurement}μs ") + super().__repr__()


@dataclass
class GeneticEndpoint(MeasuredEndpoint):
    parent: "GeneticEndpoint"
