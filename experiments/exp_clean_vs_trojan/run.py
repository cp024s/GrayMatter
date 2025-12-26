#!/usr/bin/env python3

from pathlib import Path

from analysis.monte_carlo.mc_engine import MonteCarloEngine
from analysis.detector import TrojanDetector
from analysis.reporting.image_report import UnifiedImageReport
from analysis.reporting.text_report import TextReportGenerator
from sim.backends.iverilog import IcarusBackend


# --------------------------------------------------
# Experiment configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RTL_DIR = PROJECT_ROOT / "rtl"
RESULTS_DIR = PROJECT_ROOT / "results"

CLEAN_RTL = RTL_DIR / "clean"
TROJAN_RTL = RTL_DIR / "trojans"

NUM_SAMPLES = 1000


# --------------------------------------------------
# Main experiment
# --------------------------------------------------

def run_experiment():
    print("[INFO] Starting clean vs trojan experiment")

    backend = IcarusBackend()

    # -------------------------------
    # Clean baseline
    # -------------------------------
    print("[INFO] Running clean design Monte Carlo")

    mc_clean = MonteCarloEngine(
        backend=backend,
        rtl_dir=CLEAN_RTL,
        num_samples=NUM_SAMPLES,
    )

    clean_results = mc_clean.run()

    # -------------------------------
    # Trojan design
    # -------------------------------
    print("[INFO] Running trojan design Monte Carlo")

    mc_trojan = MonteCarloEngine(
        backend=backend,
        rtl_dir=TROJAN_RTL,
        num_samples=NUM_SAMPLES,
    )

    trojan_results = mc_trojan.run()

    # -------------------------------
    # Detection
    # -------------------------------
    detector = TrojanDetector()

    detection_results = detector.detect(
        baseline=clean_results,
        observed=trojan_results,
    )

    # -------------------------------
    # Reporting
    # -------------------------------
    plots_dir = RESULTS_DIR / "plots"
    summaries_dir = RESULTS_DIR / "summaries"

    image_report = UnifiedImageReport(plots_dir)
    text_report = TextReportGenerator(summaries_dir)

    image_report.generate(detection_results)
    text_report.generate(detection_results)

    print("[OK] Experiment complete")
    print("[OK] Reports generated")


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    run_experiment()
