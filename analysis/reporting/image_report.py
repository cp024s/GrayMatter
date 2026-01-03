from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd

from analysis.monte_carlo import convergence
import numpy as np
import seaborn as sns


class UnifiedImageReport:
    """
    Generates a single, unified image report summarizing
    hardware Trojan detection results.

    Output: one PNG image suitable for README, slides, or papers.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, results: dict) -> Path:
        self._results = results   # <-- ADD THIS LINE
        """
        Generate the unified analysis report image.

        Parameters
        ----------
        results : dict
            Aggregated detection and analysis results.

        Returns
        -------
        Path
            Path to generated PNG image.
        """

        fig = plt.figure(figsize=(18, 12), dpi=150)
        fig.patch.set_facecolor("white")

        # Grid layout:
        # 0: Header
        # 1: Summary table
        # 2-3: Plots (added in Part 2)
        # 4: Conclusion panel (added in Part 3)
        gs = GridSpec(
            nrows=5,
            ncols=2,
            height_ratios=[0.9, 1.6, 2.4, 2.4, 1.6],
            hspace=0.55,
            wspace=0.30,
        )

        self._draw_header(fig, gs[0, :], results)
        self._draw_summary_table(fig, gs[1, :], results)

        # Placeholders for future parts
        self._reserve_axes(fig, gs)

        output_path = self.output_dir / "hardware_trojan_analysis_report.png"
        plt.subplots_adjust(top=0.96, bottom=0.05)
        plt.savefig(output_path, bbox_inches="tight")
        plt.close(fig)

        return output_path

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _draw_header(self, fig, grid_cell, results: dict):
        ax = fig.add_subplot(grid_cell)
        ax.axis("off")

        timestamp = results.get(
            "timestamp",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        title = "HARDWARE TROJAN DETECTION REPORT"
        subtitle = "Side-Channel Switching Activity Analysis"

        ax.text(
            0.5, 0.70, title,
            fontsize=20, fontweight="bold",
            ha="center", va="center"
        )

        ax.text(
            0.5, 0.35, subtitle,
            fontsize=13,
            ha="center", va="center"
        )

        ax.text(
            0.01, 0.05,
            f"Generated: {timestamp}",
            fontsize=9,
            ha="left", va="bottom"
        )

    # ------------------------------------------------------------------
    # Statistical Summary Table
    # ------------------------------------------------------------------

    def _draw_summary_table(self, fig, grid_cell, results: dict):
        ax = fig.add_subplot(grid_cell)
        ax.axis("off")

        stats = results["statistics"]
        decision = results["decision"]

        table_data = [
            ["Baseline Mean (μ₀)", f"{stats['mean']:.3f}"],
            ["Baseline Std Dev (σ₀)", f"{stats['std']:.3f}"],
            ["Samples (N)", f"{results.get('samples', '—')}"],
            ["Observed Activity (X)", f"{decision.get('observed', '—')}"],
            ["Z-score", f"{decision.get('z_score', '—')}"],
            ["Confidence", f"{decision.get('confidence', '—')}"],
        ]

        df = pd.DataFrame(table_data, columns=["Metric", "Value"])

        table = ax.table(
            cellText=df.values,
            colLabels=df.columns,
            loc="center",
            cellLoc="center",
        )

        table.scale(1, 1.9)

        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor("black")
            if row == 0:
                cell.set_text_props(fontweight="bold")
                cell.set_facecolor("#E6E6E6")
            else:
                cell.set_facecolor("white")

        ax.set_anchor("N")
        ax.set_title(
            "Statistical Summary",
            fontsize=14,
            fontweight="bold",
            pad=10
        )

    # ------------------------------------------------------------------
    # Axes reservation for later parts
    # ------------------------------------------------------------------

    def _reserve_axes(self, fig, gs):
        """
        Reserve axes for plots and conclusion panels.
        These will be populated in Part 2 and Part 3.
        """
        for idx in [(2, 0), (2, 1), (3, 0), (3, 1), (4, slice(None))]:
            ax = fig.add_subplot(gs[idx])
            ax.axis("off")


    # ------------------------------------------------------------------
    # Evidence plots
    # ------------------------------------------------------------------

    def _draw_baseline_distribution(self, fig, grid_cell, results: dict):
        ax = fig.add_subplot(grid_cell)

        baseline = np.array(results["baseline_samples"])
        mu = baseline.mean()
        sigma = baseline.std()

        sns.histplot(
            baseline,
            bins=30,
            kde=True,
            stat="density",
            color="steelblue",
            ax=ax,
        )

        ax.axvline(mu, color="black", linestyle="--", label="μ₀")
        ax.axvline(mu + sigma, color="red", linestyle=":", label="±1σ")
        ax.axvline(mu - sigma, color="red", linestyle=":")

        ax.set_title("Baseline Activity Distribution")
        ax.set_xlabel("Normalized Switching Activity")
        ax.set_ylabel("Density")
        ax.legend()

    def _draw_clean_vs_trojan(self, fig, grid_cell, results: dict):
        ax = fig.add_subplot(grid_cell)

        baseline = np.array(results["baseline_samples"])
        observed = np.array(results["observed_samples"])

        sns.kdeplot(baseline, label="Clean Baseline", ax=ax)
        sns.kdeplot(observed, label="Observed Design", ax=ax)

        ax.set_title("Clean vs Observed Activity Overlay")
        ax.set_xlabel("Normalized Switching Activity")
        ax.set_ylabel("Density")
        ax.legend()

    def _draw_convergence(self, fig, subplotspec, results):
    # Always materialize an Axes from the SubplotSpec
        ax = fig.add_subplot(subplotspec)

        convergence = results.get("convergence", None)

        if convergence is None:
            ax.text(
                0.5, 0.5,
                "Convergence data not available",
                ha="center",
                va="center",
                fontsize=10
            )
            ax.set_axis_off()
            return

        means = convergence["means"]
        variances = convergence["variances"]

        ax.plot(means, label="Mean", linewidth=1.8)
        ax.plot(variances, label="Variance", linewidth=1.8)
        means = convergence["means"]
        variances = convergence["variances"]

        ax.plot(means, label="Mean", linewidth=1.8)
        ax.plot(variances, label="Variance", linewidth=1.8)

        ax.set_title("Baseline Convergence")
        ax.set_xlabel("Samples")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _draw_anomaly_bars(self, fig, grid_cell, results: dict):
        ax = fig.add_subplot(grid_cell)

        anomalies = results["anomalies"]
        z_thr = results["thresholds"]["z_threshold"]

        signals = [a["signal"] for a in anomalies]
        z_scores = [a["z_score"] for a in anomalies]

        x = range(len(signals))
        ax.bar(x, z_scores, color="firebrick")
        ax.axhline(z_thr, color="black", linestyle="--", label="Z Threshold")

        ax.set_title("Z-score per Signal")
        ax.set_ylabel("Z-score")
        ax.set_xticks(x)
        ax.set_xticklabels(signals, rotation=25, ha="right")

        ax.margins(x=0.15)
        ax.legend()
    # ------------------------------------------------------------------
    # Override reservation to populate plots
    # ------------------------------------------------------------------

    def _reserve_axes(self, fig, gs):
        self._draw_baseline_distribution(fig, gs[2, 0], self._results)
        self._draw_clean_vs_trojan(fig, gs[2, 1], self._results)
        self._draw_convergence(fig, gs[3, 0], self._results)
        self._draw_anomaly_bars(fig, gs[3, 1], self._results)

    # ------------------------------------------------------------------
    # Conclusion panel
    # ------------------------------------------------------------------

    def _draw_conclusion(self, fig, grid_cell, results: dict):
        ax = fig.add_subplot(grid_cell)
        ax.axis("off")

        decision = results["decision"]
        detected = decision["trojan_detected"]

        if detected:
            banner_text = "⚠  TROJAN DETECTED"
            banner_color = "#B22222"   # firebrick
            summary = (
                "Statistical evidence indicates abnormal switching activity.\n"
                "Observed behavior deviates significantly from the clean baseline."
            )
        else:
            banner_text = "✓  NO TROJAN DETECTED"
            banner_color = "#228B22"   # forest green
            summary = (
                "Observed switching activity is statistically consistent\n"
                "with the clean baseline distribution."
            )

        # Banner box
        ax.text(
            0.5, 0.75,
            banner_text,
            fontsize=20,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.6",
                facecolor=banner_color,
                edgecolor="black",
                alpha=0.9,
            ),
            color="white",
        )

        # Evidence text
        ax.text(
            0.5, 0.40,
            summary,
            fontsize=11,
            ha="center",
            va="center",
        )

        # Key evidence details
        details = (
            f"Z-score: {decision.get('z_score', '—')}    |    "
            f"Confidence: {decision.get('confidence', '—')}\n"
            f"Threshold: {results['thresholds']['z_threshold']}"
        )

        ax.text(
            0.5, 0.15,
            details,
            fontsize=11,
            ha="center",
            va="center",
        )

    # ------------------------------------------------------------------
    # FINAL override: populate all panels
    # ------------------------------------------------------------------

    def _reserve_axes(self, fig, gs):
        self._draw_baseline_distribution(fig, gs[2, 0], self._results)
        self._draw_clean_vs_trojan(fig, gs[2, 1], self._results)
        self._draw_convergence(fig, gs[3, 0], self._results)
        self._draw_anomaly_bars(fig, gs[3, 1], self._results)
        self._draw_conclusion(fig, gs[4, :], self._results)
