import math
from classes import config


def record_abandonment(sim):
    sim.total_abandonments += 1


def calculate_fare(sim, rider):
    distance = sim.distributions.distance(rider.pickup_location, rider.dropoff_location)
    trip_time = rider.trip_time
    fare = (
        config.BASE_FARE
        + config.DISTANCE_FARE * distance
        + config.TIME_FARE * trip_time
    )
    return fare


def record_completed_ride(sim, rider, driver, pickup_travel_time):
    rider.match_delay = rider.match_time - rider.request_time
    rider.pickup_delay = rider.pickup_time - rider.match_time
    rider.wait_time = rider.pickup_time - rider.request_time
    rider.trip_time = rider.dropoff_time - rider.pickup_time
    rider.system_time = rider.dropoff_time - rider.request_time

    sim.completed_rides += 1
    sim.total_match_delay += rider.match_delay
    sim.total_pickup_delay += rider.pickup_delay
    sim.total_wait_time += rider.wait_time
    sim.total_trip_time += rider.trip_time
    sim.total_system_time += rider.system_time

    driver.completed_trips += 1
    driver.total_pickup_time += pickup_travel_time
    driver.total_trip_time += rider.trip_time
    driver.total_busy_time += pickup_travel_time + rider.trip_time

    fare = calculate_fare(sim, rider)
    driver.total_earnings += fare


def finalize_driver_exit(driver, exit_time):
    driver.exit_time = exit_time
    driver.online_time = max(driver.exit_time - driver.entry_time, 0.0)

    if driver.online_time > 0:
        driver.earning_rate = driver.total_earnings / driver.online_time
        driver.utilization = driver.total_busy_time / driver.online_time
    else:
        driver.earning_rate = 0.0
        driver.utilization = 0.0


def finalize_all_active_drivers(sim):
    active_driver_ids = list(sim.drivers.keys())

    for driver_id in active_driver_ids:
        driver = sim.drivers[driver_id]

        if driver.status == "idle" and driver_id in sim.idle_drivers:
            sim.idle_drivers.remove(driver_id)

        driver.status = "offline"
        finalize_driver_exit(driver, sim.current_time)
        sim.exited_drivers.append(driver)
        del sim.drivers[driver_id]


def safe_mean(values):
    return sum(values) / len(values) if values else 0.0


def sample_std(values):
    n = len(values)
    if n < 2:
        return 0.0
    m = safe_mean(values)
    var = sum((x - m) ** 2 for x in values) / (n - 1)
    return math.sqrt(var)


def coefficient_of_variation(values):
    m = safe_mean(values)
    if m == 0:
        return 0.0
    return sample_std(values) / m


def gini(values):
    values = [v for v in values if v >= 0]
    n = len(values)
    if n == 0:
        return 0.0

    mean_val = safe_mean(values)
    if mean_val == 0:
        return 0.0

    total_abs_diff = 0.0
    for x in values:
        for y in values:
            total_abs_diff += abs(x - y)

    return total_abs_diff / (2 * n * n * mean_val)


def get_driver_earning_rates(sim):
    rates = []
    for driver in sim.exited_drivers:
        if driver.online_time is not None and driver.online_time >= config.MIN_ONLINE_TIME_FOR_FAIRNESS:
            rates.append(driver.earning_rate)
    return rates


def get_driver_utilizations(sim):
    utils = []
    for driver in sim.exited_drivers:
        if driver.online_time is not None and driver.online_time >= config.MIN_ONLINE_TIME_FOR_FAIRNESS:
            utils.append(driver.utilization)
    return utils


def get_kpis(sim):
    served = sim.completed_rides
    total_riders = sim.total_riders_arrived

    earning_rates = get_driver_earning_rates(sim)
    utilizations = get_driver_utilizations(sim)

    avg_match_delay = sim.total_match_delay / served if served > 0 else 0.0
    avg_pickup_delay = sim.total_pickup_delay / served if served > 0 else 0.0
    avg_wait_time = sim.total_wait_time / served if served > 0 else 0.0
    avg_trip_time = sim.total_trip_time / served if served > 0 else 0.0
    avg_system_time = sim.total_system_time / served if served > 0 else 0.0
    abandonment_rate = sim.total_abandonments / total_riders if total_riders > 0 else 0.0

    return {
        "completed_rides": sim.completed_rides,
        "abandonments": sim.total_abandonments,
        "abandonment_rate": abandonment_rate,
        "avg_match_delay": avg_match_delay,
        "avg_pickup_delay": avg_pickup_delay,
        "avg_wait_time": avg_wait_time,
        "avg_trip_time": avg_trip_time,
        "avg_system_time": avg_system_time,
        "avg_waiting_riders": sim.area_waiting_riders / sim.simulation_length if sim.simulation_length > 0 else 0.0,
        "avg_idle_drivers": sim.area_idle_drivers / sim.simulation_length if sim.simulation_length > 0 else 0.0,
        "avg_driver_earning_rate": safe_mean(earning_rates),
        "std_driver_earning_rate": sample_std(earning_rates),
        "cv_driver_earning_rate": coefficient_of_variation(earning_rates),
        "gini_driver_earning_rate": gini(earning_rates),
        "avg_driver_utilization": safe_mean(utilizations),
        "std_driver_utilization": sample_std(utilizations),
        "cv_driver_utilization": coefficient_of_variation(utilizations),
        "gini_driver_utilization": gini(utilizations),
        "total_riders_arrived": sim.total_riders_arrived,
        "total_drivers_arrived": sim.total_drivers_arrived,
        "num_drivers_for_fairness": len(earning_rates),
    }


def print_summary(sim):
    kpis = get_kpis(sim)
    print("Simulation finished")
    for key, value in kpis.items():

        print(f"{key}: {value}")
