# ======================================
# SIMULATION CONFIGURATION PARAMETERS
# ======================================

# simulation horizon
SIMULATION_LENGTH = 720   # minutes (12 hours)

# rider arrival rate (Poisson)
RIDER_INTERARRIVAL_RATE = 30

# driver arrival rate
DRIVER_INTERARRIVAL_RATE = 3

# rider patience distribution
RIDER_PATIENCE_RATE = 5

# driver availability window
DRIVER_AVAILABILITY_MIN = 5
DRIVER_AVAILABILITY_MAX = 8

# average travel speed (distance units per minute)
AVERAGE_SPEED = 20

# map boundaries
MAP_X_MIN = 0
MAP_X_MAX = 20
MAP_Y_MIN = 0
MAP_Y_MAX = 20