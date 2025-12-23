"""
Icarus Verilog simulation backend.

This backend implements the SimulationBackend interface
using Icarus Verilog (iverilog + vvp) to execute RTL
simulations and extract switching activity from VCD files.

This file implements:
- tool invocation
- workspace management
- simulation execution

VCD parsing and toggle extraction are implemented
in Part 2.
"""

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List

from sim.backends.base import SimulationBackend


class IcarusBackend(SimulationBackend):
    """
    Simulation backend using Icarus Verilog.
    """

    def __init__(self) -> None:
        self.workdir: Path = None

    # --------------------------------------------------------
    # Setup / cleanup
    # --------------------------------------------------------

    def setup(self, sim_cfg: Dict[str, Any]) -> None:
        """
        Prepare a temporary working directory for simulation.
        """
        self.workdir = Path(tempfile.mkdtemp(prefix="iverilog_"))

    def cleanup(self) -> None:
        """
        Remove temporary working directory.
        """
        if self.workdir and self.workdir.exists():
            shutil.rmtree(self.workdir)

    # --------------------------------------------------------
    # Tool invocation helpers
    # --------------------------------------------------------

    def _compile(
        self,
        rtl_files: List[Path],
        top: str,
        output: Path
    ) -> None:
        """
        Compile RTL using iverilog.

        Parameters
        ----------
        rtl_files : list of Path
            RTL source files.

        top : str
            Top module name.

        output : Path
            Output executable path.
        """
        cmd = [
            "iverilog",
            "-g2012",
            "-s", top,
            "-o", str(output)
        ] + [str(f) for f in rtl_files]

        subprocess.run(
            cmd,
            cwd=self.workdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _run_simulation(self, executable: Path) -> None:
        """
        Run compiled simulation using vvp.
        """
        cmd = ["vvp", str(executable)]

        subprocess.run(
            cmd,
            cwd=self.workdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    # --------------------------------------------------------
    # Main backend entry point
    # --------------------------------------------------------

    def run(self, sim_cfg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single RTL simulation and return switching activity.

        Parameters
        ----------
        sim_cfg : dict
            Simulation configuration. Expected keys:
                - rtl_files : list of paths
                - top       : top module name
                - vcd_file  : VCD output file name
                - clock     : clock signal name

        Returns
        -------
        dict
            Parsed switching activity data.
        """

        self.setup(sim_cfg)

        try:
            rtl_files = [Path(f) for f in sim_cfg["rtl_files"]]
            top = sim_cfg["top"]
            vcd_name = sim_cfg.get("vcd_file", "dump.vcd")

            exe = self.workdir / "sim.out"
            vcd_path = self.workdir / vcd_name

            # Compile
            self._compile(
                rtl_files=rtl_files,
                top=top,
                output=exe
            )

            # Run simulation
            self._run_simulation(executable=exe)

            # Parse VCD and extract activity (Part 2)
            activity = self._parse_vcd(
                vcd_path=vcd_path,
                clock_name=sim_cfg["clock"]
            )

            return activity

        finally:
            self.cleanup()

    # --------------------------------------------------------
    # VCD parsing (implemented in Part 2)
    # --------------------------------------------------------

    def _parse_vcd(
        self,
        vcd_path: Path,
        clock_name: str
    ) -> Dict[str, Any]:
        """
        Parse VCD file and extract switching activity.

        Implemented in Part 2.
        """
        raise NotImplementedError

    def _parse_vcd(
        self,
        vcd_path: Path,
        clock_name: str
    ) -> Dict[str, Any]:
        """
        Parse a VCD file and extract switching activity.

        Parameters
        ----------
        vcd_path : Path
            Path to the VCD file.
        clock_name : str
            Name of the clock signal.

        Returns
        -------
        dict
            Dictionary containing:
                - total_toggles : int
                - cycles        : int
        """

        if not vcd_path.exists():
            raise FileNotFoundError(f"VCD file not found: {vcd_path}")

        # Map VCD identifiers to signal names
        id_to_signal = {}
        signal_to_id = {}

        # Track last known value of each signal
        last_value = {}

        total_toggles = 0
        cycles = 0

        clock_id = None
        last_clock_value = None

        with vcd_path.open("r") as f:
            in_definitions = True

            for line in f:
                line = line.strip()

                # -------------------------------
                # Header / definitions
                # -------------------------------
                if in_definitions:
                    if line.startswith("$var"):
                        # Example:
                        # $var wire 1 ! clk $end
                        parts = line.split()
                        signal_id = parts[3]
                        signal_name = parts[4]

                        id_to_signal[signal_id] = signal_name
                        signal_to_id[signal_name] = signal_id
                        last_value[signal_id] = None

                    if line == "$enddefinitions $end":
                        in_definitions = False
                        clock_id = signal_to_id.get(clock_name)
                        if clock_id is None:
                            raise ValueError(
                                f"Clock signal '{clock_name}' not found in VCD"
                            )
                    continue

                # -------------------------------
                # Value changes
                # -------------------------------
                if not line or line.startswith("#"):
                    continue

                # Scalar change: e.g. 1!
                if line[0] in ("0", "1", "x", "z"):
                    value = line[0]
                    signal_id = line[1:]

                # Vector change: e.g. b1010 !
                elif line.startswith("b"):
                    parts = line.split()
                    value = parts[0][1:]
                    signal_id = parts[1]

                else:
                    continue

                prev = last_value.get(signal_id)

                if prev is not None and prev != value:
                    total_toggles += 1

                last_value[signal_id] = value

                # Clock cycle counting (rising edge)
                if signal_id == clock_id:
                    if prev == "0" and value == "1":
                        cycles += 1

                    last_clock_value = value

        if cycles == 0:
            raise RuntimeError(
                "No clock cycles detected; check clock name and VCD"
            )

        return {
            "total_toggles": total_toggles,
            "cycles": cycles
        }
