from dosscanner.model import Endpoint


class Mutator:
    def next(self, item: Endpoint) -> Endpoint:
        pass

    def feedback(self, endpoint: Endpoint, measurement: int):
        pass
