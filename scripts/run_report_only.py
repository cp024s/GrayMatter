import sys
from pathlib import Path
from analysis.reporting.text_report import TextReportGenerator
sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
from datetime import datetime

from analysis.reporting.image_report import UnifiedImageReport

def generate_mock_results():
    # Fake baseline samples (clean design)
    baseline_samples = np.random.normal(
        loc=12.0, scale=0.8, size=800
    ).tolist()

    # Fake observed samples (Trojan-infected)
    observed_samples = np.random.normal(
        loc=15.0, scale=0.9, size=200
    ).tolist()

    # Fake convergence history
    means = np.cumsum(baseline_samples) / np.arange(1, len(baseline_samples) + 1)
    variances = [
        np.var(baseline_samples[:i]) for i in range(10, len(baseline_samples), 10)
    ]

    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "total_signals": 3,   # <-- ADD THIS LINE

        "statistics": {
            "mean": float(np.mean(baseline_samples)),
            "median": float(np.median(baseline_samples)),
            "std": float(np.std(baseline_samples)),
            "max": float(np.max(baseline_samples)),
            "iqr_threshold": float(
                np.percentile(baseline_samples, 75) +
                1.5 * (np.percentile(baseline_samples, 75) - np.percentile(baseline_samples, 25))
            ),
        },


        "samples": len(baseline_samples),

        "baseline_samples": baseline_samples,
        "observed_samples": observed_samples,

        "convergence": {
            "means": means[::10].tolist(),
            "variances": variances,
        },

        "anomalies": [
            {"signal": "trigger_counter", "z_score": 4.8},
            {"signal": "trojan_active", "z_score": 3.6},
            {"signal": "payload_mask", "z_score": 3.1},
        ],

        "thresholds": {
            "z_threshold": 3.0
        },

        "decision": {
            "trojan_detected": True,
            "z_score": 4.8,
            "confidence": "99.9%",
            "observed": round(np.mean(observed_samples), 3),
        }
    }

    return results


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
