from pathlib import Path
from datetime import datetime


class TextReportGenerator:
    """
    Generates a structured, human-readable text report
    for hardware Trojan detection results.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, results: dict) -> Path:
        timestamp = results.get(
            "timestamp",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        report_path = self.output_dir / "hardware_trojan_report.txt"

        with report_path.open("w") as f:
            self._write_header(f, timestamp)
            self._write_statistics(f, results)
            self._write_anomalies(f, results)
            self._write_conclusion(f, results)

        return report_path

    # --------------------------------------------------
    # Sections
    # --------------------------------------------------

    def _write_header(self, f, timestamp: str):
        f.write("=" * 80 + "\n")
        f.write("HARDWARE TROJAN DETECTION REPORT\n")
        f.write("Side-Channel Analysis via Switching Activity\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Report Generated: {timestamp}\n\n")

    def _write_statistics(self, f, results: dict):
        stats = results["statistics"]

        f.write("-" * 80 + "\n")
        f.write("STATISTICAL SUMMARY\n")
        f.write("-" * 80 + "\n")

        f.write(f"Total Signals Analyzed: {results['total_signals']}\n")
        f.write(f"Mean Deviation: {stats['mean']:.2f}%\n")
        f.write(f"Median Deviation: {stats['median']:.2f}%\n")
        f.write(f"Standard Deviation: {stats['std']:.2f}%\n")
        f.write(f"Maximum Deviation: {stats['max']:.2f}%\n")
        f.write(f"IQR-based Outlier Threshold: {stats['iqr_threshold']}\n\n")

    def _write_anomalies(self, f, results: dict):
        anomalies = results["anomalies"]

        f.write("-" * 80 + "\n")
        f.write("ANOMALY DETECTION RESULTS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Anomalies Detected: {len(anomalies)}\n\n")

        if not anomalies:
            f.write("No anomalous per-signal activity detected.\n\n")
            return

        f.write(
            f"{'Rank':<6}{'Signal Name':<40}"
            f"{'Deviation (%)':<15}{'Z-score'}\n"
        )
        f.write("-" * 80 + "\n")

        for a in anomalies:
            f.write(
                f"{a['rank']:<6}{a['signal']:<40}"
                f"{a['deviation']:<15.2f}{a['z_score']:.2f}\n"
            )

        f.write("\n")

    def _write_conclusion(self, f, results: dict):
        decision = results["decision"]

        f.write("-" * 80 + "\n")
        f.write("CONCLUSION\n")
        f.write("-" * 80 + "\n")

        if decision["trojan_detected"]:
            f.write("⚠ TROJAN DETECTED\n\n")

            # Case 1: Global detection
            if decision.get("primary_signal") is None:
                f.write(
                    "Detection Method: Global switching activity analysis\n"
                )
                f.write(
                    "Evidence: Total switching activity exceeds "
                    "clean baseline threshold.\n"
                )
                f.write(f"Threshold: {decision['threshold']}\n")

            # Case 2: Per-signal detection
            else:
                f.write(
                    "Detection Method: Per-signal statistical analysis\n"
                )
                f.write(
                    "Most suspicious signal: "
                    f"{decision['primary_signal']} "
                    f"({decision['primary_deviation']:.2f}% deviation)\n"
                )
                f.write(f"Threshold: {decision['threshold']}\n")

            f.write(f"Confidence: {decision['confidence']}\n")

        else:
            f.write("✓ NO TROJAN DETECTED\n")
            f.write(
                "All observed activity falls within expected baseline ranges.\n"
            )

        f.write("\n" + "=" * 80 + "\n")
