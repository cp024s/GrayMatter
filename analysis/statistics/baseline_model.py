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

from typing import Dict, Any
from pathlib import Path
import yaml


class BaselineModel:
    """
    Represents a converged baseline distribution.

    The baseline is treated as immutable once constructed.
    """

    def __init__(
        self,
        mean: float,
        variance: float,
        samples: int,
        converged: bool,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Initialize a baseline model.

        Parameters
        ----------
        mean : float
            Baseline mean (μ).

        variance : float
            Baseline variance (σ²).

        samples : int
            Number of samples used to estimate the baseline.

        converged : bool
            Whether Monte Carlo convergence was reached.

        metadata : dict
            Additional contextual information (backend, config).
        """

        self._validate(mean, variance, samples, converged)

        self.mean = mean
        self.variance = variance
        self.samples = samples
        self.converged = converged
        self.metadata = metadata

    @staticmethod
    def _validate(
        mean: float,
        variance: float,
        samples: int,
        converged: bool
    ) -> None:
        """Validate baseline parameters."""
        if samples <= 1:
            raise ValueError(
                "Baseline must be estimated from more than one sample"
            )

        if variance < 0:
            raise ValueError("Variance must be non-negative")

        if not converged:
            raise ValueError(
                "Baseline model cannot be created without convergence"
            )

    def as_dict(self) -> Dict[str, Any]:
        """
        Convert baseline model to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the baseline.
        """
        return {
            "mean": self.mean,
            "variance": self.variance,
            "samples": self.samples,
            "converged": self.converged,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaselineModel":
        """
        Construct a BaselineModel from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary containing baseline fields.

        Returns
        -------
        BaselineModel
            Instantiated baseline model.
        """

        required_fields = [
            "mean",
            "variance",
            "samples",
            "converged",
            "metadata",
        ]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return cls(
            mean=data["mean"],
            variance=data["variance"],
            samples=data["samples"],
            converged=data["converged"],
            metadata=data["metadata"],
        )

    def save(self, path: Path) -> None:
        """
        Serialize the baseline model to a YAML file.

        Parameters
        ----------
        path : Path
            Output path for the baseline YAML file.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            yaml.safe_dump(self.as_dict(), f)

    @classmethod
    def load(cls, path: Path) -> "BaselineModel":
        """
        Load a baseline model from a YAML file.

        Parameters
        ----------
        path : Path
            Path to baseline YAML file.

        Returns
        -------
        BaselineModel
            Loaded baseline model.
        """
        if not path.exists():
            raise FileNotFoundError(f"Baseline file not found: {path}")

        with path.open("r") as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)
