import random
import math

# Rider interarrival time
def rider_arrival():
    rate = 30  # riders per hour
    return random.expovariate(rate)
    
# Driver interarrival time 
def driver_arrival():
    rate = 3  # drivers per hour
    return random.expovariate(rate)
    
# Rider patience
def rider_patience():
    rate = 5
    return random.expovariate(rate)

# Driver availability duration
def driver_availability():
    return random.uniform(5, 8)

# Generate random location in Squareshire
def random_location():
    x = random.uniform(0, 20)
    y = random.uniform(0, 20)
    return (x, y)

# Actual trip time between two locations
def travel_time(loc1, loc2):
    d = math.sqrt(
        (loc1[0] - loc2[0])**2 +
        (loc1[1] - loc2[1])**2
    )
    speed = 20

    # expected travel time
    mu = d / speed

    # actual trip time distributed as
    return random.uniform(0.8 * mu, 1.2 * mu)