import os
import random
import math
import matplotlib.pyplot as plt

from classes import config
from classes.simulation import Simulation
from classes.generate_random import Distributions
from classes.event_handlers import EventHandlers
from modules import metrics


OUTPUT_DIR = "plots"


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_one_simulation(seed=None):

    if seed is not None:
        random.seed(seed)

    handlers = EventHandlers(None)
    distributions = Distributions(None)
    sim = Simulation(handlers, distributions)

    handlers.simulation = sim
    distributions.simulation = sim

    sim.run()
    results = sim.get_results()

    return sim, results


def run_multiple_simulations(n_runs=100):

    results = []

    for seed in range(n_runs):
        _, r = run_one_simulation(seed)
        results.append(r)

    return results


def mean(x):
    return sum(x)/len(x)


def std(x):
    m = mean(x)
    return math.sqrt(sum((i-m)**2 for i in x)/(len(x)-1))


def confidence_interval(values):

    m = mean(values)
    s = std(values)

    margin = config.CI_Z_VALUE * s / math.sqrt(len(values))

    return m-margin, m+margin


def summarize(results):

    summary = {}

    for k in results[0]:

        values = [r[k] for r in results]

        ci_low, ci_high = confidence_interval(values)

        summary[k] = {
            "mean": mean(values),
            "ci_low": ci_low,
            "ci_high": ci_high
        }

    return summary


# ------------------------------
# DRIVER FAIRNESS PLOTS
# ------------------------------

def plot_driver_earning_rate(sim):

    ensure_output_dir()

    earning_rates = metrics.get_driver_earning_rates(sim)

    plt.figure(figsize=(8,5))

    plt.hist(earning_rates, bins=20, edgecolor="black")

    plt.title("Distribution of Driver Earning Rate")
    plt.xlabel("Earning rate ($ per hour)")
    plt.ylabel("Number of drivers")

    plt.tight_layout()

    plt.savefig("plots/driver_earning_rate_hist.png")
    plt.close()


def plot_driver_utilization(sim):

    ensure_output_dir()

    util = metrics.get_driver_utilizations(sim)

    plt.figure(figsize=(8,5))

    plt.hist(util, bins=20, edgecolor="black")

    plt.title("Distribution of Driver Utilization")
    plt.xlabel("Utilization")
    plt.ylabel("Number of drivers")

    plt.tight_layout()

    plt.savefig("plots/driver_utilization_hist.png")
    plt.close()


def plot_earning_vs_utilization(sim):

    ensure_output_dir()

    earning = []
    util = []

    for d in sim.exited_drivers:

        if d.online_time >= config.MIN_ONLINE_TIME_FOR_FAIRNESS:

            earning.append(d.earning_rate)
            util.append(d.utilization)

    plt.figure(figsize=(8,5))

    plt.scatter(util, earning)

    plt.title("Driver Earning Rate vs Utilization")
    plt.xlabel("Utilization")
    plt.ylabel("Earning rate ($/hour)")

    plt.tight_layout()

    plt.savefig("plots/earning_vs_utilization.png")
    plt.close()


# ------------------------------
# KPI SUMMARY PLOT
# ------------------------------

def plot_mean_kpis(summary):

    ensure_output_dir()

    kpis = [
        "avg_wait_time",
        "avg_trip_time",
        "abandonment_rate",
        "avg_driver_earning_rate"
    ]

    labels = []
    means = []
    lower = []
    upper = []

    for k in kpis:

        if k in summary:

            labels.append(k)

            means.append(summary[k]["mean"])

            lower.append(summary[k]["mean"] - summary[k]["ci_low"])
            upper.append(summary[k]["ci_high"] - summary[k]["mean"])

    plt.figure(figsize=(9,6))

    plt.bar(labels, means)

    plt.errorbar(
        labels,
        means,
        yerr=[lower,upper],
        fmt="none",
        capsize=5
    )

    plt.title("Mean KPIs Across Simulation Runs")

    plt.ylabel("Value")

    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.savefig("plots/kpi_means.png")
    plt.close()


# ------------------------------
# MAIN PIPELINE
# ------------------------------

def generate_all_plots():

    sim,_ = run_one_simulation(seed=0)

    plot_driver_earning_rate(sim)
    plot_driver_utilization(sim)
    plot_earning_vs_utilization(sim)

    results = run_multiple_simulations(100)

    summary = summarize(results)

    plot_mean_kpis(summary)

    print("Plots saved in 'plots/' folder")


if __name__ == "__main__":

    generate_all_plots()
