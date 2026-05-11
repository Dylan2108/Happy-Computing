class Client:
    def __init__(self,client_id,arrival_time,service_type):
        self.id = client_id
        self.arrival_time = arrival_time
        self.service_type = service_type

        self.seller_initial_time = None
        self.seller_final_time = None

        self.technical_initial_time = None
        self.technical_final_time = None