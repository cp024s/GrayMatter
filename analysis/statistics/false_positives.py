"""
False positive rate estimation.

This module quantifies the false alarm behavior of the
statistical inference pipeline by evaluating clean
observations against a clean baseline model.

It answers:
    "How often does the detector flag normal behavior
     as abnormal under a given threshold?"
"""

from typing import List, Dict, Any

from analysis.inference.hypothesis import evaluate_hypothesis
from analysis.statistics.baseline_model import BaselineModel


def estimate_false_positive_rate(
    observations: List[float],
    baseline: BaselineModel,
    z_threshold: float
) -> Dict[str, Any]:
    """
    Estimate false positive rate for a given Z-score threshold.

    Parameters
    ----------
    observations : list of float
        Observed values from clean design (X_i).

    baseline : BaselineModel
        Converged baseline statistical model.

    z_threshold : float
        Z-score threshold for flagging abnormal behavior.

    Returns
    -------
    dict
        False positive statistics including rate and counts.
    """

    if z_threshold <= 0:
        raise ValueError("Z-score threshold must be positive")

    total = len(observations)
    if total == 0:
        raise ValueError("No observations provided")

    false_positives = 0
    deviations = []

    for obs in observations:
        stats = evaluate_hypothesis(obs, baseline)
        z = abs(stats["z_score"])
        deviations.append(z)

        if z > z_threshold:
            false_positives += 1

    rate = false_positives / float(total)

    return {
        "threshold": z_threshold,
        "total_observations": total,
        "false_positives": false_positives,
        "false_positive_rate": rate,
        "max_z": max(deviations),
        "mean_z": sum(deviations) / total,
    }
