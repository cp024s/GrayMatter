"""
Toggle-based switching activity metric.

This module defines a pure metric function that converts
parsed switching activity data into a single scalar value X.

The metric is intentionally simple and transparent:
    X = total_number_of_toggles / normalization_factor

This file must NOT:
- perform statistical inference
- apply thresholds
- depend on Monte Carlo logic
"""

from typing import Dict, Any


def compute_toggle_metric(
    activity_data: Dict[str, Any],
    normalization: str = "per_cycle"
) -> float:
    """
    Compute a toggle-based switching activity metric.

    Parameters
    ----------
    activity_data : dict
        Parsed switching activity data for a single simulation run.
        Expected structure (minimum):
            {
                "total_toggles": int,
                "cycles": int
            }

    normalization : str
        Normalization mode.
        Supported values:
            - "per_cycle" : normalize by number of cycles
            - "raw"       : no normalization

    Returns
    -------
    float
        Scalar switching activity metric X.

    Raises
    ------
    ValueError
        If required fields are missing or normalization is invalid.
    """

    if not isinstance(activity_data, dict):
        raise ValueError("activity_data must be a dictionary")

    if "total_toggles" not in activity_data:
        raise ValueError("activity_data missing required key: 'total_toggles'")

    if normalization == "per_cycle":
        if "cycles" not in activity_data:
            raise ValueError(
                "activity_data missing required key 'cycles' "
                "for per_cycle normalization"
            )

        cycles = activity_data["cycles"]
        if cycles <= 0:
            raise ValueError("Number of cycles must be positive")

        metric = activity_data["total_toggles"] / float(cycles)

    elif normalization == "raw":
        metric = float(activity_data["total_toggles"])

    else:
        raise ValueError(
            f"Unsupported normalization mode: {normalization}"
        )

    return metric


def validate_activity_data(activity_data: Dict[str, Any]) -> None:
    """
    Validate basic structure of parsed activity data.

    This function performs lightweight sanity checks and
    raises exceptions on structural errors.

    Parameters
    ----------
    activity_data : dict
        Parsed switching activity data.

    Raises
    ------
    ValueError
        If validation fails.
    """

    required_fields = ["total_toggles", "cycles"]

    for field in required_fields:
        if field not in activity_data:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(activity_data["total_toggles"], int):
        raise ValueError("'total_toggles' must be an integer")

    if not isinstance(activity_data["cycles"], int):
        raise ValueError("'cycles' must be an integer")

    if activity_data["total_toggles"] < 0:
        raise ValueError("'total_toggles' must be non-negative")

    if activity_data["cycles"] <= 0:
        raise ValueError("'cycles' must be positive")
