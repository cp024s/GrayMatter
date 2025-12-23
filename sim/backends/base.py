"""
Simulation backend interface.

This module defines the abstract base class that all
simulation backends must implement. It enforces a
tool-agnostic contract between simulation and analysis.

Backends are responsible for:
- invoking the simulator
- collecting switching activity
- returning parsed activity data

They must NOT:
- perform statistical analysis
- compute metrics
- apply thresholds
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class SimulationBackend(ABC):
    """
    Abstract base class for simulation backends.
    """

    @abstractmethod
    def run(self, sim_cfg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single simulation and return switching activity.

        Parameters
        ----------
        sim_cfg : dict
            Simulation configuration parameters.

        Returns
        -------
        dict
            Parsed switching activity data with the minimum structure:
                {
                    "total_toggles": int,
                    "cycles": int
                }

        Notes
        -----
        - This method must be deterministic with respect to sim_cfg
          and random seed.
        - Additional fields may be returned, but required keys
          must always be present.
        """
        pass

    def setup(self, sim_cfg: Dict[str, Any]) -> None:
        """
        Optional setup hook executed before simulation runs.

        Parameters
        ----------
        sim_cfg : dict
            Simulation configuration parameters.
        """
        return None

    def cleanup(self) -> None:
        """
        Optional cleanup hook executed after simulation runs.
        """
        return None
