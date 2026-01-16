# <div align="center">Hardware Trojan Detection using Side-Channel Switching Activity</div>

<div align="center">

![Language](https://img.shields.io/badge/Language-SystemVerilog%20%7C%20Python-blue) ![OS](https://img.shields.io/badge/Tested%20On-Ubuntu%2022.04-E95420?logo=ubuntu)
![Simulation](https://img.shields.io/badge/Simulation-Icarus%20Verilog-orange) ![Backend](https://img.shields.io/badge/Backend-Icarus-informational) ![Detection](https://img.shields.io/badge/Detection-Per--Signal%20Statistical-success) ![Automation](https://img.shields.io/badge/Automation-Makefile-green) ![Reproducible](https://img.shields.io/badge/Reproducible-Yes-success) ![Stage](https://img.shields.io/badge/Stage-Pre--Silicon-blueviolet) ![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

</div>

---

## 📌 Overview

This project implements a **pre-silicon hardware Trojan detection framework** based on  **side-channel switching activity analysis** extracted from RTL simulation waveforms.

Instead of relying on functional mismatches or post-silicon measurements, the framework detects Trojans by identifying **statistical deviations in internal signal activity** between:

- a **multi-seed clean baseline**, and  
- multiple **Trojan-infected RTL variants**

The entire pipeline — simulation, activity extraction, statistical modeling, detection, and reporting — is **fully automated and reproducible**.

---

### 🔁 End-to-End Detection Flow
<p align="center"> <img src="/docs/assets/arch_diagram.png" alt="Architecture Diagram" width="800"> </p>

#### Flow Explanation
- The diagram above illustrates the end-to-end, pre-silicon detection pipeline implemented in this project.
- Each stage is strictly separated, producing explicit artifacts that feed the next stage, ensuring transparency, reproducibility, and auditability.

  ##### 1. RTL Design Layer
  - The process begins with a clean reference ALU and multiple Trojan-infected variants (v0, v1, v2).
  - All variants are functionally equivalent at the architectural level — Trojans are output-silent and do not alter observable outputs.

  ##### 2. Deterministic Testbench Execution
  - A unified testbench applies identical, seeded random stimuli to all designs. 
  - This guarantees that any observed difference arises solely from internal hardware behavior, not from stimulus bias.

  ##### 3. RTL Simulation
  - Designs are simulated using an RTL simulator (Icarus Verilog or Vivado).
  - Simulations run for a fixed execution window (10,000 cycles), ensuring temporal consistency across runs.

  ##### 4. Waveform Generation (VCD)
  - Full signal activity is captured using VCD waveforms.
  - No signal filtering or reduction is applied at this stage — the waveform acts as a lossless side-channel trace.

  ##### 5.Toggle Activity Extraction
  - VCD files are parsed to compute per-signal toggle counts, preserving hierarchical signal names.
  - This transforms raw simulation data into quantitative side-channel metrics.

  ##### 6. Clean Baseline Modeling
  - Multiple clean simulations (10 independent seeds) are aggregated to build a per-signal statistical baseline.
  - This step establishes expected behavior and controls false positives.

  ##### 7. Per-Signal Statistical Detection
  - Observed activity from Trojan variants is compared against the baseline using per-signal IQR-based anomaly detection.
  - Signals are evaluated independently — no global thresholds or averaging are used.

  ##### 8. Anomaly Classification & Reporting
    - Detected anomalies are classified as:
        - Propagated (indirect effects on clean logic), or
        - Trojan-internal (direct malicious state).

    - Results are summarized through:
      - human-readable text reports, and 
      - visual analysis plots for documentation and publication.

  <br>
      This structured flow mirrors real pre-silicon security assessment pipelines, enabling early detection of stealthy hardware Trojans without requiring post-silicon measurements or trigger knowledge. </p>
---

## 🎯 Design Goals

### What this project does

- Implements a clean ALU and multiple Trojan-infected variants (`v0`, `v1`, `v2`)
- Runs **multi-seed clean simulations** to build a robust baseline
- Extracts **per-signal toggle activity** from VCD waveforms
- Performs **per-signal statistical anomaly detection**
- Distinguishes between:
  - **propagated anomalies**
  - **Trojan-internal state**
- Automates everything with a **single `make all` command**

### What this project intentionally does NOT do

- ❌ No post-silicon measurements
- ❌ No power or EM modeling
- ❌ No machine-learning black boxes
- ❌ No functional corruption (Trojans are *output-silent*)

This is a **side-channel-based pre-silicon trust evaluation study**, not a functional
verification exercise.

---

## 🧠 Why Side-Channel Detection Works

Hardware Trojans are engineered to evade functional testing by:

- activating under rare conditions,
- preserving architectural outputs,
- hiding payload effects from standard testbenches.

However, **Trojan logic still introduces additional internal state**. That state inevitably causes:

- increased switching activity,
- persistent background toggling,
- temporal correlation with trigger logic.

This project exploits those effects **at RTL simulation time**, making it suitable for **early-stage design security assessment**.

---

## 🧪 Experimental Setup

### Simulation Parameters

| Parameter           | Value                 |
|---------------------|-----------------------|
| Simulation cycles   | 10,000 cycles per run |
| Clean baseline runs | 10 independent seeds  |
| Seeds used          | 1 → 10                |
| Trojan variants     | v0, v1, v2            |
| Simulator           | Icarus Verilog        |
| Waveform format     | VCD                   |

### Clean Baseline Stability

| Metric                 | Observed Range     |
|------------------------|--------------------|
| Total toggles (clean)  | ~118,200 – 118,460 |
| Variation across seeds | < 0.3%             |
| Baseline stability     | High               |

This confirms that **multi-seed clean behavior is statistically consistent**.

---

## 🔬 Trojan Variants

| Variant | Description                   | Expected Signature        |
|---------|-------------------------------|---------------------------|
| `v0` | Weak Trojan (propagated effects) | Minor deviations          |
| `v1` | Single Trojan-owned register     | Localized anomaly         |
| `v2` | Multiple Trojan-owned registers  | Strong internal anomalies |

All Trojans preserve functional correctness.

---

## 📊 Detection Metrics

| Metric        | Meaning                         |
|---------------|---------------------------------|
| Toggle Count  | Number of value transitions     |
| Deviation (%) | Relative change from clean mean |
| Z-Score       | Statistical distance            |
| IQR Threshold | Per-signal outlier bound        |

Signals are classified as:

- **Propagated** — indirect effects
- **Trojan-internal** — malicious state

---

## 🧾 Detection Results

| Variant | Total Toggles | Anomalies    | Trojan-Internal Signals             |
|---------|---------------|--------------|-------------------------------------|
| clean   | ~118k         | 0            | None                                |
| v0      | 231,891       | 1 propagated | None                                |
| v1      | 217,228       | 2            | `shadow_reg`                        |
| v2      | 225,307       | 4            | `shadow_a`, `shadow_b`, `shadow_c`  |

---

## 🗂 Repository Structure

```
rtl/                # RTL designs
tb/                 # Unified testbench
experiments/        # Simulation orchestration
analysis/           # Toggle extraction & detection
scripts/            # Analysis entrypoints
results/            # VCDs, reports, plots
docs/               # Theory & methodology
Makefile            # One-command automation
```

---

## 📈 Results & Plots

All outputs are generated under `results/`:

```
results/
├── clean/
│   ├── seed_1/ ... seed_10/
│   ├── summaries/
│   └── plots/
│       └── hardware_trojan_analysis_report.png
├── v0/
├── v1/
├── v2/
└── plots/
└── coverage.png
```

---

## ▶ How to Run

### Prerequisites

- Python 3.8+
- Icarus Verilog
- GNU Make

### Full Pipeline

```bash
make all
```

Runs simulations, builds baseline, performs detection, and generates reports.

> [!NOTE]
> All experiments were executed and validated on **Ubuntu 22.04** using **Icarus Verilog** and **Python 3.10**.


---

## 📚 Documentation

```
docs/
├── assumptions.md                        # Scope & threat model
├── methodology.md                        # Step-by-step process
└── statistical_detection_framework.md    # Theory & justification
```

---

## 🔁 Reproducibility

* Deterministic seeds
* Scripted pipeline
* Backend-agnostic
* Fully repeatable results

---

## 🧩 Educational Value

* Hardware Trojan design
* Pre-silicon security analysis
* Side-channel leakage at RTL
* Statistical anomaly detection
* Automated hardware-security workflows

---

<div align="center">

**✔ End-to-End Hardware Trojan Detection Pipeline**

*Pre-Silicon • Reproducible • Statistically Grounded*

</div>