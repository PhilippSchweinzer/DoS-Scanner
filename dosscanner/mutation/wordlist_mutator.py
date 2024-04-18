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

        # Parse paremters from URL
        url_parts = urlparse(item.url)
        query = dict(parse_qsl(url_parts.query))

        # Iterate over all parameters and check if they should be tested
        for param in query.keys():
            if param in param_list:
                # Yield Endpoint object for every value which should be tested
                for word in wordlist:
                    new_query = query.copy()
                    new_query[param] = word
                    new_url = url_parts._replace(query=urlencode(new_query)).geturl()
                    yield_counter += 1
                    # End batch at maximum size to process all endpoints in batches
                    if yield_counter == 200:
                        batch_end = True
                        yield_counter = 0
                    else:
                        batch_end = False
                    yield Endpoint(url=new_url, http_method=item.http_method), batch_end

    @override
    def feedback(self, endpoint: Endpoint, measurement: int):
        """This mutator does not need feedback values.
           Does nothing and calls super implementation.

        Args:
            endpoint (Endpoint): Endpoint of which the feedback is given
            measurement (int): Feedback value representing the response time of the endpoint
        """
        return super().feedback(endpoint, measurement)
