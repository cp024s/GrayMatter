#!/usr/bin/env python3

import sys
from pathlib import Path

# --------------------------------------------------
# Ensure project root is on PYTHONPATH
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# --------------------------------------------------
# Standard library imports
# --------------------------------------------------
from datetime import datetime
import numpy as np

# --------------------------------------------------
# Project imports (AFTER path fix)
# --------------------------------------------------
from analysis.reporting.image_report import UnifiedImageReport
from analysis.reporting.text_report import TextReportGenerator


def generate_mock_results():
    """
    Generate mock results that fully satisfy the reporting contract.
    This is for visualization and layout validation ONLY.
    """

    # --------------------------------------------------
    # Fake baseline samples (clean design)
    # --------------------------------------------------
    baseline_samples = np.random.normal(
        loc=12.0, scale=0.8, size=800
    ).tolist()

    # --------------------------------------------------
    # Fake observed samples (Trojan-infected)
    # --------------------------------------------------
    observed_samples = np.random.normal(
        loc=15.0, scale=0.9, size=200
    ).tolist()

    # --------------------------------------------------
    # Monte Carlo convergence history
    # --------------------------------------------------
    means = np.cumsum(baseline_samples) / np.arange(1, len(baseline_samples) + 1)
    variances = [
        np.var(baseline_samples[:i]) for i in range(10, len(baseline_samples), 10)
    ]

    # --------------------------------------------------
    # Ranked anomaly list (matches detector output)
    # --------------------------------------------------
    anomalies = [
        {
            "rank": 1,
            "signal": "trigger_counter",
            "deviation": 45900.0,
            "z_score": 4.8,
        },
        {
            "rank": 2,
            "signal": "trojan_active",
            "deviation": 13700.0,
            "z_score": 3.6,
        },
        {
            "rank": 3,
            "signal": "payload_mask",
            "deviation": 10300.0,
            "z_score": 3.1,
        },
    ]

    # --------------------------------------------------
    # Assemble final results dictionary
    # --------------------------------------------------
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "total_signals": len(anomalies),
        "samples": len(baseline_samples),

        "statistics": {
            "mean": float(np.mean(baseline_samples)),
            "median": float(np.median(baseline_samples)),
            "std": float(np.std(baseline_samples)),
            "max": float(np.max(baseline_samples)),
            "iqr_threshold": float(
                np.percentile(baseline_samples, 75)
                + 1.5 * (
                    np.percentile(baseline_samples, 75)
                    - np.percentile(baseline_samples, 25)
                )
            ),
        },

        "baseline_samples": baseline_samples,
        "observed_samples": observed_samples,

        "convergence": {
            "means": means[::10].tolist(),
            "variances": variances,
        },

        "anomalies": anomalies,

        "thresholds": {
            "z_threshold": 3.0
        },

        "decision": {
            "trojan_detected": True,

            "primary_signal": "trigger_counter",
            "primary_deviation": 45900.0,

            "threshold": "25%",
            "z_score": 4.8,
            "confidence": "99.9%",
            "observed": round(float(np.mean(observed_samples)), 3),
        },  
    }

    return results


# --------------------------------------------------
# Entry point
# --------------------------------------------------
if __name__ == "__main__":
    results = generate_mock_results()

    plots_dir = Path("results/plots")
    summaries_dir = Path("results/summaries")

    image_report = UnifiedImageReport(plots_dir)
    image_path = image_report.generate(results)

    text_report = TextReportGenerator(summaries_dir)
    text_path = text_report.generate(results)

    print("[OK] Reports generated:")
    print(f" - Image report : {image_path}")
    print(f" - Text report  : {text_path}")
