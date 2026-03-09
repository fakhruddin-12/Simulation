import config


class Simulation:
    def __init__(self, handlers, distributions):
        # connect handlers and distributions
        self.handlers = handlers
        self.distributions = distributions

        # simulation clock
        self.current_time = 0.0
        self.simulation_length = config.SIMULATION_LENGTH

        # event list: (time, event_type, event_data)
        self.event_list = []

        # counters for ids
        self.driver_count = 0
        self.rider_count = 0

        # store driver and rider objects
        self.drivers = {}
        self.riders = {}

        # current system state
        self.idle_drivers = []
        self.waiting_riders = []

        # ride statistics / KPIs
        self.total_drivers_arrived = 0
        self.total_riders_arrived = 0
        self.completed_rides = 0
        self.total_abandonments = 0

        self.total_wait_time = 0.0
        self.total_trip_time = 0.0
        self.total_system_time = 0.0
        self.total_pickup_time = 0.0

        # time-average stats
        self.area_waiting_riders = 0.0
        self.area_idle_drivers = 0.0
        self.last_event_time = 0.0

        # Driver availability tracking
        # if a driver wants to go offline while busy, mark it here
        self.driver_offline_flags = set()

        # event dispatch
        self.event_handlers = {
            "driver_arrival": self.handlers.handle_driver_arrival,
            "driver_offline": self.handlers.handle_driver_offline,
            "rider_arrival": self.handlers.handle_rider_arrival,
            "rider_abandonment": self.handlers.handle_rider_abandonment,
            "pickup_complete": self.handlers.handle_pickup_complete,
            "dropoff_complete": self.handlers.handle_dropoff_complete,
            "termination": self.handlers.handle_termination,
        }

    def add_event(self, time, event_type, event_data=None):
        self.event_list.append((time, event_type, event_data))
        self.event_list.sort(key=lambda x: x[0])

    def update_time_average_stats(self, new_time):
        dt = new_time - self.last_event_time
        self.area_waiting_riders += len(self.waiting_riders) * dt
        self.area_idle_drivers += len(self.idle_drivers) * dt
        self.last_event_time = new_time

    def progress_time(self):
        if not self.event_list:
            return False

        time, event_type, event_data = self.event_list.pop(0)

        self.update_time_average_stats(time)
        self.current_time = time

        self.event_handlers[event_type](event_data)

        if event_type == "termination":
            return False

        return True

    def run(self):
        # initial events
        self.add_event(0, "driver_arrival", None)
        self.add_event(0, "rider_arrival", None)
        self.add_event(self.simulation_length, "termination", None)

        while self.progress_time():
            pass
