"""
Punto de entrada del programa de simulación.

Inicia la simulación de eventos discretos del taller Happy Computing
con una jornada laboral de 8 horas (480 minutos).
"""

from simulation import Simulation


if __name__ == "__main__":
    simulation = Simulation(max_time=480)
    simulation.start()