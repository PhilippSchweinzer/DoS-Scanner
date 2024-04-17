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

    def get_url_params(self) -> dict[str, str]:
        """Parses the url and retrieves all url parameters in it

        Returns:
            dict[str, str]: Parsed url parameters
        """
        url_parts = urlparse(self.url)
        return dict(parse_qsl(url_parts.query))

    def set_url_params(self, params: dict[str, str]) -> None:
        """Sets parameters of the current url to the given values

        Args:
            params (dict[str, str]): Parameter keys/values which are set on the url
        """
        url_parts = urlparse(self.url)
        self.url = url_parts._replace(query=urlencode(params)).geturl()


@dataclass
class MeasuredEndpoint(Endpoint):
    measurement: int

    def __repr__(self) -> str:
        return (f"Response time: {self.measurement}μs ") + super().__repr__()


@dataclass
class GeneticEndpoint(MeasuredEndpoint):
    mutated_param_key: str  # Tracks the url parameter key which is mutated

    def get_mutated_param_value(self) -> str:
        """Retrieves value of the parameter which is currently being mutated

        Returns:
            str: Value of mutated parameter
        """
        return self.get_url_params()[self.mutated_param_key]

    def set_mutated_param_value(self, value: str) -> None:
        """Sets value of the parameter which is currently being mutated

        Args:
            value (str): Value to which the parameter is set
        """
        params = self.get_url_params()
        params[self.mutated_param_key] = value
        self.set_url_params(params)
