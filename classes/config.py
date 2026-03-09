# =========================
# TIME UNITS: MINUTES
# DISTANCE UNITS: arbitrary map units
# =========================

SIMULATION_LENGTH = 720.0   # 12 hours

# Mean interarrival / patience values
MEAN_RIDER_INTERARRIVAL = 2.0
MEAN_DRIVER_INTERARRIVAL = 5.0
MEAN_RIDER_PATIENCE = 10.0

# Driver online duration
DRIVER_AVAILABILITY_MIN = 300.0
DRIVER_AVAILABILITY_MAX = 480.0

# Map settings
MAP_X_MIN = 0.0
MAP_X_MAX = 20.0
MAP_Y_MIN = 0.0
MAP_Y_MAX = 20.0

# Travel speed: distance units per minute
AVERAGE_SPEED = 0.4

# Fare model
BASE_FARE = 2.0
DISTANCE_FARE = 1.5
TIME_FARE = 0.2

# Fairness handling
MIN_ONLINE_TIME_FOR_FAIRNESS = 1.0

# Confidence interval
CI_Z_VALUE = 1.96
