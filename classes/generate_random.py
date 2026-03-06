import random
import math

class Distributions:

    def __init__(self, simulation):
        self.simulation = simulation
        # setting model parameters
        self.rider_arrival_rate = 30
        self.driver_arrival_rate = 3
        self.patience_rate = 5
        self.driver_availability_min = 5
        self.driver_availability_max = 8

    # Rider arrival process
    def rider_arrival(self):
        return random.expovariate(self.rider_arrival_rate)

    # Driver arrival process
    def driver_arrival(self):
        return random.expovariate(self.driver_arrival_rate)

    # Rider patience
    def rider_patience(self):
        return random.expovariate(self.patience_rate)

    # Driver availability duration
    def driver_availability(self):
        return random.uniform(self.driver_availability_min, self.driver_availability_max)

    # Generate random location in Squareshire 20 X 20 miles
    def random_location(self):
        x = random.uniform(0, 20)
        y = random.uniform(0, 20)
        return (x, y)
    
    # Expected travel time basis average speed
    def expected_travel_time(self, loc1, loc2):
        # Euclidean distance
        d = math.sqrt( (loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)
        return d / 20
    
    # Actual trip time distribution
    def travel_time(self, loc1, loc2):
        mu = self.expected_travel_time(loc1, loc2)
        return random.uniform(0.8*mu, 1.2*mu)
