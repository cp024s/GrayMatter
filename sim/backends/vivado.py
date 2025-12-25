"""
Vivado simulation backend.

This backend implements the SimulationBackend interface
using Xilinx Vivado in batch mode to execute RTL simulation
and extract switching activity.

This file implements:
- Vivado invocation
- TCL script generation
- Workspace management

Simulation execution and activity parsing are implemented
in subsequent parts.
"""

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List

from sim.backends.base import SimulationBackend


class VivadoBackend(SimulationBackend):
    """
    Simulation backend using Xilinx Vivado.
    """

    def __init__(self) -> None:
        self.workdir: Path = None
        self.tcl_path: Path = None

    # --------------------------------------------------------
    # Setup / cleanup
    # --------------------------------------------------------

    def setup(self, sim_cfg: Dict[str, Any]) -> None:
        """
        Prepare a temporary working directory and TCL script.
        """
        self.workdir = Path(tempfile.mkdtemp(prefix="vivado_"))
        self.tcl_path = self.workdir / "run.tcl"

    def cleanup(self) -> None:
        """
        Remove temporary working directory.
        """
        if self.workdir and self.workdir.exists():
            shutil.rmtree(self.workdir)

    # --------------------------------------------------------
    # Vivado invocation
    # --------------------------------------------------------

    def _run_vivado(self) -> None:
        """
        Invoke Vivado in batch mode using the generated TCL script.
        """
        cmd = [
            "vivado",
            "-mode", "batch",
            "-source", str(self.tcl_path)
        ]

        subprocess.run(
            cmd,
            cwd=self.workdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    # --------------------------------------------------------
    # TCL generation (implemented in Part 2)
    # --------------------------------------------------------

    def _generate_tcl(self, sim_cfg: Dict[str, Any]) -> None:
        """
        Generate Vivado TCL script for simulation.

        Implemented in Part 2.
        """
        raise NotImplementedError

    # --------------------------------------------------------
    # Main backend entry point
    # --------------------------------------------------------

    def run(self, sim_cfg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single Vivado simulation and return switching activity.
        """
        self.setup(sim_cfg)

        try:
            self._generate_tcl(sim_cfg)
            self._run_vivado()

            # Parse activity output (implemented in Part 3)
            activity = self._parse_activity(sim_cfg)

            return activity

        finally:
            self.cleanup()

    # --------------------------------------------------------
    # Activity parsing (implemented in Part 3)
    # --------------------------------------------------------

    def _parse_activity(self, sim_cfg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse activity output and extract switching statistics.

        Implemented in Part 3.
        """
        raise NotImplementedError

    def _generate_tcl(self, sim_cfg: Dict[str, Any]) -> None:
        """
        Generate Vivado TCL script for RTL simulation and
        switching activity dumping.

        Expected sim_cfg keys:
            - rtl_files : list of RTL source paths
            - top       : top module name
            - sim_time  : simulation time (e.g., "1000ns")
            - activity  : "vcd" or "saif" (default: vcd)
        """

        rtl_files = [Path(f) for f in sim_cfg["rtl_files"]]
        top = sim_cfg["top"]
        sim_time = sim_cfg.get("sim_time", "1000ns")
        activity = sim_cfg.get("activity", "vcd").lower()

        if activity not in ("vcd", "saif"):
            raise ValueError("activity must be 'vcd' or 'saif'")

        lines = []

        # Create project (in-memory)
        lines.append("create_project sim_proj . -force")

        # Add RTL sources
        for rtl in rtl_files:
            lines.append(f"add_files {rtl.resolve()}")

        lines.append("update_compile_order -fileset sources_1")

        # Set top module
        lines.append(f"set_property top {top} [current_fileset]")

        # Launch simulation
        lines.append("launch_simulation")

        # Activity dumping
        if activity == "vcd":
            lines.append("open_vcd dump.vcd")
            lines.append("log_vcd *")
        else:
            lines.append("open_saif dump.saif")
            lines.append("log_saif *")

        # Run simulation
        lines.append(f"run {sim_time}")

        # Close activity
        if activity == "vcd":
            lines.append("close_vcd")
        else:
            lines.append("close_saif")

        # Exit Vivado
        lines.append("quit")

        # Write TCL file
        self.tcl_path.parent.mkdir(parents=True, exist_ok=True)
        with self.tcl_path.open("w") as f:
            f.write("\n".join(lines))

    def _parse_activity(self, sim_cfg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse activity output (VCD or SAIF) and extract
        switching activity statistics.

        Returns
        -------
        dict
            {
                "total_toggles": int,
                "cycles": int
            }
        """

        activity = sim_cfg.get("activity", "vcd").lower()
        clock_name = sim_cfg["clock"]

        if activity == "vcd":
            return self._parse_vcd(
                vcd_path=self.workdir / "dump.vcd",
                clock_name=clock_name
            )

        elif activity == "saif":
            return self._parse_saif(
                saif_path=self.workdir / "dump.saif"
            )

        else:
            raise ValueError("Unsupported activity type")

    # --------------------------------------------------------
    # VCD parsing (reuse logic from Icarus backend)
    # --------------------------------------------------------

    def _parse_vcd(
        self,
        vcd_path: Path,
        clock_name: str
    ) -> Dict[str, Any]:
        """
        Parse VCD file and extract switching activity.
        """

        if not vcd_path.exists():
            raise FileNotFoundError(f"VCD file not found: {vcd_path}")

        id_to_signal = {}
        signal_to_id = {}
        last_value = {}

        total_toggles = 0
        cycles = 0

        clock_id = None

        with vcd_path.open("r") as f:
            in_defs = True

            for line in f:
                line = line.strip()

                if in_defs:
                    if line.startswith("$var"):
                        parts = line.split()
                        sig_id = parts[3]
                        sig_name = parts[4]

                        id_to_signal[sig_id] = sig_name
                        signal_to_id[sig_name] = sig_id
                        last_value[sig_id] = None

                    if line == "$enddefinitions $end":
                        in_defs = False
                        clock_id = signal_to_id.get(clock_name)
                        if clock_id is None:
                            raise ValueError(
                                f"Clock '{clock_name}' not found in VCD"
                            )
                    continue

                if not line or line.startswith("#"):
                    continue

                if line[0] in ("0", "1", "x", "z"):
                    value = line[0]
                    sig_id = line[1:]
                elif line.startswith("b"):
                    parts = line.split()
                    value = parts[0][1:]
                    sig_id = parts[1]
                else:
                    continue

                prev = last_value.get(sig_id)
                if prev is not None and prev != value:
                    total_toggles += 1

                last_value[sig_id] = value

                if sig_id == clock_id:
                    if prev == "0" and value == "1":
                        cycles += 1

        if cycles == 0:
            raise RuntimeError("No clock cycles detected in VCD")

        return {
            "total_toggles": total_toggles,
            "cycles": cycles
        }

    # --------------------------------------------------------
    # SAIF parsing (simplified)
    # --------------------------------------------------------

    def _parse_saif(self, saif_path: Path) -> Dict[str, Any]:
        """
        Parse SAIF file and extract total toggle count.

        Note:
        SAIF does not encode cycles directly. Cycle count
        must be provided via sim_cfg or assumed constant.
        """

        if not saif_path.exists():
            raise FileNotFoundError(f"SAIF file not found: {saif_path}")

        total_toggles = 0

        with saif_path.open("r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("(T"):
                    # Example: (T 1234)
                    parts = line.replace("(", "").replace(")", "").split()
                    total_toggles += int(parts[1])

        # Cycles must be provided externally or normalized later
        cycles = int(sim_cfg.get("cycles", 1))

        return {
            "total_toggles": total_toggles,
            "cycles": cycles
        }
