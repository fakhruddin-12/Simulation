import os
import random
import math
import matplotlib.pyplot as plt

import config
from classes.simulation import Simulation
from classes.generate_random import Distributions
from classes.event_handlers import EventHandlers
from modules import metrics


OUTPUT_DIR = "plots"


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_one_simulation_with_objects(seed=None):
    """
    Runs one simulation and returns both:
    1. the Simulation object
    2. the KPI dictionary

    This is useful because:
    - KPI boxplots need run-level summaries
    - fairness histograms need driver-level values from the simulation object
    """
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
    """
    Run multiple independent replications using different seeds.
    Returns a list of result dictionaries.
    """
    results = []

    for seed in range(n_runs):
        _, run_result = run_one_simulation_with_objects(seed=seed)
        results.append(run_result)

    return results


def mean(values):
    return sum(values) / len(values) if values else 0.0


def sample_std(values):
    n = len(values)
    if n < 2:
        return 0.0

    m = mean(values)
    var = sum((x - m) ** 2 for x in values) / (n - 1)
    return math.sqrt(var)


def confidence_interval(values, z=config.CI_Z_VALUE):
    n = len(values)
    if n == 0:
        return (0.0, 0.0)

    m = mean(values)
    s = sample_std(values)

    if n == 1:
        return (m, m)

    margin = z * s / math.sqrt(n)
    return (m - margin, m + margin)


def summarize_results(results):
    """
    Convert a list of run-level KPI dictionaries into summary stats.
    """
    if not results:
        return {}

    kpi_names = results[0].keys()
    summary = {}

    for kpi in kpi_names:
        values = [r[kpi] for r in results]
        ci_low, ci_high = confidence_interval(values)

        summary[kpi] = {
            "mean": mean(values),
            "std": sample_std(values),
            "ci_low": ci_low,
            "ci_high": ci_high,
        }

    return summary


def plot_driver_earning_rate_histogram(sim, bins=20, filename="driver_earning_rate_hist.png"):
    """
    Histogram of driver earning rates from one simulation run.
    Fairness is judged on earnings per online time, not raw trip counts.
    """
    ensure_output_dir()

    earning_rates = metrics.get_driver_earning_rates(sim)

    plt.figure(figsize=(8, 5))
    plt.hist(earning_rates, bins=bins, edgecolor="black")
    plt.xlabel("Driver earning rate")
    plt.ylabel("Frequency")
    plt.title("Distribution of Driver Earning Rate")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close()


def plot_driver_utilization_histogram(sim, bins=20, filename="driver_utilization_hist.png"):
    """
    Histogram of driver utilization from one simulation run.
    """
    ensure_output_dir()

    utilizations = metrics.get_driver_utilizations(sim)

    plt.figure(figsize=(8, 5))
    plt.hist(utilizations, bins=bins, edgecolor="black")
    plt.xlabel("Driver utilization")
    plt.ylabel("Frequency")
    plt.title("Distribution of Driver Utilization")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close()


def plot_kpi_comparison(summary, actual_kpis, filename="kpi_comparison.png"):
    """
    Bar chart of simulated mean KPI vs actual KPI, with CI error bars.
    """
    ensure_output_dir()

    common_kpis = [kpi for kpi in actual_kpis if kpi in summary]

    if not common_kpis:
        print("No common KPIs found between simulation summary and actual KPIs.")
        return

    sim_means = [summary[kpi]["mean"] for kpi in common_kpis]
    actual_vals = [actual_kpis[kpi] for kpi in common_kpis]
    lower_errors = [summary[kpi]["mean"] - summary[kpi]["ci_low"] for kpi in common_kpis]
    upper_errors = [summary[kpi]["ci_high"] - summary[kpi]["mean"] for kpi in common_kpis]

    x = list(range(len(common_kpis)))
    width = 0.35

    plt.figure(figsize=(10, 6))
    plt.bar([i - width / 2 for i in x], sim_means, width=width, label="Simulation Mean")
    plt.bar([i + width / 2 for i in x], actual_vals, width=width, label="Actual KPI")
    plt.errorbar(
        [i - width / 2 for i in x],
        sim_means,
        yerr=[lower_errors, upper_errors],
        fmt="none",
        capsize=5
    )

    plt.xticks(x, common_kpis, rotation=30, ha="right")
    plt.ylabel("KPI value")
    plt.title("Simulation vs Actual KPI Comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close()


def plot_kpi_boxplots(results, kpis_to_plot, filename="kpi_boxplots.png"):
    """
    Boxplots of KPI values across repeated simulation runs.
    Useful for showing variability across replications.
    """
    ensure_output_dir()

    data = []
    labels = []

    for kpi in kpis_to_plot:
        if kpi in results[0]:
            data.append([r[kpi] for r in results])
            labels.append(kpi)

    if not data:
        print("No valid KPIs found for boxplot.")
        return

    plt.figure(figsize=(10, 6))
    plt.boxplot(data, tick_labels=labels)
    plt.ylabel("KPI value")
    plt.title("Distribution of KPIs Across Simulation Runs")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close()


def plot_driver_earning_rate_vs_utilization(sim, filename="earning_rate_vs_utilization.png"):
    """
    Scatter plot showing relationship between driver earning rate and utilization.
    This is useful for diagnosing whether higher utilization is strongly associated with better earnings.
    """
    ensure_output_dir()

    earning_rates = []
    utilizations = []

    for driver in sim.exited_drivers:
        if driver.online_time is not None and driver.online_time >= config.MIN_ONLINE_TIME_FOR_FAIRNESS:
            earning_rates.append(driver.earning_rate)
            utilizations.append(driver.utilization)

    plt.figure(figsize=(8, 5))
    plt.scatter(utilizations, earning_rates)
    plt.xlabel("Driver utilization")
    plt.ylabel("Driver earning rate")
    plt.title("Driver Earning Rate vs Utilization")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename), dpi=300)
    plt.close()


def generate_all_plots(n_runs=100, actual_kpis=None):
    """
    Main plotting pipeline.

    Generates:
    1. driver fairness histograms from one representative run
    2. KPI boxplots across many runs
    3. simulation-vs-actual KPI comparison if actual KPIs are provided
    4. earning-rate vs utilization scatter
    """
    ensure_output_dir()

    # Representative single run for driver-level distributions
    sim, _ = run_one_simulation_with_objects(seed=0)

    plot_driver_earning_rate_histogram(sim)
    plot_driver_utilization_histogram(sim)
    plot_driver_earning_rate_vs_utilization(sim)

    # Multiple runs for KPI variability
    results = run_multiple_simulations(n_runs=n_runs)
    summary = summarize_results(results)

    plot_kpi_boxplots(
        results,
        kpis_to_plot=[
            "avg_wait_time",
            "abandonment_rate",
            "avg_trip_time",
            "avg_driver_earning_rate",
            "gini_driver_earning_rate",
        ],
    )

    if actual_kpis is not None:
        plot_kpi_comparison(summary, actual_kpis)

    print(f"Plots saved in folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    # Fill this from your actual data when ready
    actual_kpis = {
        # "avg_wait_time": 8.2,
        # "abandonment_rate": 0.12,
        # "avg_trip_time": 27.0,
        # "avg_driver_earning_rate": 0.16,
        # "gini_driver_earning_rate": 0.35,
    }

    if not actual_kpis:
        actual_kpis = None

    generate_all_plots(n_runs=100, actual_kpis=actual_kpis)