"""
Monte Carlo sampling engine.

This module orchestrates repeated simulation runs to estimate
the baseline distribution of a scalar observable X derived from
switching activity.

Responsibilities:
- Load configuration
- Initialize simulation backend
- Run Monte Carlo sampling in batches
- Track convergence of mean and variance

This module must NOT:
- perform detection or hypothesis testing
- apply decision thresholds
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List

import yaml

from analysis.metrics.toggle_metric import compute_toggle_metric
from analysis.monte_carlo.convergence import ConvergenceTracker

# NOTE:
# Simulation backends are imported lazily to avoid hard dependencies
# during analysis-only workflows.


# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML configuration file."""
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r") as f:
        return yaml.safe_load(f)


def setup_logging(enable: bool) -> None:
    """Configure logging."""
    if enable:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
    else:
        logging.basicConfig(level=logging.WARNING)


def get_repo_root() -> Path:
    """Return repository root directory."""
    return Path(__file__).resolve().parents[3]


# ------------------------------------------------------------
# Backend factory
# ------------------------------------------------------------

def get_simulation_backend(name: str):
    """
    Instantiate a simulation backend by name.

    Parameters
    ----------
    name : str
        Backend identifier ("iverilog" or "vivado").

    Returns
    -------
    object
        Simulation backend instance.

    Raises
    ------
    ValueError
        If backend is not supported.
    """

    name = name.lower()

    if name == "iverilog":
        from sim.backends.iverilog import IcarusBackend
        return IcarusBackend()

    if name == "vivado":
        from sim.backends.vivado import VivadoBackend
        return VivadoBackend()

    raise ValueError(f"Unsupported simulation backend: {name}")


# ------------------------------------------------------------
# CLI argument parsing
# ------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Monte Carlo baseline sampling engine"
    )

    parser.add_argument(
        "--backend",
        required=True,
        choices=["iverilog", "vivado"],
        help="Simulation backend to use"
    )

    parser.add_argument(
        "--sim_cfg",
        required=True,
        type=Path,
        help="Path to simulation configuration YAML"
    )

    parser.add_argument(
        "--mc_cfg",
        required=True,
        type=Path,
        help="Path to Monte Carlo configuration YAML"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output file for baseline statistics"
    )

    return parser.parse_args()


# ------------------------------------------------------------
# Batch execution helper
# ------------------------------------------------------------

def run_single_sample(
    backend,
    sim_cfg: Dict[str, Any],
    normalization: str
) -> float:
    """
    Run a single simulation sample and compute the observable X.

    Parameters
    ----------
    backend : object
        Simulation backend instance.

    sim_cfg : dict
        Simulation configuration.

    normalization : str
        Normalization mode for the metric.

    Returns
    -------
    float
        Scalar observable X for this sample.
    """

    # Run simulation and extract activity
    activity_data = backend.run(sim_cfg)

    # Compute metric
    X = compute_toggle_metric(
        activity_data,
        normalization=normalization
    )

    return X

# END of Part 1 ---


# ------------------------------------------------------------
# Monte Carlo execution
# ------------------------------------------------------------

def run_monte_carlo(
    backend_name: str,
    sim_cfg_path: Path,
    mc_cfg_path: Path,
    output_path: Path = None
) -> Dict[str, Any]:
    """
    Run Monte Carlo sampling until convergence is reached
    or maximum batch count is exceeded.

    Parameters
    ----------
    backend_name : str
        Name of the simulation backend.

    sim_cfg_path : Path
        Path to simulation configuration YAML.

    mc_cfg_path : Path
        Path to Monte Carlo configuration YAML.

    output_path : Path, optional
        Path to write baseline statistics (YAML).

    Returns
    -------
    dict
        Baseline statistics including mean and variance.
    """

    # Load configurations
    sim_cfg = load_yaml(sim_cfg_path)
    mc_cfg = load_yaml(mc_cfg_path)

    setup_logging(mc_cfg.get("enable_logging", True))

    logging.info("Initializing Monte Carlo sampling engine")

    backend = get_simulation_backend(backend_name)

    # Monte Carlo parameters
    batch_size = mc_cfg["batch_size"]
    max_batches = mc_cfg["max_batches"]
    normalization = mc_cfg.get("normalization", "per_cycle")

    # Convergence parameters
    tracker = ConvergenceTracker(
        mean_eps=mc_cfg["mean_eps"],
        var_eps=mc_cfg["var_eps"],
        stable_batches=mc_cfg["stable_batches"]
    )

    all_samples: List[float] = []

    converged = False

    for batch_idx in range(1, max_batches + 1):
        logging.info(f"Starting batch {batch_idx}")

        for _ in range(batch_size):
            X = run_single_sample(
                backend=backend,
                sim_cfg=sim_cfg,
                normalization=normalization
            )
            tracker.update(X)
            all_samples.append(X)

        status = tracker.status()
        logging.info(
            f"Batch {batch_idx} | "
            f"samples={status['samples']} | "
            f"mean={status['mean']:.6f} | "
            f"variance={status['variance']}"
        )

        if tracker.check_convergence():
            logging.info(
                f"Convergence reached after {batch_idx} batches"
            )
            converged = True
            break

    if not converged:
        logging.warning(
            "Monte Carlo sampling terminated without convergence "
            f"after {max_batches} batches"
        )

    baseline = {
        "mean": tracker.mean(),
        "variance": tracker.variance() if tracker.status()["variance"] is not None else None,
        "samples": tracker.status()["samples"],
        "converged": converged,
        "backend": backend_name,
        "batch_size": batch_size,
        "batches_run": batch_idx,
        "normalization": normalization
    }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as f:
            yaml.safe_dump(baseline, f)
        logging.info(f"Baseline statistics written to {output_path}")

    return baseline


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

def main() -> None:
    """CLI entry point."""
    args = parse_args()

    run_monte_carlo(
        backend_name=args.backend,
        sim_cfg_path=args.sim_cfg,
        mc_cfg_path=args.mc_cfg,
        output_path=args.output
    )


if __name__ == "__main__":
    main()
