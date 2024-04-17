from typing import Iterator

from dosscanner.model import Endpoint


class Mutator:
    def next(self, item: Endpoint) -> Iterator[tuple[Endpoint, bool]]:
        """Uses the item and mutates it according to the specific Mutator implementation

        Args:
            item (Endpoint): Endpoint which is mutated

        Yields:
            Iterator[tuple[Endpoint, bool]]: All mutations generated
        """
        pass

    def feedback(self, endpoint: Endpoint, measurement: int):
        """Delivers feedback to the Mutator which can be used by the next(...) call
           to further improve mutation.

        Args:
            endpoint (Endpoint): Endpoint of which the feedback is given
            measurement (int): Feedback value representing the response time of the endpoint
        """
        pass
