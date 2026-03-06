from classes.simulation import Simulation
from classes.generate_random import Distributions
from classes.event_handlers import EventHandlers


def main():

    # create objects
    handlers = EventHandlers(None)
    distributions = Distributions(None)

    # create simulation
    sim = Simulation(handlers, distributions)

    # link objects back to simulation
    handlers.simulation = sim
    distributions.simulation = sim

    # start simulation
    sim.run()


if __name__ == "__main__":
    main()