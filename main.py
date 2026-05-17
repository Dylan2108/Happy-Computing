"""
Punto de entrada del programa de simulación.

Inicia la simulación de eventos discretos del taller Happy Computing.
Permite ejecutar en diferentes modos: simulación individual (con/sin prints)
o experimentos con múltiples simulaciones.
"""

import sys

from simulation import Simulation
from experiment import run_experiments


def run_simulation_verbose(max_time: int = 480) -> None:
    """Ejecuta una simulación mostrando todos los eventos."""
    print("=" * 60)
    print("MODO: Simulación con eventos detallados")
    print(f"Jornada laboral: {max_time} minutos")
    print("=" * 60)
    simulation = Simulation(max_time=max_time, verbose=True)
    simulation.start()


def run_simulation_silent(max_time: int = 480) -> None:
    """Ejecuta una simulación sin mostrar detalles."""
    simulation = Simulation(max_time=max_time, verbose=False)
    simulation.start()


def run_experiments_menu() -> None:
    """Menú de configuración de experimentos."""
    print("\n" + "=" * 60)
    print("CONFIGURACIÓN DEL EXPERIMENTO")
    print("=" * 60)

    # Número de simulaciones
    print("\n1. Número de simulaciones (default: 1000)")
    num_input = input("   Presione Enter para usar default: ")
    num_simulations = int(num_input) if num_input.strip() else 1000

    # Duración de la jornada
    print("\n2. Duración de la jornada en minutos (default: 480)")
    time_input = input("   Presione Enter para usar default: ")
    max_time = int(time_input) if time_input.strip() else 480

    # Configuración de empleados
    print("\n3. Configuración de empleados")
    print("   Formato: vendedores,técnicos,especializados")
    print("   Default: 2,3,1")
    config_input = input("   Ingrese configuración: ")
    if config_input.strip():
        parts = config_input.split(",")
        sellers = int(parts[0]) if len(parts) > 0 else 2
        technicians = int(parts[1]) if len(parts) > 1 else 3
        special = int(parts[2]) if len(parts) > 2 else 1
    else:
        sellers, technicians, special = 2, 3, 1

    print(f"\nConfiguración seleccionada:")
    print(f"  - Simulaciones: {num_simulations}")
    print(f"  - Jornada: {max_time} minutos")
    print(f"  - Vendedores: {sellers}")
    print(f"  - Técnicos: {technicians}")
    print(f"  - Técnicos especializados: {special}")

    confirm = input("\n¿Confirmar ejecución? (s/n): ")
    if confirm.lower() != 's':
        print("Experimento cancelado.")
        return

    # Ejecutar experimentos
    results = run_experiments(
        num_simulations=num_simulations,
        max_time=max_time,
        sellers=sellers,
        technicians=technicians,
        special=special,
        verbose=True
    )

    results.print_summary()
    results.print_conclusions()

    save = input("\n¿Guardar resultados en CSV? (s/n): ")
    if save.lower() == 's':
        results.save_to_csv("experiments_results.csv")


def print_menu() -> None:
    """Muestra el menú principal."""
    print("\n" + "=" * 60)
    print("    SIMULACIÓN DE EVENTOS DISCRETOS - HAPPY COMPUTING")
    print("=" * 60)
    print("\nSeleccione una opción:")
    print("  1. Ejecutar simulación (con eventos detallados)")
    print("  2. Ejecutar simulación (solo resultados)")
    print("  3. Ejecutar experimentos (múltiples simulaciones)")
    print("  0. Salir")
    print("-" * 60)


def main() -> None:
    """Función principal con menú interactivo."""
    while True:
        print_menu()
        option = input("\nOpción: ").strip()

        if option == "1":
            time_input = input("Duración de la jornada (minutos, default 480): ")
            max_time = int(time_input) if time_input.strip() else 480
            run_simulation_verbose(max_time)

        elif option == "2":
            time_input = input("Duración de la jornada (minutos, default 480): ")
            max_time = int(time_input) if time_input.strip() else 480
            run_simulation_silent(max_time)

        elif option == "3":
            run_experiments_menu()

        elif option == "0":
            print("\n¡Hasta luego!")
            break

        else:
            print("\nOpción inválida. Intente de nuevo.")


if __name__ == "__main__":
    main()