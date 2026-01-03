#!/usr/bin/env python3

import sys
from pathlib import Path

# ------------------------------------------------------------
# FIX PYTHON PATH (THIS IS THE KEY LINE)
# ------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import argparse
import json

from analysis.metrics.toggle_metric import extract_toggle_counts
from analysis.detector import run_detector
from analysis.reporting.image_report import UnifiedImageReport
from analysis.reporting.text_report import TextReportGenerator


RESULTS_DIR = ROOT / "results"
BASELINE_FILE = RESULTS_DIR / "clean" / "baseline.json"


# ------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Run Trojan analysis from VCD")
    p.add_argument("--variant", required=True,
                   help="clean | v0 | v1 | v2")
    p.add_argument("--vcd", required=True,
                   help="Path to VCD file")
    return p.parse_args()


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    args = parse_args()

    variant = args.variant
    vcd_path = Path(args.vcd)

    out_dir = RESULTS_DIR / variant
    plots_dir = out_dir / "plots"
    summaries_dir = out_dir / "summaries"

    plots_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Extract toggles
    # --------------------------------------------------------
    toggles = extract_toggle_counts(vcd_path)
    total_activity = sum(toggles.values())

    print(f"[DEBUG] Total toggles ({variant}): {total_activity}")

    # --------------------------------------------------------
    # CLEAN: build baseline
    # --------------------------------------------------------
    if variant == "clean":
        baseline = {}

        for sig, val in toggles.items():
            baseline[sig] = {
                "mean": float(val),
                "std": 0.0,
                "iqr_threshold": float(val),
                "samples": [float(val)],
            }

        baseline["__global_activity__"] = total_activity

        BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with BASELINE_FILE.open("w") as f:
            json.dump(baseline, f, indent=2)

        results = run_detector(baseline, toggles)

    # --------------------------------------------------------
    # NON-CLEAN: load baseline
    # --------------------------------------------------------
    else:
        if not BASELINE_FILE.exists():
            raise RuntimeError("Clean baseline not found. Run clean first.")

        with BASELINE_FILE.open() as f:
            baseline = json.load(f)

        clean_global = baseline.get("__global_activity__", None)

        results = run_detector(baseline, toggles)

        # ----------------------------------------------------
        # GLOBAL ACTIVITY POSITIVE CONTROL
        # ----------------------------------------------------
        if clean_global is not None:
            if total_activity > 1.5 * clean_global:
                results["decision"]["trojan_detected"] = True
                results["decision"]["confidence"] = "high"
                results["decision"]["threshold"] = "global activity (1.5× clean)"

    # --------------------------------------------------------
    # Reporting
    # --------------------------------------------------------
    img_report = UnifiedImageReport(plots_dir)
    txt_report = TextReportGenerator(summaries_dir)

    img_report.generate(results)
    txt_report.generate(results)

    print(f"[OK] Analysis complete for variant: {variant}")


if __name__ == "__main__":
    main()
