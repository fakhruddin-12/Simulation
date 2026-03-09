#class Distributions:

    #def __init__( self, simulation, rider_interarrival_rate=30, driver_interarrival_rate=3,patience_rate=5,driver_availability_min=5,driver_availability_max=8):
        #self.simulation = simulation
        #self.rider_interarrival_rate = rider_interarrival_rate
        #self.driver_interarrival_rate = driver_interarrival_rate
        #self.patience_rate = patience_rate
        #self.driver_availability_min = driver_availability_min
        #self.driver_availability_max = driver_availability_max

    # Rider arrival process
    #def rider_arrival(self):
        #return random.expovariate(self.rider_interarrival_rate)

    # Driver arrival process
    #def driver_arrival(self):
        #return random.expovariate(self.driver_interarrival_rate)

    # Rider patience
    #def rider_patience(self):
        #return random.expovariate(self.patience_rate)

    # Driver availability duration
    #def driver_availability(self):
        #return random.uniform(self.driver_availability_min, self.driver_availability_max)

    # Generate random location in Squareshire 20 X 20 miles
    #def random_location(self):
        #x = random.uniform(0, 20)
        #y = random.uniform(0, 20)
        #return (x, y)
    
    # Actual trip time distribution
    #def travel_time(self, loc1, loc2):
        # Euclidean distance
        #d = math.sqrt( (loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)    
        #mu = d / 20    #average speed assumed
        #return random.uniform(0.8*mu, 1.2*mu)


# ===== NEW CODE =====
import random
import math
import config


class Distributions:
    def __init__(self, simulation):
        self.simulation = simulation

    def rider_interarrival(self):
        return random.expovariate(1.0 / config.MEAN_RIDER_INTERARRIVAL)

    def driver_interarrival(self):
        return random.expovariate(1.0 / config.MEAN_DRIVER_INTERARRIVAL)

    def rider_patience(self):
        return random.expovariate(1.0 / config.MEAN_RIDER_PATIENCE)

    def driver_availability(self):
        return random.uniform(
            config.DRIVER_AVAILABILITY_MIN,
            config.DRIVER_AVAILABILITY_MAX
        )

    def random_location(self):
        x = random.uniform(config.MAP_X_MIN, config.MAP_X_MAX)
        y = random.uniform(config.MAP_Y_MIN, config.MAP_Y_MAX)
        return (x, y)

    def distance(self, loc1, loc2):
        return math.sqrt(
            (loc1[0] - loc2[0]) ** 2 +
            (loc1[1] - loc2[1]) ** 2
        )

    def travel_time(self, loc1, loc2):
        d = self.distance(loc1, loc2)
        mean_time = d / config.AVERAGE_SPEED
        return random.uniform(0.8 * mean_time, 1.2 * mean_time)

        mu = d / config.AVERAGE_SPEED

        return random.uniform(0.8 * mu, 1.2 * mu)
