#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RTL_COMMON = ROOT / "rtl" / "common" / "alu_trojan_secure.v"
RTL_CLEAN  = ROOT / "rtl" / "clean" / "alu_clean_secure.v"
TB_FILE    = ROOT / "tb" / "tb_alu_secure.sv"

RESULTS_DIR = ROOT / "results"


def build_iverilog_cmd(variant: str, out_dir: Path):
    cmd = ["iverilog", "-g2012"]

    # ======================
    # Macro control
    # ======================
    if variant != "clean":
        cmd += ["-DINCLUDE_TROJAN"]
        cmd += [f"-DTROJAN_{variant.upper()}"]

    # ======================
    # Output
    # ======================
    sim_out = out_dir / "sim.out"
    cmd += ["-o", str(sim_out)]

    # ======================
    # RTL files (ORDER MATTERS)
    # ======================
    cmd += [
        str(RTL_COMMON),
        str(RTL_CLEAN),
    ]

    if variant != "clean":
        trojan_rtl = ROOT / "rtl" / "trojans" / variant / f"design_trojan_{variant}.v"
        cmd.append(str(trojan_rtl))

    # ======================
    # Testbench (LAST)
    # ======================
    cmd.append(str(TB_FILE))

    return cmd, sim_out


def run_simulation(variant: str):
    out_dir = RESULTS_DIR / variant
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[RUN] Variant : {variant}")

    cmd, sim_out = build_iverilog_cmd(variant, out_dir)

    print("[INFO] Compiling simulation...")
    subprocess.run(cmd, check=True)

    print("[INFO] Running simulation...")
    subprocess.run([str(sim_out)], check=True)

    print("[OK] Simulation completed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--variant",
        choices=["clean", "v1", "v2", "v3"],
        required=True
    )
    args = parser.parse_args()

    run_simulation(args.variant)


if __name__ == "__main__":
    main()
