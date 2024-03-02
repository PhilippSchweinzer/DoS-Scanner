import math

import numpy as np


def coefficient_of_variation(numbers: list) -> float:
    """Calculates the coefficient of variation from a list of numbers.
    It serves as a standardized measure of dispersion.

    Args:
        numbers (list): List from which the coefficient of variation is calculated

    Returns:
        float: Calculated coefficient of variation
    """
    if len(numbers) == 0:
        return 0
    return standard_deviation(numbers) / arithmetic_mean(numbers)


def standard_deviation(numbers: list) -> float:
    """Calculates the standard deviation from a list of numbers

    Args:
        numbers (list): List from which the standard deviation is calculated

    Returns:
        float: Calculated standard deviation
    """
    return np.std(numbers)


def arithmetic_mean(numbers: list) -> float:
    """Calculates arithmetic mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return sum(numbers) / len(numbers)


def geometric_mean(numbers: list) -> float:
    """Calculates geometric mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return math.pow(math.prod(numbers), 1 / len(numbers))


def harmonic_mean(numbers: list) -> float:
    """Calculates harmonic mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return len(numbers) / (sum([1 / n for n in numbers]))


def quadratic_mean(numbers: list) -> float:
    """Calculates quadratic mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return math.sqrt((sum([n**2 for n in numbers]) / len(numbers)))
