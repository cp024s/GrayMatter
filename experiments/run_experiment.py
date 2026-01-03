#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path

# -----------------------------------------------------------------------------
# Project root
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]

# -----------------------------------------------------------------------------
# RTL paths
# -----------------------------------------------------------------------------
RTL_COMMON = ROOT / "rtl" / "common" / "alu_trojan_secure.v"
RTL_CLEAN  = ROOT / "rtl" / "clean" / "alu_clean_secure.v"
TB_FILE    = ROOT / "tb" / "tb_alu_secure.sv"

RESULTS = ROOT / "results"


def build_iverilog_cmd(variant: str, out_dir: Path):
    cmd = ["iverilog", "-g2012"]

    # ---------------------------------------------------------
    # Macro control
    # ---------------------------------------------------------
    if variant != "clean":
        cmd += ["-DINCLUDE_TROJAN", f"-DTROJAN_{variant.upper()}"]

    # ---------------------------------------------------------
    # Output binary
    # ---------------------------------------------------------
    sim_out = out_dir / "sim.out"
    cmd += ["-o", str(sim_out)]

    # ---------------------------------------------------------
    # RTL (order matters)
    # ---------------------------------------------------------
    cmd += [
        str(RTL_COMMON),
        str(RTL_CLEAN),
    ]

    if variant != "clean":
        variant_num = variant[1:]  # v1 -> 1
        trojan_rtl = (
            ROOT
            / "rtl"
            / "trojans"
            / f"variant_{variant_num}"
            / f"design_trojan_variant_{variant_num}.v"
        )
        cmd.append(str(trojan_rtl))

    # ---------------------------------------------------------
    # Testbench LAST
    # ---------------------------------------------------------
    cmd.append(str(TB_FILE))

    return cmd, sim_out


def run_simulation(variant: str):
    out_dir = RESULTS / variant
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[RUN] Variant : {variant}")

    cmd, sim_out = build_iverilog_cmd(variant, out_dir)

    print("[INFO] Compiling simulation...")
    subprocess.run(cmd, check=True)

    print("[INFO] Running simulation...")
    # IMPORTANT: run from out_dir so VCD lands here
    subprocess.run([str(sim_out)], cwd=out_dir, check=True)

    print("[OK] Simulation completed")


def main():
    parser = argparse.ArgumentParser(description="Simulation runner")
    parser.add_argument(
        "--variant",
        required=True,
        choices=["clean", "v0", "v1", "v2", "v3"],
    )
    args = parser.parse_args()

    run_simulation(args.variant)


if __name__ == "__main__":
    main()
