"""
Módulo que define la entidad Cliente del sistema de simulación.

Representa a un cliente que llega al taller de reparaciones electrónicas
y solicita uno de los servicios disponibles.
"""

class Client:
    """
    Representa un cliente que arriba al taller para recibir un servicio.

    Atributos:
        id: Identificador único del cliente.
        arrival_time: Minuto en que el cliente llega al taller.
        service_type: Tipo de servicio solicitado (1-4).
    """

    def __init__(self, client_id : int, arrival_time : float, service_type : int):
        """
        Inicializa un nuevo cliente.

        Args:
            client_id (int): Identificador único del cliente.
            arrival_time (float): Tiempo de llegada en minutos.
            service_type (int): Tipo de servicio requerido:
                1 - Reparación con garantía (gratis)
                2 - Reparación sin garantía ($350)
                3 - Cambio de equipo ($500)
                4 - Venta de equipo ($750)
        """
        self.id = client_id
        self.arrival_time = arrival_time
        self.service_type = service_type