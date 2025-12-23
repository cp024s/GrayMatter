"""
Statistical hypothesis evaluation.

This module implements hypothesis testing logic to evaluate
whether an observed scalar value is statistically consistent
with a baseline distribution.

It computes deviation metrics (e.g., Z-score) and confidence
measures, but does NOT declare final detection outcomes.
"""

from typing import Dict, Any
import math

from analysis.statistics.baseline_model import BaselineModel


def compute_z_score(
    observed: float,
    baseline: BaselineModel
) -> float:
    """
    Compute Z-score of an observed value with respect to baseline.

    Parameters
    ----------
    observed : float
        Observed scalar value X_obs.

    baseline : BaselineModel
        Converged baseline statistical model.

    Returns
    -------
    float
        Z-score indicating deviation from baseline.

    Raises
    ------
    ValueError
        If baseline variance is zero.
    """

    if baseline.variance <= 0:
        raise ValueError(
            "Baseline variance must be positive to compute Z-score"
        )

    return (observed - baseline.mean) / math.sqrt(baseline.variance)


def compute_confidence_from_z(
    z_score: float
) -> float:
    """
    Convert Z-score to two-sided confidence level.

    This uses the cumulative distribution function (CDF)
    of the standard normal distribution.

    Parameters
    ----------
    z_score : float
        Z-score value.

    Returns
    -------
    float
        Confidence level in [0, 1].
    """

    # Two-sided confidence
    return 1.0 - math.erfc(abs(z_score) / math.sqrt(2.0))


def evaluate_hypothesis(
    observed: float,
    baseline: BaselineModel
) -> Dict[str, Any]:
    """
    Evaluate statistical consistency of an observation
    with respect to a baseline model.

    Parameters
    ----------
    observed : float
        Observed scalar value X_obs.

    baseline : BaselineModel
        Baseline statistical model.

    Returns
    -------
    dict
        Dictionary containing deviation and confidence metrics.
    """

    z = compute_z_score(observed, baseline)
    confidence = compute_confidence_from_z(z)

    return {
        "observed": observed,
        "mean": baseline.mean,
        "variance": baseline.variance,
        "z_score": z,
        "confidence": confidence,
    }
