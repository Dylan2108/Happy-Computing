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
    def __init__(self,max_time = 480):
        self.max_time = max_time
        self.time = 0
        self.closed = False
        self.events = []
        self.server = Server()

        self.sellers_queue  = deque()
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
    
    def save_event(self, event):
        heapq.heappush(self.events,event)

    def start(self):
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
    
    def simulate(self):
        while self.events:
            actual_event : Event = heapq.heappop(self.events)
            self.time = actual_event.time

            if self.time >= self.max_time and not self.closed:
                self.closed = True
                sellers_occupied = self.server.total_sellers - self.server.free_sellers
                technicians_occupied = self.server.total_technicians - self.server.free_technicians
                special_occupied = self.server.total_special_technicians - self.server.free_special_technicians
                print(f"\n========== minuto {self.max_time:.2f}: Hora de cierre del taller. Atendiendo clientes restantes ==========")
                print(f"Clientes en el sistema: {self.clients_in_system}")
                print(f"Atendiendo: {sellers_occupied}/{self.server.total_sellers} vendedores | {technicians_occupied}/{self.server.total_technicians} técnicos | {special_occupied}/{self.server.total_special_technicians} especializado(s)")
                print(f"En cola: {len(self.sellers_queue)} vendedores | {len(self.technicians_queue)} técnicos | {len(self.special_technicians_queue)} especializado(s)")
            
            print(f"\n========== minuto {self.time:.2f} ==========")
            
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
            
            print(f"Clientes en el sistema: {self.clients_in_system}")
            print(f"Atendiendo: {sellers_occupied}/{self.server.total_sellers} vendedores | {technicians_occupied}/{self.server.total_technicians} técnicos | {special_occupied}/{self.server.total_special_technicians} especializado(s)")
            print(f"En cola: {len(self.sellers_queue)} vendedores | {len(self.technicians_queue)} técnicos | {len(self.special_technicians_queue)} especializado(s)")

        

        self.show_results()
    
    def process_arrival(self, event : Event):
        client : Client = event.client
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
        
        print(f"minuto {self.time:.2f}: Llegó el cliente {client.id} y quiere un servicio de tipo {client.service_type}")
        if next_time < self.max_time:
            new_client = Client(
                self.generated_clients + 1,
                next_time,
                generate_service_type()
            )

            self.save_event(
                Event(next_time,"arrival",new_client)
            )

        if self.server.free_sellers > 0:
            self.server.free_sellers -= 1
            print(f"minuto {self.time:.2f}: El cliente {client.id} está siendo atendido por un vendedor")
            time_of_work = seller_service_time()
            end = self.time + time_of_work

            self.save_event(
                Event(end,"seller_end",client)
            )
        else:
            self.sellers_queue.append(client)
            print(f"minuto {self.time:.2f}: El cliente {client.id} se colocó en la cola de los vendedores ya que no había ninguno disponible")
    
    def seller_end(self, event : Event):
        client : Client = event.client
        self.server.free_sellers += 1
        print(f"minuto {self.time:.2f}: El cliente {client.id} terminó de ser atendido por el vendedor")
        if self.sellers_queue:
            next : Client = self.sellers_queue.popleft()
            self.server.free_sellers -= 1
            time_of_work = seller_service_time()
            end = self.time + time_of_work

            self.save_event(
                Event(end,"seller_end",next)
            )
        
        if client.service_type in [1,2]:
            print(f"minuto {self.time:.2f}: El cliente {client.id} fue enviado al servicio de reparación")
            self.send_to_repair(client)
        elif client.service_type == 3:
            print(f"minuto {self.time:.2f}: El cliente {client.id} fue enviado al servicio de cambio de equipo")
            self.send_to_change_equipment(client)
        else:
            print(f"minuto {self.time:.2f}: Al cliente {client.id} le vendieron un equipo")
            self.total_amount += 750
            self.attended_clients += 1
            self.clients_in_system -= 1
            print(f"minuto {self.time:.2f}: Ganancia generada hasta el momento: ${self.total_amount}")
    
    def send_to_repair(self, client : Client):
        if self.server.free_technicians > 0:
            print(f"minuto {self.time:.2f}: El cliente {client.id} está siendo atendido por un técnico")
            self.server.free_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"technichian_end",client)
            )
        elif (
            self.server.free_special_technicians > 0 
            and len(self.special_technicians_queue) == 0):
            print(f"minuto {self.time:.2f}: El cliente {client.id} está siendo atendido por un técnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"special_technichian_end",client)
            )
        else:
            print(f"minuto {self.time:.2f}: El cliente {client.id} se colocó en la cola de los técnicos ya que no había ninguno disponible")
            self.technicians_queue.append(client)
    
    def send_to_change_equipment(self, client : Client):
        if self.server.free_special_technicians > 0:
            print(f"minuto {self.time:.2f}: El cliente {client.id} está siendo atendido por un técnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = equipment_change_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"special_technichian_end",client)
            )
        else:
            print(f"minuto {self.time:.2f}: El cliente {client.id} se colocó en la cola de los técnicos especializados ya que no había ninguno disponible")
            self.special_technicians_queue.append(client)
    
    def technichian_end(self, event : Event):
        client : Client = event.client
        print(f"minuto {self.time:.2f}: El cliente {client.id} terminó de ser atendido por el técnico")
        self.server.free_technicians += 1

        if client.service_type == 2:
            self.total_amount += 350
            print(f"minuto {self.time:.2f}: Al cliente {client.id} el técnico le reparó un equipo sin garantía")
            print(f"minuto {self.time:.2f}: Ganancia generada hasta el momento: ${self.total_amount}")
        else:
            print(f"minuto {self.time:.2f}: Al cliente {client.id} el técnico le reparó un equipo con garantía")
        
        self.attended_clients += 1
        self.clients_in_system -= 1

        if self.technicians_queue:
            next : Client = self.technicians_queue.popleft()
            print(f"minuto {self.time:.2f}: El cliente {next.id} sale de la cola para ser atendido por el técnico")
            self.server.free_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"technichian_end",next)
            )
    
    def special_technichian_end(self, event : Event):
        client : Client = event.client
        self.server.free_special_technicians += 1
        print(f"minuto {self.time:.2f}: El cliente {client.id} terminó de ser atendido por el técnico especializado")
        
        if client.service_type == 3:
            self.total_amount += 500
            print(f"minuto {self.time:.2f}: Al cliente {client.id} el técnico especializado le realizó un cambio de equipo")
            print(f"minuto {self.time:.2f}: Ganancia generada hasta el momento: ${self.total_amount:.2f}")
        elif client.service_type == 2:
            self.total_amount += 350
            print(f"minuto {self.time:.2f}: Al cliente {client.id} el técnico especializado le reparó un equipo sin garantía")
            print(f"minuto {self.time:.2f}: Ganancia generada hasta el momento: ${self.total_amount:.2f}")

        
        self.attended_clients += 1
        self.clients_in_system -= 1

        if self.special_technicians_queue:
            next : Client = self.special_technicians_queue.popleft()
            print(f"minuto {self.time:.2f}: El cliente {next.id} sale de la cola de cambios de equipo para ser atendido por el técnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = equipment_change_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"special_technichian_end",next)
            )
        elif self.technicians_queue:
            next : Client = self.technicians_queue.popleft()
            print(f"minuto {self.time:.2f}: El cliente {next.id} sale de la cola de reparaciones para ser atendido por el técnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"special_technichian_end",next)
            )
    
    def show_results(self):
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