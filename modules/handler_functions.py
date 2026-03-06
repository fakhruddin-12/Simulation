from classes.simulation import Simulation
from modules import generate_random as gr
import math

# To compute Euclidean distance between two locations
def distance(loc1, loc2):

    return math.sqrt(
        (loc1[0] - loc2[0])**2 +
        (loc1[1] - loc2[1])**2)

# To find closest idle driver to a rider
def find_closest_driver(sim: Simulation, rider_id: int):

    rider_location = sim.rider_locations[rider_id]
    closest_driver = None    #initialize no close driver
    min_distance = float("inf")    #initialize max distance
    
    if not sim.idle_drivers:
        return None
    
    for driver in sim.idle_drivers:

        driver_location = sim.driver_locations[driver]
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

    # driver available for
    availability = sim.distributions["driver-availability"]()
    offline_time = sim.current_time + availability
    #schedule driver offline event
    sim.add_event(offline_time,"driver_offline",{"driver": driver_id})

    # generate driver location using module
    location = gr.random_location()
    
    sim.driver_locations[driver_id] = location

    # Driver becomes idle initially
    sim.idle_drivers.append(driver_id)

    # Schedule next driver arrival
    next_arrival = sim.current_time + sim.distributions["driver-arrival"]()
    sim.add_event(next_arrival, "driver_arrival", None)

# 2.driver goes offline
def execute_driver_offline(sim: Simulation, event_data):

    driver = event_data["driver"]

    # Case 1: driver is currently idle
    # remove from the idle driver list immediately
    if driver in sim.idle_drivers:
        sim.idle_drivers.remove(driver)

        # or remove their location record
        if driver in sim.driver_locations:
            del sim.driver_locations[driver]

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
    location = gr.random_location()
    sim.rider_locations[rider_id] = location

    # If a driver is available, match immediately
    if len(sim.idle_drivers) > 0:
        driver = find_closest_driver(sim, rider_id)

        # matched driver so, now becomes busy, remove from idle list
        sim.idle_drivers.remove(driver)

        # generate pickup travel time
        driver_location = sim.driver_locations[driver]
        rider_location = sim.rider_locations[rider_id]
        pickup_time = sim.current_time + gr.travel_time(driver_location, rider_location)

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
        patience_time = sim.current_time + sim.distributions["patience"]()

        # Schedule abandonment event
        sim.add_event(
            patience_time,
            "rider_abandonment",
            {"rider": rider_id}
        )

    # Schedule next rider arrival
    next_arrival = sim.current_time + sim.distributions["rider-arrival"]()
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

    origin = sim.rider_locations[rider]
    destination = gr.random_location()

    # Generate trip duration and find dropoff time
    sim.rider_destinations[rider] = destination       # store destination
    trip_time = gr.travel_time(origin, destination)
    
    dropoff_time = sim.current_time + trip_time
    
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

    # get rider destination
    destination = sim.rider_destinations[rider]

    # update driver location to rider destination
    sim.driver_locations[driver] = destination

    # check if driver should go offline after trip
    if sim.driver_offline_flags.get(driver, False):

        # remove driver location record
        if driver in sim.driver_locations:
            del sim.driver_locations[driver]
        return
    # if riders are waiting, serve next rider
    if len(sim.waiting_riders) > 0:
        next_rider = sim.waiting_riders.pop(0)
        driver_location = sim.driver_locations[driver]
        rider_location = sim.rider_locations[next_rider]

        pickup_time = sim.current_time + gr.travel_time(driver_location, rider_location)

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
