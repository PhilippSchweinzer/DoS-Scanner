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
        return super().__repr__() + ("%.2f" % self.measurement)
