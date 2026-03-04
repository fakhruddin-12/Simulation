class Driver:
    
    def __init__(self , driver_id , location , available = True , available_time = 0.0):
        self.driver_id = driver_id
        self.location = location
        self.available = available
        self.available_time = available_time
        self.current_trip_id = None