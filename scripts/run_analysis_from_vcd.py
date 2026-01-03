#!/usr/bin/env python3

import sys
from pathlib import Path

# -----------------------------------------------------------------------------
# Ensure project root is on PYTHONPATH
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import argparse
import pandas as pd

# Now imports work
from analysis.detector import HardwareTrojanDetector
from analysis.reporting.image_report import generate_image_report
from analysis.reporting.text_report import generate_text_report



def main():
    parser = argparse.ArgumentParser(description="Analyze VCD and generate reports")
    parser.add_argument("--variant", required=True, help="clean / v0 / v1 / v2 / v3")
    parser.add_argument("--vcd", required=True, help="Path to VCD file")
    args = parser.parse_args()

    # -------------------------------------------------------------------------
    # Output directories (STRICTLY per variant)
    # -------------------------------------------------------------------------
    base_out = Path("results") / args.variant

    plots_dir   = base_out / "plots"
    summary_dir = base_out / "summaries"
    raw_dir     = base_out / "raw_metrics"

    plots_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Run detector
    # -------------------------------------------------------------------------
    detector = HardwareTrojanDetector(vcd_path=args.vcd)
    metrics_df = detector.run()

    # -------------------------------------------------------------------------
    # Store raw metrics (CRITICAL)
    # -------------------------------------------------------------------------
    metrics_path = raw_dir / "signal_metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)

    # -------------------------------------------------------------------------
    # Generate reports
    # -------------------------------------------------------------------------
    generate_image_report(
        metrics_df,
        output_path=plots_dir / "hardware_trojan_analysis_report.png"
    )

    generate_text_report(
        metrics_df,
        output_path=summary_dir / "hardware_trojan_report.txt"
    )

    print(f"[OK] Analysis complete for variant: {args.variant}")


if __name__ == "__main__":
    main()
