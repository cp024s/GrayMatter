import numpy as np


def build_baseline_distribution(toggle_counts: dict) -> dict:
    """
    Build per-signal baseline statistics from a clean run.

    Args:
        toggle_counts (dict):
            { signal_name : toggle_count }

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

    baseline = {}

    for signal, count in toggle_counts.items():
        samples = np.array([count], dtype=float)

        q1 = np.percentile(samples, 25)
        q3 = np.percentile(samples, 75)
        iqr = q3 - q1
        iqr_threshold = q3 + 1.5 * iqr

        baseline[signal] = {
            "mean": float(samples.mean()),
            "std": float(samples.std() if samples.size > 1 else 0.0),
            "iqr_threshold": float(iqr_threshold),
            "samples": samples.tolist(),
        }

    return baseline
