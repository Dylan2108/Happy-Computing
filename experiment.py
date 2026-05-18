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
import numpy as np
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
            Diccionario con media, std, min, max, percentiles, IQR, IC 95%.
        """
        values = np.array(self.get_metric(metric))
        if len(values) == 0:
            return {}

        n = len(values)
        mean = np.mean(values)
        std = np.std(values, ddof=1) if n > 1 else 0
        min_val = np.min(values)
        max_val = np.max(values)

        p25 = np.percentile(values, 25)
        p50 = np.percentile(values, 50)
        p75 = np.percentile(values, 75)
        iqr = p75 - p25

        margin = 1.96 * (std / (n ** 0.5)) if n > 1 else 0

        return {
            "mean": mean,
            "std": std,
            "min": min_val,
            "max": max_val,
            "p25": p25,
            "p50": p50,
            "p75": p75,
            "iqr": iqr,
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
                print(f"  Percentiles: P25={stats['p25']:.2f} | P50={stats['p50']:.2f} | P75={stats['p75']:.2f}")
                print(f"  Rango intercuartílico (IQR): {stats['iqr']:.2f}")
                print(f"  IC 95%: [{stats['ci_lower']:.2f}, {stats['ci_upper']:.2f}]")
                print()

        # Análisis de servicios
        print("\n--- DISTRIBUCIÓN DE SERVICIOS (Promedio) ---")
        total_services = statistics.mean(self.get_metric("generated_clients"))
        for i in range(1, 5):
            count = statistics.mean(self.get_metric(f"clients_type{i}"))
            pct = (count / total_services * 100) if total_services > 0 else 0
            print(f"Tipo {i}: {count:.1f} clientes ({pct:.1f}%)")

        print("\n--- TIEMPOS DE ESPERA ---")
        wait_metrics = [
            ("avg_wait_seller", "Cola vendedores (min)"),
            ("avg_wait_technician", "Cola técnicos (min)"),
            ("avg_wait_special", "Cola técnicos especiales (min)"),
            ("avg_time_in_system", "Tiempo en sistema (min)"),
        ]
        for metric, label in wait_metrics:
            stats = self.calculate_stats(metric)
            if stats and stats['mean'] > 0:
                print(f"{label}:")
                print(f"  Media: {stats['mean']:.2f}")
                print(f"  Percentiles: P25={stats['p25']:.2f} | P50={stats['p50']:.2f} | P75={stats['p75']:.2f}")
                print(f"  IQR: {stats['iqr']:.2f}")
                print()

        print("\n--- UTILIZACIÓN DE SERVIDORES (%) ---")
        util_metrics = [
            ("seller_utilization", "Vendedores"),
            ("technician_utilization", "Técnicos"),
            ("special_utilization", "Técnicos especializados"),
        ]
        for metric, label in util_metrics:
            stats = self.calculate_stats(metric)
            if stats:
                print(f"{label}: {stats['mean']:.1f}% (IC 95%: [{stats['ci_lower']:.1f}, {stats['ci_upper']:.1f}])")

        print("\n--- PORCENTAJE DE OCIOSIDAD (%) ---")
        idle_metrics = [
            ("seller_idle_pct", "Vendedores"),
            ("technician_idle_pct", "Técnicos"),
            ("special_idle_pct", "Técnicos especializados"),
        ]
        for metric, label in idle_metrics:
            stats = self.calculate_stats(metric)
            if stats:
                print(f"{label}: {stats['mean']:.1f}% (IC 95%: [{stats['ci_lower']:.1f}, {stats['ci_upper']:.1f}])")

    def print_conclusions(self) -> None:
        """Imprime las conclusiones del análisis."""
        gain_stats = self.calculate_stats("total_amount")
        clients_stats = self.calculate_stats("generated_clients")
        wait_seller_stats = self.calculate_stats("avg_wait_seller")
        wait_tech_stats = self.calculate_stats("avg_wait_technician")
        time_sys_stats = self.calculate_stats("avg_time_in_system")
        seller_util = self.calculate_stats("seller_utilization")
        tech_util = self.calculate_stats("technician_utilization")
        special_util = self.calculate_stats("special_utilization")

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

3. TIEMPOS DE ESPERA:
   - Cola vendedores: {wait_seller_stats['mean']:.2f} min promedio (IC 95%: [{wait_seller_stats['ci_lower']:.2f}, {wait_seller_stats['ci_upper']:.2f}])
   - Cola técnicos: {wait_tech_stats['mean']:.2f} min promedio (IC 95%: [{wait_tech_stats['ci_lower']:.2f}, {wait_tech_stats['ci_upper']:.2f}])
   - Tiempo promedio en sistema: {time_sys_stats['mean']:.2f} min (P50={time_sys_stats['p50']:.2f}, IQR={time_sys_stats['iqr']:.2f})

4. UTILIZACIÓN DE RECURSOS Y OCISIDAD:
   - Vendedores: {seller_util['mean']:.1f}% utilizado (IC 95%: [{seller_util['ci_lower']:.1f}%, {seller_util['ci_upper']:.1f}%]) - Ociosidad: {100-seller_util['mean']:.1f}%
   - Técnicos: {tech_util['mean']:.1f}% utilizado (IC 95%: [{tech_util['ci_lower']:.1f}%, {tech_util['ci_upper']:.1f}%]) - Ociosidad: {100-tech_util['mean']:.1f}%
   - Técnicos especializados: {special_util['mean']:.1f}% utilizado (IC 95%: [{special_util['ci_lower']:.1f}%, {special_util['ci_upper']:.1f}%]) - Ociosidad: {100-special_util['mean']:.1f}%

5. TIPO DE SERVICIOS MÁS FRECUENTES:
   - Tipo 1 (Garantía): {statistics.mean(self.get_metric('clients_type1')):.1f} clientes
   - Tipo 2 (Sin garantía): {statistics.mean(self.get_metric('clients_type2')):.1f} clientes
   - Tipo 3 (Cambio): {statistics.mean(self.get_metric('clients_type3')):.1f} clientes
   - Tipo 4 (Venta): {statistics.mean(self.get_metric('clients_type4')):.1f} clientes
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

    def save_summary(self, filename: str) -> None:
        """Guarda el resumen textual en un archivo."""
        with open(filename, 'w') as f:
            import statistics
            
            f.write("=" * 70 + "\n")
            f.write("RESULTADOS DE EXPERIMENTACIÓN - SIMULACIÓN DE EVENTOS DISCRETOS\n")
            f.write(f"Número de simulaciones: {self.num_simulations}\n")
            f.write("=" * 70 + "\n\n")

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

            f.write("--- ESTADÍSTICAS PRINCIPALES ---\n\n")
            for metric, label in metrics:
                stats = self.calculate_stats(metric)
                if stats:
                    f.write(f"{label}:\n")
                    f.write(f"  Media: {stats['mean']:.2f}\n")
                    f.write(f"  Desviación estándar: {stats['std']:.2f}\n")
                    f.write(f"  Mín: {stats['min']:.2f} | Máx: {stats['max']:.2f}\n")
                    f.write(f"  Percentiles: P25={stats['p25']:.2f} | P50={stats['p50']:.2f} | P75={stats['p75']:.2f}\n")
                    f.write(f"  Rango intercuartílico (IQR): {stats['iqr']:.2f}\n")
                    f.write(f"  IC 95%: [{stats['ci_lower']:.2f}, {stats['ci_upper']:.2f}]\n\n")

            f.write("\n--- DISTRIBUCIÓN DE SERVICIOS (Promedio) ---\n")
            total_services = statistics.mean(self.get_metric("generated_clients"))
            for i in range(1, 5):
                count = statistics.mean(self.get_metric(f"clients_type{i}"))
                pct = (count / total_services * 100) if total_services > 0 else 0
                f.write(f"Tipo {i}: {count:.1f} clientes ({pct:.1f}%)\n")

            f.write("\n--- TIEMPOS DE ESPERA ---\n")
            wait_metrics = [
                ("avg_wait_seller", "Cola vendedores (min)"),
                ("avg_wait_technician", "Cola técnicos (min)"),
                ("avg_wait_special", "Cola técnicos especiales (min)"),
                ("avg_time_in_system", "Tiempo en sistema (min)"),
            ]
            for metric, label in wait_metrics:
                stats = self.calculate_stats(metric)
                if stats and stats['mean'] > 0:
                    f.write(f"{label}:\n")
                    f.write(f"  Media: {stats['mean']:.2f}\n")
                    f.write(f"  Percentiles: P25={stats['p25']:.2f} | P50={stats['p50']:.2f} | P75={stats['p75']:.2f}\n")
                    f.write(f"  IQR: {stats['iqr']:.2f}\n\n")

            f.write("\n--- UTILIZACIÓN DE SERVIDORES (%) ---\n")
            util_metrics = [
                ("seller_utilization", "Vendedores"),
                ("technician_utilization", "Técnicos"),
                ("special_utilization", "Técnicos especializados"),
            ]
            for metric, label in util_metrics:
                stats = self.calculate_stats(metric)
                if stats:
                    f.write(f"{label}: {stats['mean']:.1f}% (IC 95%: [{stats['ci_lower']:.1f}, {stats['ci_upper']:.1f}])\n")

            f.write("\n--- PORCENTAJE DE OCIOSIDAD (%) ---\n")
            idle_metrics = [
                ("seller_idle_pct", "Vendedores"),
                ("technician_idle_pct", "Técnicos"),
                ("special_idle_pct", "Técnicos especializados"),
            ]
            for metric, label in idle_metrics:
                stats = self.calculate_stats(metric)
                if stats:
                    f.write(f"{label}: {stats['mean']:.1f}%\n")

            gain_stats = self.calculate_stats("total_amount")
            clients_stats = self.calculate_stats("generated_clients")
            wait_seller_stats = self.calculate_stats("avg_wait_seller")
            wait_tech_stats = self.calculate_stats("avg_wait_technician")
            time_sys_stats = self.calculate_stats("avg_time_in_system")
            seller_util = self.calculate_stats("seller_utilization")
            tech_util = self.calculate_stats("technician_utilization")
            special_util = self.calculate_stats("special_utilization")

            f.write("\n" + "=" * 70 + "\n")
            f.write("CONCLUSIONES\n")
            f.write("=" * 70 + "\n")
            f.write(f"""
1. GANANCIA ESPERADA:
   - La ganancia media por jornada de 8 horas es de ${gain_stats['mean']:.2f}
   - Con un intervalo de confianza del 95%: [{gain_stats['ci_lower']:.2f}, {gain_stats['ci_upper']:.2f}]
   - La variabilidad (desviación estándar) es de ${gain_stats['std']:.2f}

2. CAPACIDAD DEL SISTEMA:
   - En promedio llegan {clients_stats['mean']:.1f} clientes por jornada
   - El sistema atiende aproximadamente {statistics.mean(self.get_metric('attended_clients')):.1f} clientes
   - Algunos clientes quedan sin atender al cierre: {clients_stats['mean'] - statistics.mean(self.get_metric('attended_clients')):.1f} en promedio

3. TIEMPOS DE ESPERA:
   - Cola vendedores: {wait_seller_stats['mean']:.2f} min promedio
   - Cola técnicos: {wait_tech_stats['mean']:.2f} min promedio
   - Tiempo promedio en sistema: {time_sys_stats['mean']:.2f} min (P50={time_sys_stats['p50']:.2f}, IQR={time_sys_stats['iqr']:.2f})

4. UTILIZACIÓN DE RECURSOS Y OCISIDAD:
   - Vendedores: {seller_util['mean']:.1f}% utilizado - Ociosidad: {100-seller_util['mean']:.1f}%
   - Técnicos: {tech_util['mean']:.1f}% utilizado - Ociosidad: {100-tech_util['mean']:.1f}%
   - Técnicos especializados: {special_util['mean']:.1f}% utilizado - Ociosidad: {100-special_util['mean']:.1f}%

5. TIPO DE SERVICIOS MÁS FRECUENTES:
   - Tipo 1 (Garantía): {statistics.mean(self.get_metric('clients_type1')):.1f} clientes
   - Tipo 2 (Sin garantía): {statistics.mean(self.get_metric('clients_type2')):.1f} clientes
   - Tipo 3 (Cambio): {statistics.mean(self.get_metric('clients_type3')):.1f} clientes
   - Tipo 4 (Venta): {statistics.mean(self.get_metric('clients_type4')):.1f} clientes
""")

        print(f"Resumen guardado en: {filename}")


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
        "avg_wait_seller": statistics.mean(sim.wait_times_seller) if sim.wait_times_seller else 0,
        "avg_wait_technician": statistics.mean(sim.wait_times_technician) if sim.wait_times_technician else 0,
        "avg_wait_special": statistics.mean(sim.wait_times_special) if sim.wait_times_special else 0,
        "avg_time_in_system": statistics.mean(sim.time_in_system) if sim.time_in_system else 0,
        "seller_utilization": (sum(sim.seller_busy_time) / (sim.server.total_sellers * sim.max_time) * 100) if sim.server.total_sellers > 0 else 0,
        "technician_utilization": (sum(sim.technician_busy_time) / (sim.server.total_technicians * sim.max_time) * 100) if sim.server.total_technicians > 0 else 0,
        "special_utilization": (sum(sim.special_busy_time) / (sim.server.total_special_technicians * sim.max_time) * 100) if sim.server.total_special_technicians > 0 else 0,
        "seller_idle_pct": 100 - (sum(sim.seller_busy_time) / (sim.server.total_sellers * sim.max_time) * 100) if sim.server.total_sellers > 0 else 100,
        "technician_idle_pct": 100 - (sum(sim.technician_busy_time) / (sim.server.total_technicians * sim.max_time) * 100) if sim.server.total_technicians > 0 else 100,
        "special_idle_pct": 100 - (sum(sim.special_busy_time) / (sim.server.total_special_technicians * sim.max_time) * 100) if sim.server.total_special_technicians > 0 else 100,
    }


def run_experiments(
    num_simulations: int = 10000,
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
    import os
    
    os.makedirs("results", exist_ok=True)
    
    results = run_experiments(
        num_simulations=10000,
        max_time=480,
        sellers=2,
        technicians=3,
        special=1,
        verbose=True
    )

    results.print_summary()
    results.print_conclusions()

    results.save_to_csv("results/experiments_results.csv")
    results.save_summary("results/experiments_summary.txt")


if __name__ == "__main__":
    main()