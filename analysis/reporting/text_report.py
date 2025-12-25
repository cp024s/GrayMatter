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
        """
        Generate the text report.

        Parameters
        ----------
        results : dict
            Aggregated detection results.

        Returns
        -------
        Path
            Path to the generated report file.
        """

        timestamp = results.get(
            "timestamp",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        report_path = self.output_dir / "hardware_trojan_report.txt"

        with report_path.open("w") as f:
            self._write_header(f, timestamp)
            self._write_statistics(f, results)
            self._write_anomalies(f, results)
            self._write_ml_section(f, results)
            self._write_conclusion(f, results)

        return report_path

    # ------------------------------------------------------------------
    # Section writers
    # ------------------------------------------------------------------

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
        f.write(
            f"IQR-based Outlier Threshold: "
            f"{stats['iqr_threshold']:.2f}%\n\n"
        )

    def _write_anomalies(self, f, results: dict):
        anomalies = results["anomalies"]

        f.write("-" * 80 + "\n")
        f.write("ANOMALY DETECTION RESULTS (25% Threshold)\n")
        f.write("-" * 80 + "\n")
        f.write(f"Anomalies Detected: {len(anomalies)}\n\n")

        f.write(
            f"{'Rank':<6}{'Signal Name':<30}"
            f"{'Deviation':<15}{'Status'}\n"
        )
        f.write("-" * 80 + "\n")

        for a in anomalies:
            f.write(
                f"{a['rank']:<6}{a['signal']:<30}"
                f"{a['deviation']:<15.2f}CRITICAL\n"
            )

        f.write("\n")

    def _write_ml_section(self, f, results: dict):
        ml = results.get("ml_anomalies", [])

        f.write("-" * 80 + "\n")
        f.write("MACHINE LEARNING-BASED DETECTION (Z-Score > 2.5)\n")
        f.write("-" * 80 + "\n")
        f.write(f"ML Anomalies Detected: {len(ml)}\n\n")

        for m in ml:
            f.write(
                f"  • {m['signal']}: "
                f"{m['deviation']:.2f}% deviation\n"
            )

        f.write("\n")

    def _write_conclusion(self, f, results: dict):
        decision = results["decision"]

        f.write("-" * 80 + "\n")
        f.write("CONCLUSION\n")
        f.write("-" * 80 + "\n")

        if decision["trojan_detected"]:
            f.write("⚠ TROJAN DETECTED\n\n")
            f.write(
                "Evidence: Abnormal switching activity detected "
                f"above the {decision['threshold']} deviation threshold.\n\n"
            )
            f.write(
                "Most suspicious signal: "
                f"{decision['primary_signal']} "
                f"with {decision['primary_deviation']:.2f}% deviation\n"
            )
        else:
            f.write("✓ NO TROJAN DETECTED\n")

        f.write("\n" + "=" * 80 + "\n")
