#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# --------------------------------------------------
# Project root
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# --------------------------------------------------
# Project imports
# --------------------------------------------------
from analysis.reporting.image_report import UnifiedImageReport
from analysis.reporting.text_report import TextReportGenerator
from scripts.run_analysis_from_vcd import run_analysis


# --------------------------------------------------
# RTL MAP (CLEAN + TROJAN PAIRS)
# --------------------------------------------------
RTL_MAP = {
    "clean": (
        PROJECT_ROOT / "rtl/clean/alu_clean_secure.v",
        PROJECT_ROOT / "rtl/clean/alu_trojan_secure_stub.v",
    ),
    "v1": (
        PROJECT_ROOT / "rtl/clean/alu_clean_secure.v",
        PROJECT_ROOT / "rtl/trojans/variant_1/design_trojan_variant_1.v",
    ),
    "v2": (
        PROJECT_ROOT / "rtl/clean/alu_clean_secure.v",
        PROJECT_ROOT / "rtl/trojans/variant_2/design_trojan_variant_2.v",
    ),
    "v3": (
        PROJECT_ROOT / "rtl/clean/alu_clean_secure.v",
        PROJECT_ROOT / "rtl/trojans/variant_3/design_trojan_variant_3.v",
    ),
}

TB_FILE = PROJECT_ROOT / "tb/tb_alu_secure.sv"


# --------------------------------------------------
# Simulation runner (Icarus Verilog)
# --------------------------------------------------
def run_simulation(clean_rtl: Path,
                   trojan_rtl: Path,
                   out_dir: Path,
                   seed: int,
                   cycles: int) -> Path:
    """
    Compile and run simulation, return VCD path.
    """

    sim_exe = out_dir / "sim.out"
    vcd_path = out_dir / "alu.vcd"

    # Compile
    cmd_compile = [
        "iverilog",
        "-g2012",
        "-o", str(sim_exe),
        str(TB_FILE),
        str(clean_rtl),
        str(trojan_rtl),
    ]

    print("[INFO] Compiling simulation...")
    subprocess.run(cmd_compile, check=True)

    # Run
    cmd_run = ["vvp", str(sim_exe)]

    print("[INFO] Running simulation...")
    env = dict(**dict())
    env["SEED"] = hex(seed)
    env["NUM_CYCLES"] = str(cycles)

    subprocess.run(cmd_run, cwd=out_dir, check=True)

    if not vcd_path.exists():
        raise RuntimeError("Simulation completed but VCD was not generated")

    return vcd_path


# --------------------------------------------------
# Main experiment driver
# --------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Run hardware Trojan experiment (clean vs variants)"
    )
    parser.add_argument(
        "--variant",
        required=True,
        choices=RTL_MAP.keys(),
        help="RTL variant to test",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=10000,
        help="Number of simulation cycles",
    )
    parser.add_argument(
        "--seed",
        type=lambda x: int(x, 0),
        default=0xC0FFEE,
        help="Random seed (hex or int)",
    )

    args = parser.parse_args()

    clean_rtl, trojan_rtl = RTL_MAP[args.variant]

    # Validate RTL existence
    for rtl in (clean_rtl, trojan_rtl):
        if not rtl.exists():
            raise FileNotFoundError(f"RTL not found: {rtl}")

    if not TB_FILE.exists():
        raise FileNotFoundError(f"Testbench not found: {TB_FILE}")

    # --------------------------------------------------
    # Output directories
    # --------------------------------------------------
    out_root = PROJECT_ROOT / "results" / args.variant
    plots_dir = out_root / "plots"
    summaries_dir = out_root / "summaries"

    plots_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir.mkdir(parents=True, exist_ok=True)

    print(f"[RUN] Variant: {args.variant}")
    print(f"[RUN] Cycles : {args.cycles}")
    print(f"[RUN] Seed   : {hex(args.seed)}")

    # --------------------------------------------------
    # Step 1: Simulation
    # --------------------------------------------------
    vcd_file = run_simulation(
        clean_rtl=clean_rtl,
        trojan_rtl=trojan_rtl,
        out_dir=out_root,
        seed=args.seed,
        cycles=args.cycles,
    )

    # --------------------------------------------------
    # Step 2: Analysis
    # --------------------------------------------------
    results = run_analysis(vcd_file)

    # Attach experiment metadata
    results["experiment"] = {
        "variant": args.variant,
        "seed": hex(args.seed),
        "cycles": args.cycles,
        "clean_rtl": str(clean_rtl),
        "trojan_rtl": str(trojan_rtl),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # --------------------------------------------------
    # Step 3: Reports
    # --------------------------------------------------
    image_report = UnifiedImageReport(plots_dir)
    image_path = image_report.generate(results)

    text_report = TextReportGenerator(summaries_dir)
    text_path = text_report.generate(results)

    print("[OK] Experiment completed successfully")
    print(f" - VCD   : {vcd_file}")
    print(f" - Image : {image_path}")
    print(f" - Text  : {text_path}")


# --------------------------------------------------
# Entry point
# --------------------------------------------------
if __name__ == "__main__":
    main()
