# Centro de Servicio Técnico - Simulación de Eventos Discretos

Simulación de un centro de servicio técnico de equipos de cómputo usando el método de eventos discretos.

## Descripción

El taller cuenta con:
- **2 vendedores** que atienden a los clientes y venden equipos
- **3 técnicos** que realizan reparaciones
- **1 técnico especializado** que realiza cambios de equipo y también puede hacer reparaciones

### Tipos de Servicio

| Tipo | Descripción | Ganancia |
|------|-------------|----------|
| 1 | Venta + Reparación con garantía | $0 |
| 2 | Venta + Reparación sin garantía | $350 |
| 3 | Venta + Cambio de equipo | $500 |
| 4 | Solo venta de equipo | $750 |

### Distribución de llegada de clientes

| Tipo | Probabilidad |
|------|-------------|
| 1 | 45% |
| 2 | 25% |
| 3 | 10% |
| 4 | 20% |

## Estructura del Proyecto

```
├── main.py              # Punto de entrada de la simulación
├── simulation.py        # Motor principal de eventos discretos
├── client.py            # Modelo de cliente
├── event.py             # Modelo de evento
├── server.py            # Modelo de servidores
├── random_variables.py  # Generadores de variables aleatorias
└── random_variables_test.py # Pruebas unitarias
```

### Archivos principales

- **main.py**: Crea y ejecuta la simulación con un tiempo máximo de 480 minutos (8 horas).

- **simulation.py**: Contiene la clase `Simulation` que gestiona la cola de eventos, procesa llegadas y salidas, y lleva control de colas de espera.

- **client.py**: Define la estructura de un cliente con su ID, tiempo de llegada y tipo de servicio.

- **event.py**: Representa los eventos de la simulación (llegada, fin de venta, fin de reparación, etc.).

- **server.py**: Controla la disponibilidad de vendedores y técnicos.

- **random_variables.py**: Implementa generadores de variables aleatorias usando métodos como inversa y Box-Muller.

## Requisitos

- Python 3.12+

## Cómo ejecutar

```bash
python main.py
```

La simulación mostrará en consola:
- Cada evento que ocurre con su minuto correspondiente
- Estado del sistema (clientes en cola, servidores ocupados)
- Resultados finales al terminar