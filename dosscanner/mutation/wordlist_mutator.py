from collections.abc import Iterator
from urllib.parse import parse_qsl, urlencode, urlparse

from typing_extensions import override

from dosscanner.model import Endpoint
from dosscanner.mutation.mutator import Mutator


class WordlistMutator(Mutator):
    def __init__(self, wordlist_path: str, param_list_path: str) -> None:
        self.wordlist_path = wordlist_path
        self.param_list_path = param_list_path
        self.batch_size = 100

    @override
    def next(self, item: Endpoint) -> Iterator[tuple[Endpoint, bool]]:
        """Uses the item and mutates it by changing the parameter values according
           to the specified wordlist

        Args:
            item (Endpoint): Endpoint which is mutated

        Yields:
            Iterator[tuple[Endpoint, bool]]: All mutations generated
        """

        # Counter to track how many elements were yielded
        yield_counter = 0

        # Yield the original item to measure it and create a baseline reading
        yield item, False
        yield_counter += 1

        # Read values from both wordlists
        with open(self.wordlist_path, "r") as f:
            wordlist = [line.strip() for line in f.readlines()]
        with open(self.param_list_path, "r") as f:
            param_list = [line.strip() for line in f.readlines()]

        wordlist_length = len(wordlist)

        # Parse paremters from URL
        url_params = item.get_url_params()

        # Iterate over all parameters and check if they should be tested
        for param in url_params:
            if param in param_list:
                # Yield Endpoint object for every value which should be tested
                for idx, word in enumerate(wordlist):
                    new_url_params = url_params.copy()
                    new_url_params[param] = word
                    mutated_endpoint = Endpoint(
                        url=item.url, http_method=item.http_method
                    )
                    mutated_endpoint.set_url_params(new_url_params)
                    yield_counter += 1
                    # End batch at maximum size or last element to process all endpoints in batches
                    if yield_counter == 200 or idx == wordlist_length - 1:
                        batch_end = True
                        yield_counter = 0
                    else:
                        batch_end = False
                    yield mutated_endpoint, batch_end

    @override
    def feedback(self, endpoint: Endpoint, measurement: int):
        """This mutator does not need feedback values.
           Does nothing and calls super implementation.

        Args:
            endpoint (Endpoint): Endpoint of which the feedback is given
            measurement (int): Feedback value representing the response time of the endpoint
        """
        return super().feedback(endpoint, measurement)
