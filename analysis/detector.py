"""
Statistical detector for hardware Trojan identification
using per-signal side-channel switching activity.

PATH A:
- Trojan payload attribution (shadow_* only)
- Structural signal filtering
- Zero-baseline handling for Trojan-only signals
"""

import numpy as np


def run_detector(baseline: dict, observed: dict) -> dict:
    anomalies = []
    deviations = []

    baseline_samples = []
    observed_samples = []

    # --------------------------------------------------
    # Per-signal analysis
    # --------------------------------------------------
    for signal, obs_val in observed.items():
        observed_samples.append(obs_val)

        # --------------------------------------------------
        # Ignore testbench-only artifacts
        # --------------------------------------------------
        if signal.startswith("tb_alu_secure.seed"):
            continue
        if signal.startswith("tb_alu_secure.result_trojan"):
            continue

        # --------------------------------------------------
        # Ignore structural Trojan internals
        # (FSM, clock, datapath, noise, etc.)
        # --------------------------------------------------
        if "u_trojan" in signal and "shadow_" not in signal:
            continue

        # --------------------------------------------------
        # Baseline handling
        # --------------------------------------------------
        if signal not in baseline:
            # Trojan payload signal: clean baseline = zero
            mean = 0.0
            std = 0.0
            threshold = 0.0
            baseline_samples.append(0.0)
        else:
            b = baseline[signal]
            mean = b.get("mean", 0.0)
            std = b.get("std", 0.0)
            threshold = b.get("iqr_threshold", float("inf"))
            baseline_samples.extend(b.get("samples", []))

        # --------------------------------------------------
        # Deviation calculation
        # --------------------------------------------------
        if mean > 0:
            deviation_pct = ((obs_val - mean) / mean) * 100.0
        else:
            deviation_pct = 100.0 if obs_val > 0 else 0.0

        deviations.append(abs(deviation_pct))

        z_score = ((obs_val - mean) / std) if std > 0 else 0.0

        # --------------------------------------------------
        # Trojan payload classification
        # --------------------------------------------------
        is_trojan_internal = "shadow_" in signal

        # --------------------------------------------------
        # Anomaly decision
        # --------------------------------------------------
        if obs_val > threshold:
            anomalies.append({
                "signal": signal,
                "observed": int(obs_val),
                "mean": round(mean, 3),
                "deviation": round(deviation_pct, 2),
                "z_score": round(z_score, 2),
                "class": (
                    "trojan_internal"
                    if is_trojan_internal
                    else "propagated"
                ),
            })

    # --------------------------------------------------
    # DEBUG: raw anomaly structure (PRE-RANK)
    # --------------------------------------------------
    if anomalies:
        print("\n[DEBUG] Raw anomaly candidates (first 10):")
        for a in anomalies[:10]:
            print(
                f"  {a['signal']:<50} "
                f"{a['class']:<18} "
                f"dev={a['deviation']:>7}% "
                f"z={a['z_score']:>5}"
            )
        print()

    # --------------------------------------------------
    # Rank anomalies
    # --------------------------------------------------
    anomalies.sort(key=lambda x: abs(x["deviation"]), reverse=True)
    for idx, a in enumerate(anomalies, start=1):
        a["rank"] = idx

    # --------------------------------------------------
    # Aggregate statistics
    # --------------------------------------------------
    if deviations:
        stats_mean = float(np.mean(deviations))
        stats_median = float(np.median(deviations))
        stats_std = float(np.std(deviations))
        stats_max = float(np.max(deviations))
    else:
        stats_mean = stats_median = stats_std = stats_max = 0.0

    # --------------------------------------------------
    # Results (report-compatible)
    # --------------------------------------------------
    results = {
        "total_signals": len(observed),

        "statistics": {
            "mean": round(stats_mean, 3),
            "median": round(stats_median, 3),
            "std": round(stats_std, 3),
            "max": round(stats_max, 3),
            "iqr_threshold": "per-signal",
        },

        "baseline_samples": baseline_samples,
        "observed_samples": observed_samples,

        "anomalies": anomalies,

        "thresholds": {
            "z_threshold": "per-signal",
        },

        "decision": {
            "trojan_detected": len(anomalies) > 0,
            "primary_signal": anomalies[0]["signal"] if anomalies else None,
            "primary_deviation": anomalies[0]["deviation"] if anomalies else None,
            "threshold": "per-signal IQR + zero-baseline",
            "z_score": anomalies[0]["z_score"] if anomalies else None,
            "confidence": "high" if anomalies else "low",
        },
    }

    return results
