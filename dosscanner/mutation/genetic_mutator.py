import copy
import random
import string
from collections.abc import Iterator

from typing_extensions import override

from dosscanner.model import Endpoint, GeneticEndpoint
from dosscanner.mutation.mutator import Mutator


class GeneticMutator(Mutator):

    def __init__(self, population_size: int = 10, max_evolutions: int = 10):
        self.population_size = population_size
        self.max_evolutions = max_evolutions
        self.feedback_data = []

    @override
    def next(self, item: Endpoint) -> Iterator[tuple[Endpoint, bool]]:
        # Reset feedback data
        self.feedback_data.clear()

        # Yield the original item to measure it and create a baseline reading
        yield item, True

        # Create initial population
        population = []
        initial_measurement = self.feedback_data[0].measurement
        for _ in range(self.population_size):
            population.append(
                GeneticEndpoint(
                    url=item.url,
                    http_method=item.http_method,
                    measurement=initial_measurement,
                    parent=None,
                )
            )

        # Iterate over all evolutions
        for _ in range(self.max_evolutions):
            # Reset feedback data
            self.feedback_data.clear()

            # Mutate population
            for pop in population[:-1]:
                yield self._mutate(pop), False
            yield self._mutate(population[-1]), True

            # Evaluate fitness
            # This step is done in the scanner implementation

            # Create new generation by selecting viable parents
            population = self._select_parents(self.feedback_data)

    @override
    def feedback(self, endpoint: GeneticEndpoint, measurement: int):
        endpoint.measurement = measurement
        self.feedback_data.append(endpoint)

    def _select_parents(
        self, population: list[GeneticEndpoint]
    ) -> list[GeneticEndpoint]:
        """Select viable parents from the population

        Args:
            population (list[GeneticEndpoint]): Population of the current evolution stage

        Returns:
            list[GeneticEndpoint]: Selected parents viable for further evolution
        """
        # Sort by greatest improvement in response time compared to the parent
        sorted_by_measurement_diff = sorted(
            population, key=lambda e: e.measurement - e.parent.measurement, reverse=True
        )

        # Calculate the bias weights for randomly choosing from the list
        weights = [1 / (i + 0.5) for i in range(self.population_size)]
        # Using biased randomness favoring parents with greater time improvement to choose a new population
        parents = random.choices(
            sorted_by_measurement_diff, weights, k=self.population_size
        )
        return parents

    def _mutate(self, endpoint: GeneticEndpoint) -> GeneticEndpoint:
        """Mutate the endpoint by chaning properties of its parameters

        Args:
            endpoint (GeneticEndpoint): Endpoint from which the mutation is generated

        Returns:
            GeneticEndpoint: Mutated endpoint
        """
        params = endpoint.get_url_params()

        if len(params) == 0:
            return endpoint

        chosen_param = random.choice(list(params.keys()))

        mutations = [
            Mutations.add_digit,
            Mutations.add_lowercase_character,
            Mutations.add_uppercase_character,
            Mutations.add_special_character,
        ]
        params[chosen_param] = random.choice(mutations)(params[chosen_param])

        mutated_endpoint = GeneticEndpoint(
            url=endpoint.url,
            http_method=endpoint.http_method,
            measurement=None,
            parent=endpoint,
        )
        mutated_endpoint.set_url_params(params)
        return mutated_endpoint


class Mutations:

    @staticmethod
    def add_digit(param: str):
        return param + str(random.randint(0, 9))

    @staticmethod
    def add_lowercase_character(param: str):
        return param + random.choice(string.ascii_lowercase)

    @staticmethod
    def add_uppercase_character(param: str):
        return param + random.choice(string.ascii_uppercase)

    @staticmethod
    def add_special_character(param: str):
        return param + random.choice(".,:;-+_#*~?!/\\<>")
