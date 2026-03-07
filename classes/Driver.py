import random

class Driver:
    
    def __init__(self , driver_id , location , entry_time , offline_time):
        self.driver_id = driver_id
        self.location = location
        self.entry_time = entry_time
        
        #self.offline_start = offline_start  #old code
        #self.offline_end = offline_end    #old code
        
        self.offline_time = offline_time   # time driver leaves system, changed by MANSI
        
        #self.offline_time = self.entry_time + random.uniform(self.offline_start , self.offline_end)    #old code

        # driver availability status
        self.available = True

