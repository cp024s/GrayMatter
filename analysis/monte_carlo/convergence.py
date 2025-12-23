"""
Monte Carlo convergence tracking.

This module implements convergence logic for Monte Carlo
sampling based on stabilization of the running mean (μ)
and variance (σ²) of a sequence of scalar observations.

It answers the question:
    "Have we sampled enough to trust the baseline model?"

This module must NOT:
- generate samples
- apply detection thresholds
- perform hypothesis testing
"""

from typing import Optional
import math


class ConvergenceTracker:
    """
    Tracks convergence of mean and variance for a stream
    of scalar observations.

    Convergence is declared only if both mean and variance
    remain within specified tolerances for a fixed number
    of consecutive batches.
    """

    def __init__(
        self,
        mean_eps: float,
        var_eps: float,
        stable_batches: int
    ) -> None:
        """
        Initialize the convergence tracker.

        Parameters
        ----------
        mean_eps : float
            Tolerance for mean convergence (ε_μ).

        var_eps : float
            Tolerance for variance convergence (ε_σ).

        stable_batches : int
            Number of consecutive batches required
            to declare convergence.
        """

        if mean_eps <= 0 or var_eps <= 0:
            raise ValueError("Convergence tolerances must be positive")

        if stable_batches <= 0:
            raise ValueError("stable_batches must be positive")

        self.mean_eps = mean_eps
        self.var_eps = var_eps
        self.stable_batches_required = stable_batches

        # Running statistics
        self._count = 0
        self._mean = 0.0
        self._m2 = 0.0  # Sum of squared deviations (Welford)

        # Previous batch statistics
        self._prev_mean: Optional[float] = None
        self._prev_variance: Optional[float] = None

        # Stability tracking
        self._stable_count = 0

    def update(self, value: float) -> None:
        """
        Update running statistics with a new observation.

        Parameters
        ----------
        value : float
            New scalar observation X_i.
        """

        self._count += 1

        delta = value - self._mean
        self._mean += delta / self._count
        delta2 = value - self._mean
        self._m2 += delta * delta2

    def variance(self) -> float:
        """
        Return the current running variance (σ²).

        Returns
        -------
        float
            Sample variance estimate.

        Raises
        ------
        RuntimeError
            If fewer than two samples are available.
        """

        if self._count < 2:
            raise RuntimeError("Variance requires at least two samples")

        return self._m2 / (self._count - 1)

    def mean(self) -> float:
        """
        Return the current running mean (μ).

        Returns
        -------
        float
            Running mean.
        """

        return self._mean

    def check_convergence(self) -> bool:
        """
        Check whether convergence criteria are satisfied.

        Convergence is declared if the change in mean and
        variance relative to the previous check is below
        the specified tolerances for a sufficient number
        of consecutive checks.

        Returns
        -------
        bool
            True if convergence has been reached, False otherwise.
        """

        # Cannot check convergence without variance
        if self._count < 2:
            return False

        current_mean = self.mean()
        current_variance = self.variance()

        if self._prev_mean is None or self._prev_variance is None:
            self._prev_mean = current_mean
            self._prev_variance = current_variance
            self._stable_count = 0
            return False

        mean_diff = abs(current_mean - self._prev_mean)
        var_diff = abs(current_variance - self._prev_variance)

        if mean_diff < self.mean_eps and var_diff < self.var_eps:
            self._stable_count += 1
        else:
            self._stable_count = 0

        self._prev_mean = current_mean
        self._prev_variance = current_variance

        return self._stable_count >= self.stable_batches_required

    def status(self) -> dict:
        """
        Return current convergence status and statistics.

        Returns
        -------
        dict
            Dictionary containing count, mean, variance,
            and stability information.
        """

        variance = None
        if self._count >= 2:
            variance = self.variance()

        return {
            "samples": self._count,
            "mean": self._mean,
            "variance": variance,
            "stable_batches": self._stable_count,
            "stable_required": self.stable_batches_required
        }
