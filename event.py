"""
Módulo que define la entidad Evento del sistema de simulación.

Representa un evento discreto que ocurre en un momento específico
y modifica el estado del sistema (llegada, fin de atención, etc.).
"""
from __future__ import annotations
from client import Client

class Event:
    """
    Representa un evento en la simulación de eventos discretos.

    Los eventos son ordenados por tiempo de ocurrencia usando un heap,
    lo que permite procesar los eventos en orden cronológico.

    Atributos:
        time: Momento en que ocurre el evento (en minutos).
        type: Tipo de evento ('arrival', 'seller_end', etc.).
        client: Cliente asociado al evento (si aplica).
    """

    def __init__(self, time : float, event_type : str, client : Client):
        """
        Inicializa un nuevo evento.

        Args:
            time (float): Tiempo de ocurrencia del evento.
            event_type (str): Tipo de evento:
                - 'arrival': Llegada de un cliente al taller.
                - 'seller_end': Fin de atención por vendedor.
                - 'technichian_end': Fin de reparación por técnico.
                - 'special_technichian_end': Fin de servicio por técnico especializado.
            client (Client): Cliente relacionado con el evento.
        """
        self.time = time
        self.type = event_type
        self.client = client
    
    def __lt__(self, other : Event) -> bool:
        """
        Compara dos eventos por su tiempo de ocurrencia.

        Necesario para usar la clase Event en un heapq (cola de prioridad).

        Args:
            other (Event): Otro evento a comparar.

        Returns:
            bool: True si este evento ocurre antes que el otro.
        """
        return self.time < other.time