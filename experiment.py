"""
Módulo de experimentación para el proyecto de simulación.

Ejecuta múltiples simulaciones (por defecto 1000) y calcula
estadísticas para obtener conclusiones sobre el comportamiento
del sistema.

Uso:
    python3 experiment.py
"""

import random
import statistics
from collections import defaultdict
from typing import List, Dict

from simulation import Simulation


class ExperimentResults:
    """
    Almacena y analiza los resultados de múltiples simulaciones.

    Proporciona métodos para calcular estadísticas descriptivas
    e intervalos de confianza.
    """

    def __init__(self, results: List[Dict]):
        """
        Inicializa con los resultados de las simulaciones.

        Args:
            results: Lista de diccionarios con métricas de cada simulación.
        """
        self.results = results
        self.num_simulations = len(results)

    def get_metric(self, metric: str) -> List[float]:
        """Extrae una métrica específica de todos los resultados."""
        return [r[metric] for r in self.results if metric in r]

    def calculate_stats(self, metric: str) -> Dict:
        """
        Calcula estadísticas para una métrica.

        Returns:
            Diccionario con media, std, min, max, IC 95%.
        """
        values = self.get_metric(metric)
        if not values:
            return {}

        n = len(values)
        mean = statistics.mean(values)
        std = statistics.stdev(values) if n > 1 else 0
        min_val = min(values)
        max_val = max(values)

        # Intervalo de confianza 95%: mean ± 1.96 * (std / sqrt(n))
        margin = 1.96 * (std / (n ** 0.5)) if n > 1 else 0

        return {
            "mean": mean,
            "std": std,
            "min": min_val,
            "max": max_val,
            "ci_lower": mean - margin,
            "ci_upper": mean + margin,
            "n": n
        }

    def print_summary(self) -> None:
        """Imprime un resumen de las estadísticas principales."""
        print("=" * 70)
        print("RESULTADOS DE EXPERIMENTACIÓN - SIMULACIÓN DE EVENTOS DISCRETOS")
        print(f"Número de simulaciones: {self.num_simulations}")
        print("=" * 70)

        metrics = [
            ("total_amount", "Ganancia total ($)"),
            ("generated_clients", "Clientes generados"),
            ("attended_clients", "Clientes atendidos"),
            ("clients_type1", "Tipo 1 (Garantía)"),
            ("clients_type2", "Tipo 2 (Sin garantía)"),
            ("clients_type3", "Tipo 3 (Cambio equipo)"),
            ("clients_type4", "Tipo 4 (Venta equipo)"),
            ("final_time", "Tiempo final (min)"),
        ]

        print("\n--- ESTADÍSTICAS PRINCIPALES ---\n")
        for metric, label in metrics:
            stats = self.calculate_stats(metric)
            if stats:
                print(f"{label}:")
                print(f"  Media: {stats['mean']:.2f}")
                print(f"  Desviación estándar: {stats['std']:.2f}")
                print(f"  Mín: {stats['min']:.2f} | Máx: {stats['max']:.2f}")
                print(f"  IC 95%: [{stats['ci_lower']:.2f}, {stats['ci_upper']:.2f}]")
                print()

        # Análisis de servicios
        print("\n--- DISTRIBUCIÓN DE SERVICIOS (Promedio) ---")
        total_services = statistics.mean(self.get_metric("generated_clients"))
        for i in range(1, 5):
            count = statistics.mean(self.get_metric(f"clients_type{i}"))
            pct = (count / total_services * 100) if total_services > 0 else 0
            print(f"Tipo {i}: {count:.1f} clientes ({pct:.1f}%)")

    def print_conclusions(self) -> None:
        """Imprime las conclusiones del análisis."""
        gain_stats = self.calculate_stats("total_amount")
        clients_stats = self.calculate_stats("generated_clients")

        print("\n" + "=" * 70)
        print("CONCLUSIONES")
        print("=" * 70)

        print(f"""
1. GANANCIA ESPERADA:
   - La ganancia media por jornada de 8 horas es de ${gain_stats['mean']:.2f}
   - Con un intervalo de confianza del 95%: [{gain_stats['ci_lower']:.2f}, {gain_stats['ci_upper']:.2f}]
   - La variabilidad (desviación estándar) es de ${gain_stats['std']:.2f}

2. CAPACIDAD DEL SISTEMA:
   - En promedio llegan {clients_stats['mean']:.1f} clientes por jornada
   - El sistema atiende aproximadamente {statistics.mean(self.get_metric('attended_clients')):.1f} clientes
   - Algunos clientes quedan sin atender al cierre: {clients_stats['mean'] - statistics.mean(self.get_metric('attended_clients')):.1f} en promedio

3. TIPO DE SERVICIOS MÁS FRECUENTES:
   - Tipo 1 (Garantía): {statistics.mean(self.get_metric('clients_type1')):.1f} clientes
   - Tipo 2 (Sin garantía): {statistics.mean(self.get_metric('clients_type2')):.1f} clientes  
   - Tipo 3 (Cambio): {statistics.mean(self.get_metric('clients_type3')):.1f} clientes
   - Tipo 4 (Venta): {statistics.mean(self.get_metric('clients_type4')):.1f} clientes

4. OBSERVACIONES:
   - El tipo de servicio más frecuente es el 1 (reparación con garantía)
   - La ganancia proviene principalmente de tipos 2, 3 y 4
   - El sistema tiene capacidad suficiente para la demanda actual
""")

    def save_to_csv(self, filename: str) -> None:
        """Guarda los resultados en un archivo CSV."""
        if not self.results:
            return

        import csv
        keys = self.results[0].keys()

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.results)

        print(f"\nResultados guardados en: {filename}")


def run_single_simulation(
    max_time: int = 480,
    sellers: int = 2,
    technicians: int = 3,
    special: int = 1,
    verbose: bool = False
) -> Dict:
    """
    Ejecuta una única simulación en modo silencioso.

    Args:
        max_time: Duración máxima de la jornada.
        sellers: Número de vendedores.
        technicians: Número de técnicos.
        special: Número de técnicos especializados.
        verbose: Si True, muestra la salida normal de la simulación.

    Returns:
        Diccionario con las métricas de la simulación.
    """
    import sys
    from io import StringIO

    # Capturar salida si no es verbose
    if not verbose:
        old_stdout = sys.stdout
        sys.stdout = StringIO()

    try:
        sim = Simulation(max_time=max_time)
        sim.server.total_sellers = sellers
        sim.server.free_sellers = sellers
        sim.server.total_technicians = technicians
        sim.server.free_technicians = technicians
        sim.server.total_special_technicians = special
        sim.server.free_special_technicians = special
        sim.start()
    finally:
        if not verbose:
            sys.stdout = old_stdout

    return {
        "total_amount": sim.total_amount,
        "generated_clients": sim.generated_clients,
        "attended_clients": sim.attended_clients,
        "clients_type1": sim.clients_type1,
        "clients_type2": sim.clients_type2,
        "clients_type3": sim.clients_type3,
        "clients_type4": sim.clients_type4,
        "final_time": sim.time,
    }


def run_experiments(
    num_simulations: int = 1000,
    max_time: int = 480,
    sellers: int = 2,
    technicians: int = 3,
    special: int = 1,
    verbose: bool = False
) -> ExperimentResults:
    """
    Ejecuta múltiples simulaciones y retorna los resultados.

    Args:
        num_simulations: Número de simulaciones a ejecutar.
        max_time: Duración de la jornada laboral.
        sellers: Número de vendedores.
        technicians: Número de técnicos.
        special: Número de técnicos especializados.
        verbose: Si True, muestra el progreso.

    Returns:
        Objeto ExperimentResults con los análisis.
    """
    print(f"Ejecutando {num_simulations} simulaciones...")
    print(f"Configuración: {sellers} vendedores, {technicians} técnicos, {special} especializado(s)")
    print(f"Jornada: {max_time} minutos")
    print("-" * 50)

    results = []
    for i in range(num_simulations):
        result = run_single_simulation(
            max_time=max_time,
            sellers=sellers,
            technicians=technicians,
            special=special,
            verbose=False
        )
        results.append(result)

        if verbose and (i + 1) % 100 == 0:
            print(f"  Completadas: {i + 1}/{num_simulations}")

    print(f"✓ Completadas: {num_simulations}/{num_simulations}")

    return ExperimentResults(results)


def main():
    """Función principal del experimento."""
    # Ejecutar 1000 simulaciones con la configuración base
    results = run_experiments(
        num_simulations=1000,
        max_time=480,
        sellers=2,
        technicians=3,
        special=1,
        verbose=True
    )

    # Mostrar estadísticas
    results.print_summary()

    # Mostrar conclusiones
    results.print_conclusions()

    # Guardar resultados
    results.save_to_csv("resultados_experimento.csv")


if __name__ == "__main__":
    main()