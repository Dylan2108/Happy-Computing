"""
Módulo de generación de variables aleatorias para la simulación.

Implementa generadores para las distribuciones de probabilidad
especificadas en el problema:
- Exponencial (tiempos de servicio)
- Normal (tiempo del vendedor)
- Poisson (llegadas de clientes)
- Discreta (tipo de servicio)

Utiliza métodos exactos: transformada inversa, Box-Muller y Knuth.
"""

import math
import random


def exponential(mean: float) -> float:
    """
    Genera una variable aleatoria con distribución exponencial.

    Utiliza el método de la transformada inversa:
    X = -mean * ln(U), donde U ~ U(0,1)

    Args:
        mean (float): Valor medio de la distribución exponencial.
                     Equivale a 1/λ.

    Returns:
        float: Variable aleatoria exponencial.
    """
    u = random.random()
    return -mean * math.log(u)


def normal(mean: float, variance: float) -> float:
    """
    Genera una variable aleatoria con distribución normal.

    Utiliza el método de Box-Muller para convertir dos variables
    uniformes en una distribución normal estándar, luego la
    transforma a la distribución deseada.

    Args:
        mean (float): Media de la distribución normal (μ).
        variance (float): Varianza de la distribución normal (σ²).

    Returns:
        float: Variable aleatoria normal con la media y varianza especificadas.
    """
    u1 = random.random()
    u2 = random.random()

    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    standard_deviation = math.sqrt(variance)
    return mean + standard_deviation * z


def poisson(_lambda: int) -> int:
    """
    Genera una variable aleatoria con distribución de Poisson.

    Utiliza el método de inversión secuencial de Knuth.
    Genera el número de eventos en un intervalo dado.

    Args:
        _lambda (int): Parámetro λ de la distribución de Poisson.
                       Representa el número promedio de eventos.

    Returns:
        int: Número de eventos generados según Poisson(λ).
    """
    L = math.exp(-_lambda)

    k = 0
    p = 1

    while p > L:
        k += 1
        p *= random.random()
    
    return k


def generate_service_type() -> int:
    """
    Genera el tipo de servicio que solicita un cliente.

    Utiliza el método de la transformada inversa discreta.
    Distribución basada en las probabilidades del problema:
    - Tipo 1: 45% (reparación con garantía)
    - Tipo 2: 25% (reparación sin garantía)
    - Tipo 3: 10% (cambio de equipo)
    - Tipo 4: 20% (venta de equipo)

    Returns:
        int: Tipo de servicio (1-4).
    """
    u = random.random()

    if u <= 0.45:
        return 1
    elif u <= 0.70:
        return 2
    elif u <= 0.80:
        return 3
    else:
        return 4


def arrival_time() -> int:
    """
    Genera el tiempo entre llegadas consecutivas de clientes.

    Utiliza una distribución de Poisson con λ = 20 minutos.
    Los clientes arrivan con intervalo
    promedio de 20 minutos.

    Returns:
        int: Minutos hasta la próxima llegada del cliente.
    """
    return poisson(20)


def seller_service_time() -> float:
    """
    Genera el tiempo de atención de un vendedor.

    Utiliza una distribución normal con media 5 minutos
    y varianza 2 minutos
    Se usa valor absoluto para evitar tiempos negativos.

    Returns:
        float: Tiempo de atención del vendedor en minutos.
    """
    service_time = normal(5, 2)
    return abs(service_time)


def repair_time() -> float:
    """
    Genera el tiempo de reparación de un técnico.

    Utiliza una distribución exponencial con media 20 minutos.

    Returns:
        float: Tiempo de reparación en minutos.
    """
    return exponential(20)


def equipment_change_time() -> float:
    """
    Genera el tiempo de cambio de equipo por técnico especializado.

    Utiliza una distribución exponencial con media 15 minutos.

    Returns:
        float: Tiempo de cambio de equipo en minutos.
    """
    return exponential(15)