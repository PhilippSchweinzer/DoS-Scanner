import random
import string
from collections.abc import Iterator
from copy import deepcopy

from typing_extensions import override

from dosscanner.model import Endpoint, GeneticEndpoint
from dosscanner.mutation.mutator import Mutator


class GeneticMutator(Mutator):

    def __init__(self, population_size: int, max_evolutions: int):
        self.population_size = population_size
        self.max_evolutions = max_evolutions
        self.feedback_data = []

    @override
    def next(self, item: Endpoint) -> Iterator[tuple[Endpoint, bool]]:
        """Uses the item and mutates it using a genetic algorithm.

        Args:
            item (Endpoint): Endpoint which is mutated

        Yields:
            Iterator[tuple[Endpoint, bool]]: All mutations generated
        """
        for param in item.get_url_params():
            # Reset feedback data
            self.feedback_data.clear()

            # Yield the original item to measure it and create a baseline reading
            yield item, True
            initial_measurement = self.feedback_data[0].measurement

            # Create initial population
            population = [
                GeneticEndpoint(
                    url=item.url,
                    http_method=item.http_method,
                    measurement=None,
                    mutated_param_key=param,
                )
            ] * self.population_size

            # Iterate over all evolutions
            for _ in range(self.max_evolutions):
                # Reset feedback data
                self.feedback_data.clear()

                # Create a deepcopy of the population to initiate a new step
                population = [deepcopy(pop) for pop in population]

                # Mutate population
                for pop in population:
                    if random.random() < 0.3:
                        self._mutate(pop)

                # Evaluate fitness
                for pop in population[:-1]:
                    yield pop, False
                yield population[-1], True

                # Select viable parent from population
                parent_population = self._select_parents(
                    self.feedback_data, initial_measurement
                )

                # Execute crossover to fill population with ancestors from
                # the viable parents
                population = self._crossover(parent_population)

    @override
    def feedback(self, endpoint: GeneticEndpoint, measurement: int):
        """Delivers feedback to the Mutator which can be used by the next(...) call to
           further improve mutation.

        Args:
            endpoint (GeneticEndpoint): GeneticEndpoint of which the feedback is given
            measurement (int): Feedback value representing the response time of the endpoint
        """
        endpoint.measurement = measurement
        self.feedback_data.append(endpoint)

    # One point crossover
    def _crossover(
        self, parent_population: list[GeneticEndpoint]
    ) -> list[GeneticEndpoint]:
        """Represents the crossover phase in the genetic algorithm.
           Takes a list of parents and fills the population by crossing their properties to
           create offspring until the population has reached its maximum.

        Args:
            parent_population (list[GeneticEndpoint]): Parents from which offspring is created

        Returns:
            list[GeneticEndpoint]: New generation of population
        """
        population = parent_population.copy()

        while len(population) != self.population_size:
            # Choose two parents
            parent1, parent2 = random.sample(parent_population, k=2)
            param1 = parent1.get_mutated_param_value()
            param2 = parent2.get_mutated_param_value()
            min_len = min(len(param1), len(param2))
            crossover_point = random.randint(0, min_len)
            offspring = GeneticEndpoint(
                url=parent1.url,
                http_method=parent1.http_method,
                measurement=None,
                mutated_param_key=parent1.mutated_param_key,
            )
            crossover_value = param1[:crossover_point] + param2[crossover_point:]
            offspring.set_mutated_param_value(crossover_value)
            population.append(offspring)

        return population

    def _select_parents(
        self, population: list[GeneticEndpoint], initial_measurement: int
    ) -> list[GeneticEndpoint]:
        """Represents the natural selection phase in the genetic algorithm.
           Select viable parents from the population using a biased randomness to
           favor endpoints with the greatest improvement in response time with respect
           to its original ancestor.

        Args:
            population (list[GeneticEndpoint]): Population of the current evolution stage

        Returns:
            list[GeneticEndpoint]: Selected parents viable for further evolution
        """
        # Sort by greatest improvement in response time compared to the parent
        sorted_by_measurement_diff = sorted(
            population, key=lambda e: e.measurement - initial_measurement, reverse=True
        )

        # Calculate the bias weights for randomly choosing from the list
        weights = [1 / (i + 0.5) for i in range(self.population_size)]
        # Using biased randomness favoring parents with greater time improvement to choose a new population
        parents = random.choices(
            sorted_by_measurement_diff, weights, k=self.population_size // 2
        )
        return parents

    def _mutate(self, endpoint: GeneticEndpoint) -> GeneticEndpoint:
        """Represents the mutation phase in the genetic algorithm
           Mutate the endpoint by changing its properties

        Args:
            endpoint (GeneticEndpoint): Endpoint from which the mutation is generated

        Returns:
            GeneticEndpoint: Mutated endpoint
        """
        mutations = [
            Mutations.add_digit,
            Mutations.negate,
            Mutations.add_lowercase_character,
            Mutations.add_uppercase_character,
            Mutations.add_special_character,
            Mutations.add_copy,
            Mutations.remove_last_character,
            Mutations.remove_first_character,
            Mutations.add_non_printable_character,
        ]
        params = endpoint.get_url_params()
        params[endpoint.mutated_param_key] = random.choice(mutations)(
            params[endpoint.mutated_param_key]
        )
        endpoint.set_url_params(params)

        return endpoint


class Mutations:

    @staticmethod
    def add_digit(param: str):
        return param + str(random.randint(0, 9))

    @staticmethod
    def negate(param: str) -> str:
        return "-" + param

    @staticmethod
    def add_lowercase_character(param: str) -> str:
        return param + random.choice(string.ascii_lowercase)

    @staticmethod
    def add_uppercase_character(param: str) -> str:
        return param + random.choice(string.ascii_uppercase)

    @staticmethod
    def add_special_character(param: str) -> str:
        return param + random.choice(".,:;-+_#*~?!/\\<>&'\"%=@")

    @staticmethod
    def add_non_printable_character(param: str) -> str:
        return param + chr(random.randint(0, 32))

    @staticmethod
    def add_copy(param: str) -> str:
        return param + param

    @staticmethod
    def remove_last_character(param: str) -> str:
        if len(param) > 1:
            return param[:-1]
        return param

    @staticmethod
    def remove_first_character(param: str) -> str:
        if len(param) > 1:
            return param[1:]
        return param
