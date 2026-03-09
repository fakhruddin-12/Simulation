import random
import math

import config
from classes.simulation import Simulation
from classes.generate_random import Distributions
from classes.event_handlers import EventHandlers


def run_one_simulation(seed=None):
    if seed is not None:
        random.seed(seed)

    handlers = EventHandlers(None)
    distributions = Distributions(None)
    sim = Simulation(handlers, distributions)

    handlers.simulation = sim
    distributions.simulation = sim

    sim.run()
    return sim.get_results()


def run_multiple_simulations(n_runs=100):
    results = []
    for seed in range(n_runs):
        results.append(run_one_simulation(seed=seed))
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
    if not results:
        return {}

    summary = {}
    kpi_names = results[0].keys()

    for kpi in kpi_names:
        values = [r[kpi] for r in results]
        summary[kpi] = {
            "mean": mean(values),
            "std": sample_std(values),
            "ci_low": confidence_interval(values)[0],
            "ci_high": confidence_interval(values)[1],
        }

    return summary


def compare_with_actual(summary, actual_kpis):
    comparison = {}

    for kpi, actual_value in actual_kpis.items():
        if kpi not in summary:
            continue

        sim_mean = summary[kpi]["mean"]
        comparison[kpi] = {
            "actual": actual_value,
            "sim_mean": sim_mean,
            "difference": sim_mean - actual_value,
            "ci_low": summary[kpi]["ci_low"],
            "ci_high": summary[kpi]["ci_high"],
            "actual_inside_ci": summary[kpi]["ci_low"] <= actual_value <= summary[kpi]["ci_high"],
        }

    return comparison


if __name__ == "__main__":
    actual_kpis = {
        # Fill these using your data
        # "avg_wait_time": 8.2,
        # "abandonment_rate": 0.12,
        # "avg_driver_earning_rate": 4.5,
    }

    results = run_multiple_simulations(n_runs=100)
    summary = summarize_results(results)

    print("=== Simulation summary ===")
    for kpi, vals in summary.items():
        print(kpi, vals)

    if actual_kpis:
        comparison = compare_with_actual(summary, actual_kpis)
        print("\n=== Comparison with actual ===")
        for kpi, vals in comparison.items():
            print(kpi, vals)