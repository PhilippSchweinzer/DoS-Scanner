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
    return float(np.std(numbers))


def arithmetic_mean(numbers: list) -> int:
    """Calculates arithmetic mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return int(np.mean(numbers))


def geometric_mean(numbers: list) -> int:
    """Calculates geometric mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return int(math.pow(math.prod(numbers), 1 / len(numbers)))


def harmonic_mean(numbers: list) -> int:
    """Calculates harmonic mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return int(len(numbers) / (sum([1 / n for n in numbers])))


def quadratic_mean(numbers: list) -> int:
    """Calculates quadratic mean from list of numbers

    Args:
        numbers (list): List from which mean is calculated

    Returns:
        float: Calculated mean value
    """
    return int(math.sqrt((sum([n**2 for n in numbers]) / len(numbers))))


def median(numbers: list) -> int:
    """Calculates median from list of numbers

    Args:
        numbers (list): List from which median is calculated

    Returns:
        int: Calculated median value
    """
    return np.median(numbers)
