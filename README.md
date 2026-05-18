# Happy Computing - Simulación de Eventos Discretos

Simulación de un taller de reparaciones electrónicas usando el método de eventos discretos con 10,000 réplicas Monte Carlo.

## Descripción

El taller "Happy Computing" cuenta con empleados que ofrecen servicios de reparación, cambio y venta de equipos electrónicos. El modelo simula el flujo de clientes, tiempos de espera y ganancias diarias.

### Recursos del Sistema

| Recurso | Cantidad | Función |
|---------|----------|---------|
| Vendedores | 2 | Atención inicial y ventas |
| Técnicos | 3 | Reparaciones |
| Técnico Especializado | 1 | Cambios de equipo y reparaciones |

### Tipos de Servicio

| Tipo | Descripción | Ganancia |
|------|-------------|----------|
| 1 | Reparación con garantía | $0 |
| 2 | Reparación sin garantía | $350 |
| 3 | Cambio de equipo | $500 |
| 4 | Venta de equipo | $750 |

### Distribución de Llegada de Clientes

| Tipo | Probabilidad |
|------|-------------|
| 1 | 45% |
| 2 | 25% |
| 3 | 10% |
| 4 | 20% |

## Estructura del Proyecto

```
├── main.py                    # Menú interactivo
├── simulation.py              # Motor de simulación de eventos discretos
├── experiment.py             # Experimentos (10,000 simulaciones)
├── client.py                 # Entidad cliente
├── event.py                  # Entidad evento
├── server.py                 # Recursos humanos
├── random_variables.py       # Generadores de variables aleatorias
├── docs/                   # Informe
└── results/                  # Resultados de experimentos
```

## Requisitos

- Python 3.12+
- numpy (para cálculo de estadísticas y percentiles)

## Instalación

```bash
pip install -r requirements.txt
```

## Cómo ejecutar

### Menú interactivo

```bash
python main.py
```

Opciones disponibles:
1. Ejecutar simulación con eventos detallados
2. Ejecutar simulación (solo resultados)
3. Ejecutar experimentos (múltiples simulaciones)

### Ejecutar experimentos directamente

```bash
python experiment.py
```

Ejecuta 10,000 simulaciones y genera:
- `results/experiments_results.csv` - Datos crudos de cada simulación
- `results/experiments_summary.txt` - Resumen con estadísticas


## Repositorio

https://github.com/Dylan2108/Happy-Computing