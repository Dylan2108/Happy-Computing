"""
Módulo que define la entidad Cliente del sistema de simulación.

Representa a un cliente que llega al taller de reparaciones electrónicas
y solicita uno de los servicios disponibles.
"""

class Client:
    def __init__(self, client_id : int, arrival_time : float, service_type : int):
        self.id = client_id
        self.arrival_time = arrival_time
        self.service_type = service_type
        self.wait_start_seller = None
        self.wait_start_technician = None
        self.wait_start_special = None
        self.service_start_time = None
        self.exit_time = None