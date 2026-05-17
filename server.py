"""
Módulo que representa los recursos humanos del taller.

Gestiona la disponibilidad de vendedores, técnicos y técnicos especializados.
"""

class Server:
    """
    Representa los empleados del taller y su disponibilidad.

    Controla cuántos empleados de cada tipo están libres para atender
    a los clientes. Utiliza un modelo de recursos compartidos donde
    cada empleado puede atender un cliente a la vez.

    Atributos:
        total_sellers: Número total de vendedores en el taller.
        total_technicians: Número total de técnicos.
        total_special_technicians: Número total de técnicos especializados.
        free_sellers: Número de vendedores disponibles.
        free_technicians: Número de técnicos disponibles.
        free_special_technicians: Número de técnicos especializados disponibles.
    """

    def __init__(self,total_sellers : int = 2, total_technicians : int = 3,total_special_technicians : int = 1):
        """
        Inicializa el servidor con la configuración base del taller.
        
        Configuración actual: 2 vendedores, 3 técnicos, 1 técnico especializado.
        """
        self.total_sellers = total_sellers
        self.total_technicians = total_technicians
        self.total_special_technicians = total_special_technicians

        self.free_sellers = total_sellers
        self.free_technicians = total_technicians
        self.free_special_technicians = total_special_technicians