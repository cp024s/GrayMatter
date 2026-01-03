from pathlib import Path
import matplotlib.pyplot as plt

RESULTS = Path("results")

def main():
    variants = ["clean", "v0", "v1", "v2"]
    totals = {}

    for v in variants:
        summary = RESULTS / v / "summaries" / "hardware_trojan_report.txt"
        if not summary.exists():
            continue

        with summary.open() as f:
            for line in f:
                if "Total Signals Analyzed" in line:
                    totals[v] = int(line.split(":")[-1])
                    break

    if not totals:
        print("[WARN] No summaries found, skipping plots")
        return

    plt.figure(figsize=(6,4))
    plt.bar(totals.keys(), totals.values())
    plt.ylabel("Signals Analyzed")
    plt.title("Trojan Detection Coverage")
    plt.tight_layout()

    out = RESULTS / "plots"
    out.mkdir(exist_ok=True)
    plt.savefig(out / "coverage.png")
    print("[OK] Plot written to results/plots/coverage.png")

if __name__ == "__main__":
    main()
