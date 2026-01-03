
# Hardware Trojan Detection using Side-Channel Switching Activity

This project implements a **pre-silicon hardware Trojan detection framework** based on **per-signal switching activity analysis** extracted from RTL simulation waveforms.

The system compares **clean baseline behavior** against multiple **Trojan-infected RTL variants**, identifying anomalous internal activity using statistically grounded metrics.

---
![Language](https://img.shields.io/badge/Language-SystemVerilog%20%7C%20Python-blue) ![Simulation](https://img.shields.io/badge/Simulation-Icarus%20Verilog-orange) ![Backend](https://img.shields.io/badge/Backend-Vivado%20%7C%20Icarus-informational) ![Detection](https://img.shields.io/badge/Detection-Per--Signal%20Statistical-success) ![Automation](https://img.shields.io/badge/Automation-Makefile-green) ![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## Project Overview

### What this project does

* Designs a clean ALU and multiple Trojan-infected variants (v0, v1, v2)
* Simulates RTL designs under randomized stimuli
* Extracts signal-level toggle activity from VCD waveforms
* Builds a **multi-seed clean baseline**
* Detects Trojan presence using **per-signal statistical deviation**
* Fully automates simulation and analysis with a single command

### What this project intentionally does NOT do

* No post-silicon measurements
* No machine-learning black boxes
* No unrealistic assumptions about signal observability
* No functional corruption (Trojans are *output-silent*)

This is a **side-channel-based pre-silicon detection study**, not a functional verification project.

---

## Repository Structure (High-Level)

```
rtl/                # Clean and Trojan RTL designs
tb/                 # Unified testbench
experiments/        # Simulation orchestration
analysis/           # Toggle extraction, baseline, detector
scripts/            # Analysis entrypoints
results/            # Generated VCDs, reports, plots
Makefile            # One-command automation
```

---

## How to Run

### Prerequisites

* Python 3.8+
* Icarus Verilog (`iverilog`)
* GNU Make

Ensure `iverilog` is available:

```bash
iverilog -V
```

---

### Full Pipeline Execution

Run **everything** (simulation + analysis + reports):

```bash
make all
```

This single command performs:

1. **Clean simulations** (10 randomized seeds)
2. **Trojan simulations** (v0, v1, v2)
3. **Per-signal analysis** on all VCDs
4. **Text report generation**
5. (Optional) Plot hooks

No manual steps are required.

---


## 📊 Plots & Report Artifacts

All analysis outputs are generated automatically during execution and stored under the results/ directory.

The project distinguishes raw data, analysis summaries, and visual artifacts to maintain clarity and reproducibility.

```
results/
├── clean/
│   ├── seed_1/
│   │   └── alu_secure.vcd
│   ├── seed_2/
│   │   └── alu_secure.vcd
│   └── ...
│
├── v0/
│   ├── alu_secure.vcd
│   ├── summaries/
│   │   └── hardware_trojan_report.txt
│   └── plots/
│
├── v1/
│   ├── alu_secure.vcd
│   ├── summaries/
│   │   └── hardware_trojan_report.txt
│   └── plots/
│
├── v2/
│   ├── alu_secure.vcd
│   ├── summaries/
│   │   └── hardware_trojan_report.txt
│   └── plots/
│
└── plots/
    └── (aggregate figures)

```

## 📝 Text Reports

For each Trojan variant, a human-readable detection report is generated at:

```
results/<variant>/summaries/hardware_trojan_report.txt
```

These reports contain:
- Statistical summary
- Detected anomalous signals
- Classification (propagated vs Trojan-internal)
- Final detection decision and confidence

---


### Detection Behavior by Variant

| Variant | Behavior                           | Expected Outcome                  |
| ------- | ---------------------------------- | --------------------------------- |
| clean   | No Trojan                          | No anomalies                      |
| v0      | Weak Trojan (propagated effects)   | Low-confidence detection          |
| v1      | Single internal Trojan register    | Clear internal anomaly            |
| v2      | Multiple internal Trojan registers | Strong, high-confidence detection |

### Example (v2)

* Internal signals (`shadow_a`, `shadow_b`, `shadow_c`) show **100% deviation**
* Clean datapath remains functionally correct
* Trojan detected based purely on **side-channel behavior**

This demonstrates increasing detectability as Trojan payload complexity increases.

---

## Detection Method Summary

* **Metric:** Signal toggle count from RTL simulation
* **Baseline:** Multi-seed clean distribution (per signal)
* **Detector:** Per-signal IQR-based anomaly detection
* **Classification:**

  * *Propagated anomalies* → indirect effects
  * *Internal anomalies* → Trojan-owned state

No global heuristics or ML assumptions are used.

---

## Reproducibility

All experiments are:

* Deterministic (seeded)
* Fully scripted
* Backend-agnostic (Icarus / Vivado supported)

A reviewer can reproduce all results with:

```bash
make all
```

---

## 📌 Project Status

<img src="https://img.shields.io/badge/Status-Complete-brightgreen" />
<img src="https://img.shields.io/badge/Reproducible-Yes-success" />
<img src="https://img.shields.io/badge/Automation-Full%20Pipeline-green" />
<img src="https://img.shields.io/badge/Simulation-RTL%20(Icarus%20%7C%20Vivado)-orange" />
<img src="https://img.shields.io/badge/Detection-Per--Signal%20Statistical-blue" />
<img src="https://img.shields.io/badge/Scope-Pre--Silicon%20Security-informational" />