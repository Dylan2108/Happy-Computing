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
        self.total_await_time = 0
        self.clients_type1 = 0
        self.clients_type2 = 0
        self.clients_type3 = 0
        self.clients_type4 = 0
    
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
                print(f"\n========== minuto {self.max_time} : Hora de cierre del taller. Atendiendo clientes restantes ==========")
                print(f"Clientes en colas al cierre:")
                print(f"  - Vendedores: {len(self.sellers_queue)}")
                print(f"  - Técnicos: {len(self.technicians_queue)}")
                print(f"  - Especializados: {len(self.special_technicians_queue)}")
            
            print(f"\n========== minuto :  {self.time} ==========")
            
            if actual_event.type == "arrival":
                self.process_arrival(actual_event)
            elif actual_event.type == "seller_end":
                self.seller_end(actual_event)
            elif actual_event.type == "technichian_end":
                self.technichian_end(actual_event)
            elif actual_event.type == "special_technichian_end":
                self.special_technichian_end(actual_event)
        

        self.show_results()
    
    def process_arrival(self, event : Event):
        client : Client = event.client
        self.generated_clients += 1

        if client.service_type == 1:
            self.clients_type1 += 1
        elif client.service_type == 2:
            self.clients_type2 += 1
        elif client.service_type == 3:
            self.clients_type3 += 1
        else:
            self.clients_type4 += 1
        
        next_time = self.time + arrival_time()
        
        print(f"minuto {self.time} : Llego el cliente {client.id} y quiere un servicio de tipo {client.service_type}")
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
            print(f"minuto {self.time} El cliente {client.id} esta siendo atendido por un vendedor")
            client.seller_initial_time = self.time
            time_of_work = seller_service_time()
            end = self.time + time_of_work
            client.seller_final_time = end

            self.save_event(
                Event(end,"seller_end",client)
            )
        else:
            self.sellers_queue.append(client)
            print(f"minuto {self.time} : El cliente {client.id} se coloco en la cola de los vendedores ya que no habia ninguno disponible")
    
    def seller_end(self, event : Event):
        client : Client = event.client
        self.server.free_sellers += 1
        print(f"minuto {self.time} : El cliente {client.id} termino de ser atendido por el vendedor")
        if self.sellers_queue:
            next : Client = self.sellers_queue.popleft()
            self.server.free_sellers -= 1
            next.seller_initial_time = self.time
            time_of_work = seller_service_time()
            end = self.time + time_of_work
            next.seller_final_time = end

            self.save_event(
                Event(end,"seller_end",next)
            )
        
        if client.service_type in [1,2]:
            print(f"minuto {self.time} : El cliente {client.id} fue enviado al servicio de reparacion")
            self.send_to_repair(client)
        elif client.service_type == 3:
            print(f"minuto {self.time} : El cliente {client.id} fue enviado al servicio de cambio de equipo")
            self.send_to_change_equipment(client)
        else:
            print(f"minuto {self.time} : Al cliente {client.id} le vendieron un equipo")
            self.total_amount += 750
            self.attended_clients += 1
            print(f"minuto {self.time} : Ganacia generada hasta el momento {self.total_amount}")
    
    def send_to_repair(self, client : Client):
        if self.server.free_technicians > 0:
            print(f"minuto {self.time} : El cliente {client.id} esta siendo atendido por un tecnico")
            self.server.free_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"technichian_end",client)
            )
        elif (
            self.server.free_special_technicians > 0 
            and len(self.special_technicians_queue) == 0):
            print(f"minuto {self.time} : El cliente {client.id} esta siendo atendido por un tecnico specializado")
            self.server.free_special_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"special_technichian_end",client)
            )
        else:
            print(f"minuto {self.time} : El cliente {client.id} se coloco en la cola de los tecnicos ya que no habia ninguno disponible")
            self.technicians_queue.append(client)
    
    def send_to_change_equipment(self, client : Client):
        if self.server.free_special_technicians > 0:
            print(f"minuto {self.time} : El cliente {client.id} esta siendo atendido por un tecnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = equipment_change_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"special_technichian_end",client)
            )
        else:
            print(f"minuto {self.time} : El cliente {client.id} se coloco en la cola de los tecnicos especializados ya que no habia ninguno disponible")
            self.special_technicians_queue.append(client)
    
    def technichian_end(self, event : Event):
        client : Client = event.client
        print(f"minuto {self.time} : El cliente {client.id} termino de ser atendido por el tecnico")
        self.server.free_technicians += 1

        if client.service_type == 2:
            self.total_amount += 350
            print(f"minuto {self.time} : Al cliente {client.id} el tecnico le reparo un equipo sin garantia")
            print(f"minuto {self.time} : Ganacia generada hasta el momento {self.total_amount}")
        else:
            print(f"minuto {self.time} : Al cliente {client.id} el tecnico le reparo un equipo con garantia")
        
        self.attended_clients += 1

        if self.technicians_queue:
            next : Client = self.technicians_queue.popleft()
            print(f"minuto {self.time} : El cliente {next.id} sale de la cola para ser atendido por el tecnico")
            self.server.free_technicians -= 1
            time_of_work = repair_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"technichian_end",next)
            )
    
    def special_technichian_end(self, event : Event):
        client : Client = event.client
        self.server.free_special_technicians += 1
        print(f"minuto {self.time} : El cliente {client.id} termino de ser atendido por el tecnico especializado")
        
        if client.service_type == 3:
            self.total_amount += 500
            print(f"minuto {self.time} : Al cliente {client.id} el tecnico especializado le realizo un cambio de equipo")
            print(f"minuto {self.time} : Ganacia generada hasta el momento {self.total_amount}")
        elif client.service_type == 2:
            self.total_amount += 350
            print(f"minuto {self.time} : Al cliente {client.id} el tecnico especializado le reparo un equipo sin garantia")
            print(f"minuto {self.time} : Ganacia generada hasta el momento {self.total_amount}")

        
        self.attended_clients += 1

        if self.special_technicians_queue:
            next : Client = self.special_technicians_queue.popleft()
            print(f"minuto {self.time} : El cliente {next.id} sale de la cola de cambios de equipo para ser atendido por el tecnico especializado")
            self.server.free_special_technicians -= 1
            time_of_work = equipment_change_time()
            end = self.time + time_of_work
            self.save_event(
                Event(end,"special_technichian_end",next)
            )
        elif self.technicians_queue:
            next : Client = self.technicians_queue.popleft()
            print(f"minuto {self.time} : El cliente {next.id} sale de la cola de reparaciones para ser atendido por el tecnico especializado")
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
        print(f"Ganancia total: ${self.total_amount}")
        print("\n--- Tipos de servicio ---")
        print(f"Tipo 1: {self.clients_type1}")
        print(f"Tipo 2: {self.clients_type2}")
        print(f"Tipo 3: {self.clients_type3}")
        print(f"Tipo 4: {self.clients_type4}")
        print("\n--- Colas restantes ---")
        print(f"Cola vendedores: {len(self.sellers_queue)}")
        print(f"Cola técnicos: {len(self.technicians_queue)}")
        print(f"Cola especializado: {len(self.special_technicians_queue)}")
        for event in self.events:
            print(f"Evento pendiente: {event.type} para el cliente {event.client.id} a las {event.time:.2f} minutos")