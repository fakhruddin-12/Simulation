from modules import generate_random as gr

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

        # driver and rider locations
        self.driver_locations = {}
        self.rider_locations = {}
        self.rider_destinations = {}
        
        # Performance statistics
        self.total_abandonments = 0

        # Event handlers dictionary
        self.event_handlers = {}

        # Driver availability tracking
        self.driver_offline_flags = {}

        # Random Distributions
        self.distributions = {
            "driver-arrival": gr.driver_arrival,
            "rider-arrival": gr.rider_arrival,
            "patience": gr.rider_patience,
            "driver-availability": gr.driver_availability
        }

        # Event handlers dictionary
        self.event_handlers = {}
