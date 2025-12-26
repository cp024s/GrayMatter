"""
Detection orchestration logic.

This module combines:
- a converged baseline model
- an observed scalar metric
- a decision policy (thresholds)

to produce a structured detection result.

This module does NOT:
- perform simulation
- compute metrics
- estimate baselines
"""
"""
Statistical detector for hardware Trojan identification
using side-channel switching activity.
"""

import numpy as np


def run_detector(baseline: dict, observed: dict) -> dict:
    """
    Compare observed toggle activity against a clean baseline.

    Args:
        baseline (dict):
            Output of build_baseline_distribution()
        observed (dict):
            { "signal_name": toggle_count }

    Returns:
        dict: results compatible with reporting layer
    """

    baseline_mean = baseline["mean"]
    baseline_std = baseline["std"]
    iqr_threshold = baseline["iqr_threshold"]

    anomalies = []

    # --------------------------------------------------
    # Analyze observed signals
    # --------------------------------------------------
    for sig, val in observed.items():
        deviation_pct = (
            ((val - baseline_mean) / baseline_mean) * 100.0
            if baseline_mean > 0 else 0.0
        )

        z_score = (
            (val - baseline_mean) / baseline_std
            if baseline_std > 0 else 0.0
        )

        # IQR-based anomaly decision
        if val > iqr_threshold:
            anomalies.append({
                "signal": sig,
                "deviation": round(deviation_pct, 2),
                "z_score": round(z_score, 2),
            })

    # --------------------------------------------------
    # Rank anomalies
    # --------------------------------------------------
    anomalies.sort(key=lambda x: abs(x["deviation"]), reverse=True)
    for idx, a in enumerate(anomalies, start=1):
        a["rank"] = idx

    # --------------------------------------------------
    # Final decision
    # --------------------------------------------------
    trojan_detected = len(anomalies) > 0

    results = {
        "total_signals": len(observed),

        "statistics": {
            "mean": round(baseline_mean, 3),
            "median": round(float(np.median(baseline["samples"])), 3),
            "std": round(baseline_std, 3),
            "max": round(float(np.max(baseline["samples"])), 3),
            "iqr_threshold": round(iqr_threshold, 3),
        },

        "baseline_samples": baseline["samples"],
        "observed_samples": list(observed.values()),

        "anomalies": anomalies,

        "thresholds": {
            "z_threshold": 2.5,
        },

        "decision": {
            "trojan_detected": trojan_detected,
            "primary_signal": anomalies[0]["signal"] if anomalies else None,
            "primary_deviation": anomalies[0]["deviation"] if anomalies else None,
            "threshold": "IQR-based",
            "z_score": anomalies[0]["z_score"] if anomalies else None,
            "confidence": "high" if trojan_detected else "low",
        },
    }

    return results
