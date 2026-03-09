def suggest_parameter_changes(comparison):
    suggestions = []

    if "avg_wait_time" in comparison:
        diff = comparison["avg_wait_time"]["difference"]
        if diff < 0:
            suggestions.append(
                "Simulated average wait time is lower than actual. Consider reducing driver supply, reducing driver availability, or lowering travel speed."
            )
        elif diff > 0:
            suggestions.append(
                "Simulated average wait time is higher than actual. Consider increasing driver supply, increasing driver availability, or increasing travel speed."
            )

    if "abandonment_rate" in comparison:
        diff = comparison["abandonment_rate"]["difference"]
        if diff < 0:
            suggestions.append(
                "Simulated abandonment rate is lower than actual. Consider reducing rider patience or reducing effective driver supply."
            )
        elif diff > 0:
            suggestions.append(
                "Simulated abandonment rate is higher than actual. Consider increasing rider patience or increasing effective driver supply."
            )

    if "avg_trip_time" in comparison:
        diff = comparison["avg_trip_time"]["difference"]
        if diff < 0:
            suggestions.append(
                "Simulated trip time is lower than actual. Consider lowering average speed."
            )
        elif diff > 0:
            suggestions.append(
                "Simulated trip time is higher than actual. Consider increasing average speed."
            )

    if "avg_driver_earning_rate" in comparison:
        diff = comparison["avg_driver_earning_rate"]["difference"]
        if diff < 0:
            suggestions.append(
                "Simulated driver earning rate is lower than actual. Consider increasing fare parameters or improving matching efficiency."
            )
        elif diff > 0:
            suggestions.append(
                "Simulated driver earning rate is higher than actual. Consider lowering fare parameters or reducing matching efficiency assumptions."
            )

    if "gini_driver_earning_rate" in comparison:
        diff = comparison["gini_driver_earning_rate"]["difference"]
        if diff < 0:
            suggestions.append(
                "Simulated driver earning fairness is better than actual. Consider adding more geographical imbalance or less fair matching if you need closer realism."
            )
        elif diff > 0:
            suggestions.append(
                "Simulated driver earning fairness is worse than actual. Consider a fairer assignment policy, such as weighting distance with historical driver earnings."
            )

    return suggestions


if __name__ == "__main__":
    example_comparison = {
        "avg_wait_time": {"difference": -2.0},
        "abandonment_rate": {"difference": -0.03},
        "avg_driver_earning_rate": {"difference": 0.5},
        "gini_driver_earning_rate": {"difference": 0.08},
    }

    suggestions = suggest_parameter_changes(example_comparison)
    print("=== Tuning suggestions ===")
    for s in suggestions:
        print("-", s)