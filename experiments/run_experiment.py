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
# Imports from project
# --------------------------------------------------
from analysis.reporting.image_report import UnifiedImageReport
from analysis.reporting.text_report import TextReportGenerator
from scripts.run_analysis_from_vcd import run_analysis


# --------------------------------------------------
# RTL selection
# --------------------------------------------------
RTL_MAP = {
    "clean": PROJECT_ROOT / "rtl/clean/alu_clean_secure.v",
    "v1": PROJECT_ROOT / "rtl/trojans/variant_1/design_trojan_variant_1.v",
    "v2": PROJECT_ROOT / "rtl/trojans/variant_2/design_trojan_variant_2.v",
    "v3": PROJECT_ROOT / "rtl/trojans/variant_3/design_trojan_variant_3.v",
}

TB_FILE = PROJECT_ROOT / "tb/tb_alu_secure.sv"


# --------------------------------------------------
# Simulation runner (Icarus)
# --------------------------------------------------
def run_simulation(rtl_file: Path, out_dir: Path, seed: int, cycles: int):
    vcd_path = out_dir / "alu.vcd"
    sim_exe = out_dir / "sim.out"

    cmd_compile = [
        "iverilog",
        "-g2012",
        "-o", str(sim_exe),
        str(TB_FILE),
        str(rtl_file),
    ]

    cmd_run = [
        "vvp",
        str(sim_exe),
    ]

    print("[INFO] Compiling simulation...")
    subprocess.run(cmd_compile, check=True)

    print("[INFO] Running simulation...")
    env = dict(**dict())
    env["SEED"] = hex(seed)
    env["NUM_CYCLES"] = str(cycles)

    subprocess.run(cmd_run, check=True, cwd=out_dir)

    if not vcd_path.exists():
        raise RuntimeError("VCD file not generated")

    return vcd_path


# --------------------------------------------------
# Main experiment driver
# --------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Run hardware trojan experiment")
    parser.add_argument("--variant", required=True, choices=RTL_MAP.keys())
    parser.add_argument("--cycles", type=int, default=10000)
    parser.add_argument("--seed", type=lambda x: int(x, 0), default=0xC0FFEE)
    args = parser.parse_args()

    rtl_file = RTL_MAP[args.variant]
    if not rtl_file.exists():
        raise FileNotFoundError(f"RTL not found: {rtl_file}")

    # --------------------------------------------------
    # Output directories
    # --------------------------------------------------
    out_root = PROJECT_ROOT / "results" / args.variant
    plots_dir = out_root / "plots"
    summaries_dir = out_root / "summaries"

    for d in [out_root, plots_dir, summaries_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print(f"[RUN] Variant: {args.variant}")
    print(f"[RUN] Cycles : {args.cycles}")
    print(f"[RUN] Seed   : {hex(args.seed)}")

    # --------------------------------------------------
    # Step 1: Simulation
    # --------------------------------------------------
    vcd_file = run_simulation(
        rtl_file=rtl_file,
        out_dir=out_root,
        seed=args.seed,
        cycles=args.cycles,
    )

    # --------------------------------------------------
    # Step 2: Analysis
    # --------------------------------------------------
    results = run_analysis(vcd_file)

    # Attach metadata
    results["experiment"] = {
        "variant": args.variant,
        "seed": hex(args.seed),
        "cycles": args.cycles,
        "rtl": str(rtl_file),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # --------------------------------------------------
    # Step 3: Reports
    # --------------------------------------------------
    image_report = UnifiedImageReport(plots_dir)
    image_path = image_report.generate(results)

    text_report = TextReportGenerator(summaries_dir)
    text_path = text_report.generate(results)

    print("[OK] Experiment completed")
    print(f" - VCD   : {vcd_file}")
    print(f" - Image : {image_path}")
    print(f" - Text  : {text_path}")


if __name__ == "__main__":
    main()
