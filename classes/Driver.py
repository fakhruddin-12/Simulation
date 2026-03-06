import random

class Driver:
    
    def __init__(self , driver_id , location , entry_time , offline_start , offline_end):
        self.driver_id = driver_id
        self.location = location
        self.entry_time = entry_time
        self.offline_start = offline_start
        self.offline_end = offline_end
        
        self.available = True
        self.offline_time = self.entry_time + random.uniform(self.offline_start , self.offline_end)
