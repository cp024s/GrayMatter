import numpy as np
from collections import defaultdict


def build_baseline_distribution(toggle_counts_list: list[dict]) -> dict:
    """
    Build per-signal baseline statistics from multiple clean runs.

    Args:
        toggle_counts_list (list of dict):
            [
              { signal_name : toggle_count },   # run 1
              { signal_name : toggle_count },   # run 2
              ...
            ]

    Returns:
        dict:
            {
              signal: {
                "mean": float,
                "std": float,
                "iqr_threshold": float,
                "samples": [float]
              }
            }
    """

    # --------------------------------------------------
    # Aggregate samples per signal
    # --------------------------------------------------
    samples_per_signal = defaultdict(list)

    for run in toggle_counts_list:
        for signal, count in run.items():
            samples_per_signal[signal].append(float(count))

    # --------------------------------------------------
    # Compute statistics
    # --------------------------------------------------
    baseline = {}

    for signal, samples in samples_per_signal.items():
        arr = np.array(samples, dtype=float)

        mean = arr.mean()
        std = arr.std(ddof=1) if arr.size > 1 else 0.0

        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1
        iqr_threshold = q3 + 1.5 * iqr

        baseline[signal] = {
            "mean": float(mean),
            "std": float(std),
            "iqr_threshold": float(iqr_threshold),
            "samples": arr.tolist(),
        }

    return baseline
