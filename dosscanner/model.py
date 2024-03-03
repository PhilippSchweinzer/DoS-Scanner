from dataclasses import dataclass


@dataclass
class Endpoint:
    url: str
    http_method: str

    def __repr__(self) -> str:
        return self.http_method + " " + self.url


@dataclass
class MeasuredEndpoint(Endpoint):
    measurement: float

    def __repr__(self) -> str:
        return ("Response time: %.1fμs " % self.measurement) + super().__repr__()
