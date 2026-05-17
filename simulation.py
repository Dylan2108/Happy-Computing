"""
Módulo principal del motor de simulación de eventos discretos.

Implementa el modelo de simulación del taller Happy Computing,
gestionando la cola de eventos, el estado del sistema y el
flujo de clientes a través de los diferentes servicios.

Utiliza un heap (cola de prioridad) para mantener los eventos
ordenados por tiempo de ocurrencia.
"""

import heapq
from collections import deque

from client import Client
from event import Event
from server import Server

from random_variables import (
    arrival_time,
    seller_service_time,
    repair_time,
    equipment_change_time,
    generate_service_type
)


class Simulation:
    """
    Motor de simulación de eventos discretos para el taller Happy Computing.

    Gestiona el tiempo de simulación, la cola de eventos, las colas de espera
    de clientes y las estadísticas del sistema.

    Atributos:
        max_time: Duración máxima de la jornada laboral (default 480 min).
        time: Tiempo actual de la simulación.
        closed: Indica si el taller ha cerrado sus puertas.
        events: Cola de prioridad con los eventos pendientes.
        server: Gestor de recursos humanos (vendedores, técnicos).
        sellers_queue: Cola de espera de vendedores.
        technicians_queue: Cola de espera de técnicos.
        special_technicians_queue: Cola de espera de técnicos especializados.
        generated_clients: Total de clientes generados.
        attended_clients: Clientes que han completado su servicio.
        total_amount: Ganancia acumulada en la jornada.
        clients_type1-4: Contadores de clientes por tipo de servicio.
        clients_in_system: Clientes actualmente en el sistema.
    """

    def __init__(self, max_time=480, verbose=True):
        """
        Inicializa la simulación con la duración de la jornada laboral.

        Args:
            max_time (float): Duración máxima en minutos. Default 480 (8 horas).
            verbose (bool): Si True, muestra los eventos en consola. Default True.
        """
        self.max_time = max_time
        self.verbose = verbose
        self.time = 0
        self.closed = False
        self.events = []
        self.server = Server()

        self.sellers_queue = deque()
        self.technicians_queue = deque()
        self.special_technicians_queue = deque()

        self.generated_clients = 0
        self.attended_clients = 0
        self.total_amount = 0
        self.clients_type1 = 0
        self.clients_type2 = 0
        self.clients_type3 = 0
        self.clients_type4 = 0
        self.clients_in_system = 0

    def log(self, *args, **kwargs) -> None:
        """Imprime mensajes solo si verbose=True."""
        if self.verbose:
            print(*args, **kwargs)
    
    def save_event(self, event: Event) -> None:
        """
        Agrega un evento a la cola de eventos priorizada.

        Utiliza heapq para mantener los eventos ordenados por tiempo
        de ocurrencia con complejidad O(log n).

        Args:
            event (Event): Evento a agregar a la cola.
        """
        heapq.heappush(self.events, event)

    def start(self) -> None:
        """
        Inicia la simulación creando el primer evento de llegada.

        Genera el primer cliente y programa su llegada al taller.
        Luego ejecuta el ciclo principal de simulación.
        """
        first_client = Client(
            1,
            arrival_time(),
            generate_service_type()
        )
        first_event = Event(
            first_client.arrival_time,
            "arrival",
            first_client
        )
        self.save_event(first_event)

        self.simulate()
    
    def simulate(self) -> None:
        """
        Ciclo principal de la simulación.

        Procesa eventos en orden cronológico hasta que la cola de eventos
        se vacíe. Por cada evento:
        1. Extrae el evento con menor tiempo.
        2. Actualiza el tiempo de simulación.
        3. Verifica si es hora de cerrar el taller.
        4. Procesa el evento según su tipo.
        """
        while self.events:
            actual_event: Event = heapq.heappop(self.events)
            self.time = actual_event.time

            if self.time >= self.max_time and not self.closed:
                self.closed = True
                sellers_occupied = self.server.total_sellers - self.server.free_sellers
                technicians_occupied = self.server.total_technicians - self.server.free_technicians
                special_occupied = self.server.total_special_technicians - self.server.free_special_technicians
                self.log(f"\n========== minuto {self.max_time:.2f}: Hora de cierre del taller. Atendiendo clientes restantes ==========")
                self.log(f"Clientes en el sistema: {self.clients_in_system}")
                self.log(f"Atendiendo: {sellers_occupied}/{self.server.total_sellers} vendedores | {technicians_occupied}/{self.server.total_technicians} técnicos | {special_occupied}/{self.server.total_special_technicians} especializado(s)")
                self.log(f"En cola: {len(self.sellers_queue)} vendedores | {len(self.technicians_queue)} técnicos | {len(self.special_technicians_queue)} especializado(s)")
            
            self.log(f"\n========== minuto {self.time:.2f} ==========")
            
            if actual_event.type == "arrival":
                self.process_arrival(actual_event)
            elif actual_event.type == "seller_end":
                self.seller_end(actual_event)
            elif actual_event.type == "technichian_end":
                self.technichian_end(actual_event)
            elif actual_event.type == "special_technichian_end":
                self.special_technichian_end(actual_event)
            
            sellers_occupied = self.server.total_sellers - self.server.free_sellers
            technicians_occupied = self.server.total_technicians - self.server.free_technicians
            special_occupied = self.server.total_special_technicians - self.server.free_special_technicians
            
            self.log(f"Clientes en el sistema: {self.clients_in_system}")
            self.log(f"Atendiendo: {sellers_occupied}/{self.server.total_sellers} vendedores | {technicians_occupied}/{self.server.total_technicians} técnicos | {special_occupied}/{self.server.total_special_technicians} especializado(s)")
            self.log(f"En cola: {len(self.sellers_queue)} vendedores | {len(self.technicians_queue)} técnicos | {len(self.special_technicians_queue)} especializado(s)")
        

        self.show_results()
    
    def process_arrival(self, event: Event) -> None:
        """
        Procesa la llegada de un cliente al taller.

        El cliente puede:
        - Ser atendido inmediatamente si hay vendedores libres.
        - Encolarse si todos los vendedores están ocupados.
        
        También programa la próxima llegada si el tiempo lo permite.

        Args:
            event (Event): Evento de llegada containing el cliente.
        """
        client: Client = event.client
        self.generated_clients += 1
        self.clients_in_system += 1

        if client.service_type == 1:
            self.clients_type1 += 1
        elif client.service_type == 2:
            self.clients_type2 += 1
        elif client.service_type == 3:
            self.clients_type3 += 1
        else:
            self.clients_type4 += 1
        
        next_time = self.time + arrival_time()
        
        self.log(f"minuto {self.time:.2f}: Llegó el cliente {client.id} y quiere un servicio de tipo {client.service_type}")
        if next_time < self.max_time:
            new_client = Client(
                self.generated_clients + 1,
                next_time,
                generate_service_type()
            )

            self.save_event(
                Event(next_time, "arrival", new_client)
            )

        if self.server.free_sellers > 0:
            self.server.free_sellers -= 1
            self.log(f"minuto {self.time:.2f}: El cliente {client.id} está siendo atendido por un vendedor")
            time_of_work = seller_service_time()
            end = self.time + time_of_work

            self.save_event(
                Event(end, "seller_end", client)
            )
        else:
            self.sellers_queue.append(client)
            self.log(f"minuto {self.time:.2f}: El cliente {client.id} se colocou en la cola de los vendedores ya que no había ninguno disponible")
    
    def seller_end(self, event: Event) -> None:
        """
        Procesa el fin de atención por parte de un vendedor.

        Libera al vendedor y:
        - Atiende al próximo cliente en cola de vendedores (si existe).
        - Dirige al cliente actual según su tipo de servicio:
          - Tipos 1, 2: Envía a reparación.
          - Tipo 3: Envía a cambio de equipo.
          - Tipo 4: Cobra $750 y el cliente sale del sistema.

        Args:
            event (Event): Evento de fin de atención del vendedor.
        """
        client: Client = event.client
        self.server.free_sellers += 1
        self.log(f"minuto {self.time:.2f}: El cliente {client.id} terminó de ser atendido por el vendedor")
        if self.sellers_queue:
            next_client: Client = self.sellers_queue.popleft()
            self.server.free_sellers -= 1
            time_of_work = seller_service_time()
            end = self.time + time_of_work

            self.save_event(
                Event(end, "seller_end", next_client)
            )
        
        if client.service_type in [1, 2]:
            self.log(f"minuto {self.time:.2f}: El cliente {client.id} fue enviado al servicio de reparación")
            self.send_to_repair(client)
        elif client.service_type == 3:
            self.log(f"minuto {self.time:.2f}: El cliente {client.id} fue enviado al servicio de cambio de equipo")
            self.send_to_change_equipment(client)
        else:
            self.log(f"minuto {self.time:.2f}: Al cliente {client.id} le vendieron un equipo")
            self.total_amount += 750
            self.attended_clients += 1
            self.clients_in_system -= 1
            self.log(f"minuto {self.time:.2f}: Ganancia generada hasta el momento: ${self.total_amount}")
    
    def send_to_repair(self, client: Client) -> None:
        """
        Envía un cliente al servicio de reparación.

        El cliente puede ser atendido por:
        1. Un técnico regular (si hay disponibles).
        2. Un técnico especializado (solo si no hay clientes esperando
           cambio de equipo en la cola).
        3. La cola de técnicos (si no hay recursos disponibles).

        Args:
            client (Client): Cliente que requiere reparación.
        """
        if self.server.free_technicians > 0:
            self.log(f"minuto {self.time:.2f}: El cliente {client.id} está siendo atendido por un técnico")
            self.server.free_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end, "technichian_end", client)
            )
        elif (
            self.server.free_special_technicians > 0 
            and len(self.special_technicians_queue) == 0
        ):
            self.log(f"minuto {self.time:.2f}: El cliente {client.id} está siendo atendido por un técnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end, "special_technichian_end", client)
            )
        else:
            self.log(f"minuto {self.time:.2f}: El cliente {client.id} se colocou en la cola de los técnicos ya que no había ninguno disponible")
            self.technicians_queue.append(client)
    
    def send_to_change_equipment(self, client: Client) -> None:
        """
        Envía un cliente al servicio de cambio de equipo.

        Solo puede ser atendido por un técnico especializado.
        Si no hay ninguno disponible, el cliente pasa a la cola
        de técnicos especializados.

        Args:
            client (Client): Cliente que requiere cambio de equipo.
        """
        if self.server.free_special_technicians > 0:
            self.log(f"minuto {self.time:.2f}: El cliente {client.id} está siendo atendido por un técnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = equipment_change_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end, "special_technichian_end", client)
            )
        else:
            self.log(f"minuto {self.time:.2f}: El cliente {client.id} se放在了cola de los técnicos especializados ya que no había ninguno disponible")
            self.special_technicians_queue.append(client)
    
    def technichian_end(self, event: Event) -> None:
        """
        Procesa el fin de reparación por parte de un técnico.

        Libera al técnico y:
        - Registra la ganancia (solo para tipo 2: $350).
        - Registra al cliente como atendido.
        - Atiende al próximo cliente en cola de técnicos (si existe).

        Args:
            event (Event): Evento de fin de reparación.
        """
        client: Client = event.client
        self.log(f"minuto {self.time:.2f}: El cliente {client.id} terminó de ser atendido por el técnico")
        self.server.free_technicians += 1

        if client.service_type == 2:
            self.total_amount += 350
            self.log(f"minuto {self.time:.2f}: Al cliente {client.id} el técnico le reparó un equipo sin garantía")
            self.log(f"minuto {self.time:.2f}: Ganancia generada hasta el momento: ${self.total_amount}")
        else:
            self.log(f"minuto {self.time:.2f}: Al cliente {client.id} el técnico le reparó un equipo con garantía")
        
        self.attended_clients += 1
        self.clients_in_system -= 1

        if self.technicians_queue:
            next_client: Client = self.technicians_queue.popleft()
            self.log(f"minuto {self.time:.2f}: El cliente {next_client.id} sale de la cola para ser atendido por el técnico")
            self.server.free_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end, "technichian_end", next_client)
            )
    
    def special_technichian_end(self, event: Event) -> None:
        """
        Procesa el fin de servicio por parte de un técnico especializado.

        Libera al técnico especializado y:
        - Registra la ganancia según el tipo de servicio:
          - Tipo 2: $350 (reparación sin garantía)
          - Tipo 3: $500 (cambio de equipo)
        - Registra al cliente como atendido.
        - Prioriza atender clientes de la cola de cambios de equipo.
        - Solo si esa cola está vacía, atiende reparaciones.

        Args:
            event (Event): Evento de fin de servicio especializado.
        """
        client: Client = event.client
        self.server.free_special_technicians += 1
        self.log(f"minuto {self.time:.2f}: El cliente {client.id} terminó de ser atendido por el técnico especializado")
        
        if client.service_type == 3:
            self.total_amount += 500
            self.log(f"minuto {self.time:.2f}: Al cliente {client.id} el técnico especializado le realizó un cambio de equipo")
            self.log(f"minuto {self.time:.2f}: Ganancia generada hasta el momento: ${self.total_amount:.2f}")
        elif client.service_type == 2:
            self.total_amount += 350
            self.log(f"minuto {self.time:.2f}: Al cliente {client.id} el técnico especializado le reparó un equipo sin garantía")
            self.log(f"minuto {self.time:.2f}: Ganancia generada hasta el momento: ${self.total_amount:.2f}")

        
        self.attended_clients += 1
        self.clients_in_system -= 1

        if self.special_technicians_queue:
            next_client: Client = self.special_technicians_queue.popleft()
            self.log(f"minuto {self.time:.2f}: El cliente {next_client.id} sale de la cola de cambios de equipo para ser atendido por el técnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = equipment_change_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end, "special_technichian_end", next_client)
            )
        elif self.technicians_queue:
            next_client: Client = self.technicians_queue.popleft()
            self.log(f"minuto {self.time:.2f}: El cliente {next_client.id} sale de la cola de reparaciones para ser atendido por el técnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end, "special_technichian_end", next_client)
            )
    
    def show_results(self) -> None:
        """
        Muestra las estadísticas finales de la simulación.

        Imprime en consola:
        - Tiempo final de simulación.
        - Total de clientes generados.
        - Clientes atendidos.
        - Ganancia total.
        - Distribución de tipos de servicio atendidos.
        """
        print("\n========== RESULTADOS ==========")
        print(f"Tiempo final de simulación: {self.time:.2f} minutos")
        print(f"Clientes generados: {self.generated_clients}")
        print(f"Clientes atendidos: {self.attended_clients}")
        print(f"Ganancia total: ${self.total_amount:.2f}")
        print("\n--- Tipos de servicio ---")
        print(f"Tipo 1: {self.clients_type1}")
        print(f"Tipo 2: {self.clients_type2}")
        print(f"Tipo 3: {self.clients_type3}")
        print(f"Tipo 4: {self.clients_type4}")