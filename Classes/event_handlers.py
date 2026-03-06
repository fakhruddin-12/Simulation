from typing import Any
import modules.handler_functions as hf

class EventHandlers:
    def __init__(self, simulation):
        self.simulation = simulation
        
    def handle_driver_arrival(self, event_data: Any):
        hf.execute_driver_arrival(self.simulation)

    def handle_rider_arrival(self, event_data: Any):
        hf.execute_rider_arrival(self.simulation)

    def handle_rider_abandonment(self, event_data: Any):
        hf.execute_rider_abandonment(self.simulation, event_data)

    def handle_pickup_complete(self, event_data: Any):
        hf.execute_pickup_complete(self.simulation, event_data)

    def handle_dropoff_complete(self, event_data: Any):
        hf.execute_dropoff_complete(self.simulation, event_data)

    def handle_termination(self, event_data: Any):
        hf.execute_termination(self.simulation)