from typing import Iterator

from dosscanner.model import Endpoint


class Mutator:
    def next(self, item: Endpoint) -> Iterator[tuple[Endpoint, bool]]:
        pass

    def feedback(self, endpoint: Endpoint, measurement: int):
        pass
