from classes.simulation import Simulation
import random
import math

# 1.driver arrival
def execute_driver_arrival(sim: Simulation):
    # Create new driver
    sim.driver_count += 1
    driver_id = sim.driver_count

    # Assign random starting location
    location = (random.uniform(0, 20), random.uniform(0, 20))
    sim.driver_locations[driver_id] = location

    # Driver becomes idle initially
    sim.idle_drivers.append(driver_id)

    # Schedule next driver arrival
    next_arrival = sim.current_time + sim.distributions["driver-arrival"]()

    sim.add_event(next_arrival, "driver_arrival", None)

# 2.rider arrival
def execute_rider_arrival(sim: Simulation):

    # Create new rider
    sim.rider_count += 1
    rider_id = sim.rider_count

    # Generate rider pickup location
    location = (random.uniform(0, 20), random.uniform(0, 20))
    sim.rider_locations[rider_id] = location

    # If a driver is available, match immediately
    if len(sim.idle_drivers) > 0:

        driver = find_closest_driver(sim, rider_id)
        sim.idle_drivers.remove(driver)

        pickup_time = sim.current_time + sim.distributions["pickup"]()

        sim.add_event(
            pickup_time,
            "pickup_complete",
            {"driver": driver, "rider": rider_id}
        )

    else:
        # Rider waits if no drivers available
        sim.waiting_riders.append(rider_id)

        patience_time = sim.current_time + sim.distributions["patience"]()

        sim.add_event(
            patience_time,
            "rider_abandonment",
            {"rider": rider_id}
        )

    # Schedule next rider arrival
    next_arrival = sim.current_time + sim.distributions["rider-arrival"]()

    sim.add_event(next_arrival, "rider_arrival", None)

# 3. rider abandonment
def execute_rider_abandonment(sim: Simulation, event_data):

    rider = event_data["rider"]

    # Only abandon if still waiting
    if rider in sim.waiting_riders:

        sim.waiting_riders.remove(rider)

        sim.total_abandonments += 1

# 4. pickup completion
def execute_pickup_complete(sim: Simulation, event_data):

    driver = event_data["driver"]
    rider = event_data["rider"]

    # Generate trip duration
    trip_time = sim.distributions["trip"]()

    dropoff_time = sim.current_time + trip_time

    sim.add_event(
        dropoff_time,
        "dropoff_complete",
        {"driver": driver, "rider": rider}
    )

# 5. dropoff completion
def execute_dropoff_complete(sim: Simulation, event_data):

    driver = event_data["driver"]
    rider = event_data["rider"]

    # Update driver location to rider drop-off
    sim.driver_locations[driver] = sim.rider_locations[rider]

    # If riders are waiting, serve next rider
    if len(sim.waiting_riders) > 0:

        next_rider = sim.waiting_riders.pop(0)

        pickup_time = sim.current_time + sim.distributions["pickup"]()

        sim.add_event(
            pickup_time,
            "pickup_complete",
            {"driver": driver, "rider": next_rider}
        )

    else:
        # Otherwise driver becomes idle
        sim.idle_drivers.append(driver)

# 6. terminate simulation and calculate summary statistics
def execute_termination(sim: Simulation):

    served = sim.rider_count - sim.total_abandonments

    print("Simulation finished")
    print("Riders served:", served)
    print("Rider abandonments:", sim.total_abandonments)

# 7. To compute Euclidean distance between two locations
def distance(loc1, loc2):

    return math.sqrt(
        (loc1[0] - loc2[0])**2 +
        (loc1[1] - loc2[1])**2
    )

# 8. To find closest idle driver to a rider
def find_closest_driver(sim: Simulation, rider_id: int):

    rider_location = sim.rider_locations[rider_id]

    closest_driver = None
    min_distance = float("inf")

    for driver in sim.idle_drivers:

        driver_location = sim.driver_locations[driver]

        d = distance(rider_location, driver_location)

        if d < min_distance:
            min_distance = d
            closest_driver = driver

    return closest_driver