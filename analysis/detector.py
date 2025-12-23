"""
Detection orchestration logic.

This module combines:
- a converged baseline model
- an observed scalar metric
- a decision policy (thresholds)

to produce a structured detection result.

This module does NOT:
- perform simulation
- compute metrics
- estimate baselines
"""

import argparse
from pathlib import Path
from typing import Dict, Any

import yaml

from analysis.statistics.baseline_model import BaselineModel
from analysis.inference.hypothesis import evaluate_hypothesis


# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML configuration file."""
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r") as f:
        return yaml.safe_load(f)


# ------------------------------------------------------------
# Detection logic
# ------------------------------------------------------------

def detect(
    observed: float,
    baseline: BaselineModel,
    thresholds: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Perform detection based on observed value and thresholds.

    Parameters
    ----------
    observed : float
        Observed scalar metric X_obs.

    baseline : BaselineModel
        Converged baseline statistical model.

    thresholds : dict
        Detection threshold configuration.

    Returns
    -------
    dict
        Structured detection result including evidence
        and decision flags.
    """

    stats = evaluate_hypothesis(observed, baseline)

    z_threshold = thresholds.get("z_score_threshold")
    confidence_level = thresholds.get("confidence_level")

    if z_threshold is None or confidence_level is None:
        raise ValueError(
            "Detection thresholds must define "
            "'z_score_threshold' and 'confidence_level'"
        )

    z_exceeded = abs(stats["z_score"]) > z_threshold
    confidence_exceeded = stats["confidence"] > confidence_level

    decision = z_exceeded and confidence_exceeded

    return {
        "observed": stats["observed"],
        "baseline_mean": stats["mean"],
        "baseline_variance": stats["variance"],
        "z_score": stats["z_score"],
        "confidence": stats["confidence"],
        "z_threshold": z_threshold,
        "confidence_level": confidence_level,
        "z_exceeded": z_exceeded,
        "confidence_exceeded": confidence_exceeded,
        "decision": decision,
    }


# ------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Detection orchestration"
    )

    parser.add_argument(
        "--baseline",
        required=True,
        type=Path,
        help="Path to baseline model YAML"
    )

    parser.add_argument(
        "--observed",
        required=True,
        type=float,
        help="Observed scalar metric X_obs"
    )

    parser.add_argument(
        "--det_cfg",
        required=True,
        type=Path,
        help="Path to detection thresholds YAML"
    )

    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()

    baseline = BaselineModel.load(args.baseline)
    thresholds = load_yaml(args.det_cfg)

    result = detect(
        observed=args.observed,
        baseline=baseline,
        thresholds=thresholds
    )

    # Print structured result for inspection
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
