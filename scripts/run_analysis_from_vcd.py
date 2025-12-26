#!/usr/bin/env python3

import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# --------------------------------------------------
# Ensure project root is on PYTHONPATH
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# --------------------------------------------------
# Project imports
# --------------------------------------------------
from analysis.metrics.toggle_metric import extract_toggle_counts
from analysis.statistics.baseline_model import build_baseline_distribution
from analysis.detector import run_detector
from analysis.reporting.image_report import UnifiedImageReport
from analysis.reporting.text_report import TextReportGenerator


def run_analysis(vcd_path: Path):
    """
    Run full hardware-trojan analysis starting from a VCD file.
    """

    if not vcd_path.exists():
        raise FileNotFoundError(f"VCD not found: {vcd_path}")

    # --------------------------------------------------
    # Step 1: Extract toggle counts from VCD
    # --------------------------------------------------
    toggle_data = extract_toggle_counts(vcd_path)

    clean_toggles = {
        sig: cnt for sig, cnt in toggle_data.items()
        if ".u_clean." in sig
    }

    trojan_toggles = {
        sig: cnt for sig, cnt in toggle_data.items()
        if ".u_trojan." in sig
    }

    if not clean_toggles or not trojan_toggles:
        raise RuntimeError("Failed to separate clean and trojan signals")

    # --------------------------------------------------
    # Step 2: Build baseline distribution (clean)
    # --------------------------------------------------
    baseline = build_baseline_distribution(clean_toggles)

    # --------------------------------------------------
    # Step 3: Compute baseline convergence
    # --------------------------------------------------
    baseline_samples = baseline["samples"]

    means = []
    variances = []

    for i in range(5, len(baseline_samples) + 1):
        subset = baseline_samples[:i]
        means.append(float(np.mean(subset)))
        variances.append(float(np.var(subset)))

    convergence = {
        "means": means,
        "variances": variances,
    }

    # --------------------------------------------------
    # Step 4: Run detector
    # --------------------------------------------------
    results = run_detector(
        baseline=baseline,
        observed=trojan_toggles
    )

    # --------------------------------------------------
    # Step 5: Attach convergence + metadata
    # --------------------------------------------------
    results["convergence"] = convergence
    results["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results["samples"] = len(clean_toggles)

    return results


# --------------------------------------------------
# Entry point
# --------------------------------------------------
if __name__ == "__main__":

    vcd_file = PROJECT_ROOT / "alu_secure.vcd"

    results = run_analysis(vcd_file)

    plots_dir = PROJECT_ROOT / "results" / "plots"
    summaries_dir = PROJECT_ROOT / "results" / "summaries"

    plots_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir.mkdir(parents=True, exist_ok=True)

    image_report = UnifiedImageReport(plots_dir)
    image_path = image_report.generate(results)

    text_report = TextReportGenerator(summaries_dir)
    text_path = text_report.generate(results)

    print("[OK] Real analysis completed")
    print(f" - Image report : {image_path}")
    print(f" - Text report  : {text_path}")
