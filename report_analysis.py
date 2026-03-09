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
        _, result = run_one_simulation(seed=seed)
        results.append(result)

    return results


def mean(x):
    return sum(x) / len(x) if x else 0.0


def std(x):
    if len(x) < 2:
        return 0.0
    m = mean(x)
    return math.sqrt(sum((i - m) ** 2 for i in x) / (len(x) - 1))


def confidence_interval(values):
    if len(values) == 0:
        return (0.0, 0.0)

    m = mean(values)
    s = std(values)

    if len(values) == 1:
        return (m, m)

    margin = config.CI_Z_VALUE * s / math.sqrt(len(values))
    return m - margin, m + margin


def summarize(results):
    summary = {}

    if not results:
        return summary

    for kpi in results[0]:
        values = [r[kpi] for r in results]
        ci_low, ci_high = confidence_interval(values)

        summary[kpi] = {
            "mean": mean(values),
            "std": std(values),
            "ci_low": ci_low,
            "ci_high": ci_high
        }

    return summary


def print_summary(summary):
    print("\n=== ANALYSIS SUMMARY ACROSS RUNS ===\n")

    for kpi, vals in summary.items():
        print(f"{kpi}")
        print(f"  mean   : {vals['mean']:.6f}")
        print(f"  std    : {vals['std']:.6f}")
        print(f"  ci_low : {vals['ci_low']:.6f}")
        print(f"  ci_high: {vals['ci_high']:.6f}")
        print()


# ------------------------------
# DRIVER FAIRNESS / DRIVER-SIDE PLOTS
# ------------------------------

def plot_driver_earning_boxplot(sim):
    ensure_output_dir()

    earnings = []

    for d in sim.exited_drivers:
        if d.online_time is not None and d.online_time >= config.MIN_ONLINE_TIME_FOR_FAIRNESS:
            earnings.append(d.total_earnings)

    plt.figure(figsize=(7, 5))
    plt.boxplot(earnings)
    plt.title("Box Plot of Driver Earnings")
    plt.ylabel("Total earnings")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "driver_earnings_boxplot.png"), dpi=300)
    plt.close()


def plot_driver_earning_rate(sim):
    ensure_output_dir()

    earning_rates = metrics.get_driver_earning_rates(sim)

    plt.figure(figsize=(8, 5))
    plt.hist(earning_rates, bins=20, edgecolor="black")
    plt.title("Distribution of Driver Earning Rate")
    plt.xlabel("Earning rate ($ per hour)")
    plt.ylabel("Number of drivers")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "driver_earning_rate_hist.png"), dpi=300)
    plt.close()


def plot_driver_utilization(sim):
    ensure_output_dir()

    util = metrics.get_driver_utilizations(sim)

    plt.figure(figsize=(8, 5))
    plt.hist(util, bins=20, edgecolor="black")
    plt.title("Distribution of Driver Utilization")
    plt.xlabel("Utilization")
    plt.ylabel("Number of drivers")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "driver_utilization_hist.png"), dpi=300)
    plt.close()


def plot_earning_vs_utilization(sim):
    ensure_output_dir()

    earning = []
    util = []

    for d in sim.exited_drivers:
        if d.online_time is not None and d.online_time >= config.MIN_ONLINE_TIME_FOR_FAIRNESS:
            earning.append(d.earning_rate)
            util.append(d.utilization)

    plt.figure(figsize=(8, 5))
    plt.scatter(util, earning)
    plt.title("Driver Earning Rate vs Utilization")
    plt.xlabel("Utilization")
    plt.ylabel("Earning rate ($/hour)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "earning_vs_utilization.png"), dpi=300)
    plt.close()


# ------------------------------
# RUN-LEVEL KPI DISTRIBUTION PLOTS
# ------------------------------

def plot_waiting_time_histogram(results):
    ensure_output_dir()

    wait_times = [r["avg_wait_time"] for r in results if "avg_wait_time" in r]

    plt.figure(figsize=(8, 5))
    plt.hist(wait_times, bins=20, edgecolor="black")
    plt.title("Histogram of Average Waiting Time Across Runs")
    plt.xlabel("Average waiting time")
    plt.ylabel("Number of runs")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "waiting_time_hist.png"), dpi=300)
    plt.close()


def plot_abandonment_rate_histogram(results):
    ensure_output_dir()

    abandonment_rates = [r["abandonment_rate"] for r in results if "abandonment_rate" in r]

    plt.figure(figsize=(8, 5))
    plt.hist(abandonment_rates, bins=20, edgecolor="black")
    plt.title("Histogram of Abandonment Rate Across Runs")
    plt.xlabel("Abandonment rate")
    plt.ylabel("Number of runs")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "abandonment_rate_hist.png"), dpi=300)
    plt.close()


# ------------------------------
# MAIN PIPELINE
# ------------------------------

def generate_report_outputs(n_runs=50):
    print("Current working directory:", os.getcwd())
    print("Plots will be saved in:", os.path.abspath(OUTPUT_DIR))

    # One representative run for driver-level plots
    sim, _ = run_one_simulation(seed=0)

    plot_driver_earning_boxplot(sim)
    plot_driver_earning_rate(sim)
    plot_driver_utilization(sim)
    plot_earning_vs_utilization(sim)

    # Multiple runs for analysis summary + KPI histograms
    results = run_multiple_simulations(n_runs=n_runs)
    summary = summarize(results)

    print_summary(summary)

    plot_waiting_time_histogram(results)
    plot_abandonment_rate_histogram(results)

    print(f"Plots saved in '{OUTPUT_DIR}/' folder")


if __name__ == "__main__":
    generate_report_outputs(n_runs=50)

