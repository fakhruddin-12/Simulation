class Rider:
    
    def __init__(self , rider_id , request_time , pickup_location , dropoff_location):
        self.rider_id = rider_id
        self.request_time = request_time
        self.pickup_location = pickup_location
        self.dropoff_location = dropoff_location

        self.matched = False
        self.driver_id = None
        self.pickup_time = None
        self.dropoff_time = None
