import random

#class Driver:
    
    #def __init__(self , driver_id , location , entry_time , offline_time):
        #self.driver_id = driver_id
        #self.location = location
        #self.entry_time = entry_time
        
        #self.offline_start = offline_start  #old code
        #self.offline_end = offline_end    #old code
        
        #self.offline_time = offline_time   # time driver leaves system, changed by MANSI
        
        #self.offline_time = self.entry_time + random.uniform(self.offline_start , self.offline_end)    #old code

        # driver availability status
        #self.available = True

        # performance metrics
        #self.earnings = 0.0
        #self.completed_trips = 0
        #self.total_busy_time = 0.0

# ===== NEW CODE =====

class Driver:
    def __init__(self, driver_id, location, entry_time, offline_time):
        self.driver_id = driver_id
        self.location = location
        self.entry_time = entry_time
        self.offline_time = offline_time

        # idle, pickup, trip, offline
        self.status = "idle"

        self.assigned_rider = None

        # driver metrics
        self.completed_trips = 0
        self.total_pickup_time = 0.0
        self.total_trip_time = 0.0
        self.total_busy_time = 0.0
        self.total_earnings = 0.0

        # true exit time from the system
        self.exit_time = None
        self.online_time = None

        # derived metrics
        self.earning_rate = None
        self.utilization = None

        self.last_state_change_time = entry_time
        # useful for tracking state transitions
        self.last_state_change_time = entry_time



