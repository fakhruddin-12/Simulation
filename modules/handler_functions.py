from classes.simulation import Simulation
from classes.driver import Driver         
from classes.rider import Rider            
import math

# To compute Euclidean distance between two locations
def distance(loc1, loc2):
    return math.sqrt(
        (loc1[0] - loc2[0])**2 +
        (loc1[1] - loc2[1])**2)
    
# To find closest idle driver to a rider
def find_closest_driver(sim: Simulation, rider_id: int):

    # get rider pickup location from rider object
    rider_location = sim.riders[rider_id].pickup_location     # <<< CHANGED

    closest_driver = None    #initialize no close driver
    min_distance = float("inf")    #initialize max distance
    
    if not sim.idle_drivers:
        return None
    
    for driver in sim.idle_drivers:

        # get driver location from driver object
        driver_location = sim.drivers[driver].location         # <<< CHANGED

        d = distance(rider_location, driver_location)

        if d < min_distance:
            min_distance = d
            closest_driver = driver

    return closest_driver
    

# 1.driver arrival
def execute_driver_arrival(sim: Simulation):

    # Create new driver
    sim.driver_count += 1
    driver_id = sim.driver_count

    # generate driver location using distributions
    location = sim.distributions.random_location()

    # driver available for
    availability = sim.distributions.driver_availability()
    offline_time = sim.current_time + availability

    # create driver object to store driver state
    driver = Driver(   # <<< NEW
    driver_id,
    location,
    sim.current_time,
    offline_time)

    # store driver object
    sim.drivers[driver_id] = driver                # <<< NEW

    #schedule driver offline event
    sim.add_event(
        offline_time,
        "driver_offline",
        {"driver": driver_id})

    # Driver becomes idle initially
    sim.idle_drivers.append(driver_id)

    # Schedule next driver arrival
    next_arrival = sim.current_time + sim.distributions.driver_arrival()

    sim.add_event(next_arrival, "driver_arrival", None)


# 2.driver goes offline
def execute_driver_offline(sim: Simulation, event_data):

    driver = event_data["driver"]

    # Case 1: driver is currently idle
    # remove from the idle driver list immediately
    if driver in sim.idle_drivers:

        sim.idle_drivers.remove(driver)

        # remove driver object if leaving system
        if driver in sim.drivers:                   # <<< CHANGED
            del sim.drivers[driver]                 # <<< CHANGED

    else:
        # Case 2: driver is currently finishing a ride
        # flag that the driver should leave after finishing the trip
        sim.driver_offline_flags[driver] = True


# 3.rider arrival
def execute_rider_arrival(sim: Simulation):

    # Create new rider
    sim.rider_count += 1
    rider_id = sim.rider_count

    # Generate rider pickup location
    pickup_location = sim.distributions.random_location()

    # generate dropoff location
    dropoff_location = sim.distributions.random_location()     # <<< NEW

    # create rider object
    patience = sim.distributions.rider_patience()
    rider = Rider(                     # <<< NEW
        rider_id,
        sim.current_time,
        pickup_location,
        dropoff_location,
        patience)

    # store rider object
    sim.riders[rider_id] = rider                               # <<< NEW

    # If a driver is available, match immediately
    if len(sim.idle_drivers) > 0:

        driver = find_closest_driver(sim, rider_id)

        # matched driver so, now becomes busy, remove from idle list
        sim.idle_drivers.remove(driver)

        # generate pickup travel time
        driver_location = sim.drivers[driver].location         # <<< CHANGED
        rider_location = rider.pickup_location                 # <<< CHANGED

        pickup_time = sim.current_time + sim.distributions.travel_time(
            driver_location,
            rider_location
        )

        # Schedule pickup completion event
        sim.add_event(
            pickup_time,
            "pickup_complete",
            {"driver": driver, "rider": rider_id}
        )

    else:
        # Rider waits if no drivers available
        sim.waiting_riders.append(rider_id)

        # Generate patience time
        patience_time = rider.deadline                         # <<< CHANGED

        # Schedule abandonment event
        sim.add_event(
            patience_time,
            "rider_abandonment",
            {"rider": rider_id}
        )

    # Schedule next rider arrival
    next_arrival = sim.current_time + sim.distributions.rider_arrival()

    sim.add_event(next_arrival, "rider_arrival", None)


# 4.rider abandonment
def execute_rider_abandonment(sim: Simulation, event_data):

    rider = event_data["rider"]

    # Only abandon if still waiting
    if rider in sim.waiting_riders:

        # Remove rider from queue
        sim.waiting_riders.remove(rider)

        # update abandonment counter
        sim.total_abandonments += 1


# 5.pickup completion
def execute_pickup_complete(sim: Simulation, event_data):

    driver = event_data["driver"]
    rider = event_data["rider"]

    # get rider object
    rider_obj = sim.riders[rider]                          # <<< NEW

    # origin is pickup location
    origin = rider_obj.pickup_location                     # <<< CHANGED

    # destination is dropoff location
    destination = rider_obj.dropoff_location               # <<< CHANGED

    # Generate trip duration and find dropoff time
    trip_time = sim.distributions.travel_time(origin, destination)

    dropoff_time = sim.current_time + trip_time

    # record pickup time and driver match
    rider_obj.pickup_time = sim.current_time               # <<< NEW
    rider_obj.driver_id = driver                           # <<< NEW
    
    # Schedule drop-off completion
    sim.add_event(
        dropoff_time,
        "dropoff_complete",
        {"driver": driver, "rider": rider}
    )


# 6.dropoff completion
def execute_dropoff_complete(sim: Simulation, event_data):

    driver = event_data["driver"]
    rider = event_data["rider"]

    rider_obj = sim.riders[rider]                          # <<< NEW

    # get rider destination
    destination = rider_obj.dropoff_location               # <<< CHANGED

    # update driver location to rider destination
    sim.drivers[driver].location = destination             # <<< CHANGED

    # record dropoff time
    rider_obj.dropoff_time = sim.current_time              # <<< NEW

    # check if driver should go offline after trip
    if sim.driver_offline_flags.get(driver, False):

        if driver in sim.drivers:
            del sim.drivers[driver]

        return

    # if riders are waiting, serve next rider
    if len(sim.waiting_riders) > 0:

        next_rider = sim.waiting_riders.pop(0)

        driver_location = sim.drivers[driver].location     # <<< CHANGED
        rider_location = sim.riders[next_rider].pickup_location   # <<< CHANGED

        pickup_time = sim.current_time + sim.distributions.travel_time(
            driver_location,
            rider_location
        )

        sim.add_event(
            pickup_time,
            "pickup_complete",
            {"driver": driver, "rider": next_rider}
        )

    # otherwise driver becomes idle
    else:
        sim.idle_drivers.append(driver)


# 7.terminate simulation and calculate summary statistics
def execute_termination(sim: Simulation):

    served = sim.rider_count - sim.total_abandonments

    print("Simulation finished")
    print("Riders served:", served)
    print("Rider abandonments:", sim.total_abandonments)
