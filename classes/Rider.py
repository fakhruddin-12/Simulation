import random

#class Rider:
    
    #def __init__(self , rider_id , request_time , pickup_location , dropoff_location , patience):
        #self.rider_id = rider_id
        #self.request_time = request_time
        #self.pickup_location = pickup_location
        #self.dropoff_location = dropoff_location
        #self.patience_lambda = patience_lambda
        #self.patience = patience      #changed by MANSI
        
        #self.patience = random.expovariate(self.patience_lambda)
        #self.deadline = self.request_time + self.patience
        #self.deadline = request_time + patience        #changed by MANSI
        
        #self.matched = False
        #self.driver_id = None
        #self.pickup_time = None
        #self.dropoff_time = None

# ===== NEW CODE =====

class Rider:
    def __init__(self, rider_id, request_time, pickup_location, dropoff_location, patience):
        self.rider_id = rider_id
        self.request_time = request_time
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location
        self.patience = patience
        self.deadline = request_time + patience

        # waiting, matched, in_trip, completed, abandoned
        self.status = "waiting"

        self.driver_id = None

        # event times
        self.match_time = None
        self.pickup_time = None
        self.dropoff_time = None

        # rider metrics
        self.match_delay = None
        self.pickup_delay = None
        self.wait_time = None
        self.trip_time = None
        self.system_time = None

        # rider metrics
        self.wait_time = None
        self.trip_time = None
        self.system_time = None

