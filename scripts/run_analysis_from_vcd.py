#!/usr/bin/env python3

import argparse
from pathlib import Path
from datetime import datetime

from analysis.metrics.toggle_metric import extract_toggle_counts
from analysis.statistics.baseline_model import build_baseline_distribution
from analysis.detector import run_detector
from analysis.reporting.text_report import TextReportGenerator
from analysis.reporting.image_report import UnifiedImageReport


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def collect_clean_baseline(clean_root: Path) -> list[dict]:
    """
    Collect toggle counts from all clean seed runs.
    Expects:
      results/clean/seed_*/alu_secure.vcd
    """
    runs = []

    seed_dirs = sorted(p for p in clean_root.iterdir() if p.is_dir())
    if not seed_dirs:
        raise RuntimeError("No clean seed directories found.")

    for d in seed_dirs:
        vcd = d / "alu_secure.vcd"
        if not vcd.exists():
            continue
        runs.append(extract_toggle_counts(vcd))

    if not runs:
        raise RuntimeError("No clean VCDs found for baseline.")

    return runs


def main():
    parser = argparse.ArgumentParser(description="Analyze VCD against baseline")
    parser.add_argument("--variant", required=True)
    parser.add_argument("--vcd", required=True)
    args = parser.parse_args()

    variant = args.variant
    vcd_path = Path(args.vcd)

    # --------------------------------------------------
    # Load baseline (MULTI-RUN)
    # --------------------------------------------------
    clean_root = RESULTS / "clean"
    baseline_runs = collect_clean_baseline(clean_root)
    baseline = build_baseline_distribution(baseline_runs)

    # --------------------------------------------------
    # Observed toggles
    # --------------------------------------------------
    observed = extract_toggle_counts(vcd_path)

    total_toggles = sum(observed.values())
    print(f"[DEBUG] Total toggles ({variant}): {total_toggles}")

    # --------------------------------------------------
    # Run detector
    # --------------------------------------------------
    results = run_detector(baseline, observed)
    results["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --------------------------------------------------
    # Global positive control (keep this)
    # --------------------------------------------------
    clean_mean_total = sum(
        sum(run.values()) for run in baseline_runs
    ) / len(baseline_runs)

    if total_toggles > 1.5 * clean_mean_total:
        results["decision"]["trojan_detected"] = True
        results["decision"]["threshold"] = "global activity (1.5× clean)"
        results["decision"]["confidence"] = "high"
        results["decision"]["primary_signal"] = None
        results["decision"]["primary_deviation"] = None

    # --------------------------------------------------
    # Reports
    # --------------------------------------------------
    out_dir = RESULTS / variant
    (out_dir / "summaries").mkdir(parents=True, exist_ok=True)
    (out_dir / "plots").mkdir(parents=True, exist_ok=True)

    TextReportGenerator(out_dir / "summaries").generate(results)
    UnifiedImageReport(out_dir / "plots").generate(results)

    print(f"[OK] Analysis complete for variant: {variant}")


if __name__ == "__main__":
    main()
