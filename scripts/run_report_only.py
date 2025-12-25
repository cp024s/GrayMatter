import sys
from pathlib import Path
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

        "statistics": {
            "mean": np.mean(baseline_samples),
            "std": np.std(baseline_samples),
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

    report = UnifiedImageReport(Path("results/plots"))
    output_path = report.generate(results)

    print(f"[OK] Report generated at: {output_path}")
