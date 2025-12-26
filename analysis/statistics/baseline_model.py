"""
Baseline statistical model.

This module defines a formal representation of baseline
behavior derived from Monte Carlo sampling. It encapsulates
mean, variance, sample count, and metadata required for
statistically sound reuse across experiments.

This module must NOT:
- perform sampling
- update statistics
- apply detection thresholds
"""
"""
Baseline statistical model construction for clean designs.
"""

import numpy as np


def build_baseline_distribution(clean_toggles: dict) -> dict:
    """
    Build a baseline distribution from clean-design toggle counts.

    Args:
        clean_toggles (dict):
            { "signal_name": toggle_count }

    Returns:
        dict containing baseline statistics and samples
    """

    if not clean_toggles:
        raise ValueError("Empty toggle dictionary provided to baseline model")

    # --------------------------------------------------
    # Raw samples (toggle counts per signal)
    # --------------------------------------------------
    samples = np.array(list(clean_toggles.values()), dtype=float)

    # --------------------------------------------------
    # Basic statistics
    # --------------------------------------------------
    mean = float(np.mean(samples))
    std = float(np.std(samples))
    variance = float(np.var(samples))

    # --------------------------------------------------
    # Robust statistics (IQR-based)
    # --------------------------------------------------
    q1 = np.percentile(samples, 25)
    q3 = np.percentile(samples, 75)
    iqr = q3 - q1
    iqr_threshold = q3 + 1.5 * iqr

    # --------------------------------------------------
    # Per-signal normalization (z-score)
    # --------------------------------------------------
    normalized = {}
    for sig, val in clean_toggles.items():
        if std > 0:
            normalized[sig] = (val - mean) / std
        else:
            normalized[sig] = 0.0

    return {
        "samples": samples.tolist(),
        "mean": mean,
        "std": std,
        "variance": variance,
        "iqr_threshold": float(iqr_threshold),
        "normalized": normalized,
    }
