class Simulation:

    def __init__(self):

        # Current simulation clock
        self.current_time = 0

        # Event list
        self.event_list = []

        # Counters
        self.driver_count = 0
        self.rider_count = 0

        # Lists to store system state
        self.idle_drivers = []
        self.waiting_riders = []

        # Track driver and rider locations
        self.driver_locations = {}
        self.rider_locations = {}

        # Performance statistics
        self.total_abandonments = 0

        # Distribution functions (arrival, trip, patience)
        self.distributions = {}

        # Event handlers dictionary
        self.event_handlers = {}