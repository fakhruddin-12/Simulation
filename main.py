from classes.simulation import Simulation
from classes.event_handlers import EventHandlers
from classes.generate_random import Distributions


def main():

    # create handler and distribution objects first
    handlers = EventHandlers(None)
    distributions = Distributions(None)

    # create simulation object
    sim = Simulation(handlers, distributions)

    # connect handlers and distributions back to simulation
    handlers.simulation = sim
    distributions.simulation = sim

    # run the simulation
    sim.run()


if __name__ == "__main__":
    main()