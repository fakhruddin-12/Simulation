import random
import math


class Distributions:

    def __init__(self, simulation):
        self.simulation = simulation


    # Rider arrival process
    def rider_arrival(self):

        rate = 30
        return random.expovariate(rate)

    # Driver arrival process
    def driver_arrival(self):

        rate = 3
        return random.expovariate(rate)


    # Rider patience
    def rider_patience(self):

        rate = 5
        return random.expovariate(rate)

    # Driver availability duration
    def driver_availability(self):

        return random.uniform(5, 8)


    # Generate random location in Squareshire
    # City is 20 x 20 miles
    def random_location(self):

        x = random.uniform(0, 20)
        y = random.uniform(0, 20)

        return (x, y)


    # Actual trip time distribution
    def travel_time(self, loc1, loc2):
	
	#Euclidean distance
        d = math.sqrt(
            (loc1[0] - loc2[0])**2 +
            (loc1[1] - loc2[1])**2)

        mu = d / 20

        return random.uniform(0.8 * mu, 1.2 * mu)