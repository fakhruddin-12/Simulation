class Simulation:

    def __init__(self, handlers, distributions):

        # connect handlers and distributions
        self.handlers = handlers
        self.distributions = distributions

        # Current simulation clock
        self.current_time = 0

        # Event list
        self.event_list = []

        # Counters
        self.driver_count = 0
        self.rider_count = 0

        # store driver and rider objects
        self.drivers = {}
        self.riders = {}

        # Lists to store system state
        self.idle_drivers = []
        self.waiting_riders = []

        # ride statistics
        self.completed_rides = 0
        self.total_wait_time = 0
        self.total_trip_time = 0
        # Performance statistics
        self.total_abandonments = 0

        # Driver availability tracking
        self.driver_offline_flags = {}

    # Add event to event list
    def add_event(self, time, event_type, event_data):

        # add event tuple
        self.event_list.append((time, event_type, event_data))

        # keep events sorted by time
        self.event_list.sort(key=lambda x: x[0])

    # Simulation run loop
    def run(self):

        # schedule initial events
        self.add_event(0, "driver_arrival", None)
        self.add_event(0, "rider_arrival", None)

        # simulation end time
        self.add_event(720, "termination", None)

        # main simulation loop
        while self.event_list:

            # get next event
            time, event_type, event_data = self.event_list.pop(0)

            # advance simulation clock
            self.current_time = time

            # call corresponding handler
            if event_type == "driver_arrival":
                self.handlers.handle_driver_arrival(event_data)

            elif event_type == "driver_offline":
                self.handlers.handle_driver_offline(event_data)

            elif event_type == "rider_arrival":
                self.handlers.handle_rider_arrival(event_data)

            elif event_type == "rider_abandonment":
                self.handlers.handle_rider_abandonment(event_data)

            elif event_type == "pickup_complete":
                self.handlers.handle_pickup_complete(event_data)

            elif event_type == "dropoff_complete":
                self.handlers.handle_dropoff_complete(event_data)

            elif event_type == "termination":
                self.handlers.handle_termination(event_data)
                break
