import math
import random

"""
Random variable generators used in the simulation.
Only random.random() is used as the base generator.
"""

def exponential(mean : float) -> float:
    """
    Generate an exponential random variable using
    the inverse transform method.


    Args:
    mean (float): Mean value of the distribution.

    
    Returns:
    float: Exponential random variable.
    """
    u = random.random()
    return -mean * math.log(u)

def normal(mean : float, variance : float) -> float:
    """
    Generate a normal random variable using
    the Box-Muller method.
    Args:
    mean (float): Mean of the distribution.
    variance (float): Variance of the distribution.
    Returns:
    float: Normal random variable.
    """
    u1 = random.random()
    u2 = random.random()

    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    standard_desviation = math.sqrt(variance)
    return mean + standard_desviation * z

def poisson(_lambda):
    L = math.exp(-_lambda)

    k = 0
    p = 1

    while p > L:
        k += 1
        p *= random.random()
    
    return k

def generate_service_type():

    u = random.random()

    if u <= 0.45:
        return 1
    elif u <= 0.70:
        return 2
    elif u <= 0.80:
        return 3
    else:
        return 4