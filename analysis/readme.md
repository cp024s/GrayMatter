# `analysis/` — Statistical Analysis and Inference Layer

This directory implements the **analysis layer** of the hardware Trojan detection framework.
Its responsibility is to convert **raw switching activity measurements** into **statistically meaningful conclusions**, without any dependence on RTL structure, simulator internals, or Trojan knowledge.

The analysis layer is deliberately separated from simulation and RTL to enforce **methodological correctness** and **reproducibility**.

---

## Scope and Role

The `analysis/` directory answers the following technical questions:

1. **What numerical observable represents circuit switching behavior?**
2. **How do we collect enough samples to model normal behavior reliably?**
3. **When can sampling be stopped without compromising statistical validity?**

This layer does **not**:

* simulate RTL
* parse VCD or SAIF files
* decide whether a Trojan exists
* tune detection thresholds

It provides **quantitative evidence**, not verdicts.

---

## Architectural Overview

At a high level, the analysis flow implemented here is:

```
Parsed switching activity
        ↓
 Metric computation (X)
        ↓
 Monte Carlo sampling
        ↓
 Convergence validation
        ↓
 Baseline statistics (μ, σ²)
```

Each module in this directory is responsible for **exactly one stage** of this flow.

---

## Module Breakdown

### 1. `metrics/toggle_metric.py`

**Purpose:**
Defines the primary **observable** used in the project.

**Responsibility:**
Convert parsed switching activity from a single simulation run into a **scalar metric** ( X ).

**Key characteristics:**

* Pure function (no side effects)
* Tool-agnostic (VCD / SAIF independent)
* No statistical logic
* No thresholds or decisions

**Conceptually:**
[
X = \frac{\text{total signal toggles}}{\text{observation cycles}}
]

This definition is intentionally simple and transparent, allowing later extensions (e.g., entropy-based or region-based metrics) without modifying downstream logic.

---

### 2. `monte_carlo/convergence.py`

**Purpose:**
Determine **when enough samples have been collected** to trust baseline estimates.

**Responsibility:**
Track convergence of:

* running mean ( \mu )
* running variance ( \sigma^2 )

using tolerance-based stability criteria.

**Key characteristics:**

* Incremental statistics (numerically stable)
* Explicit convergence conditions
* Requires consecutive stability to avoid false convergence
* Independent of how samples are generated

This module formalizes the question:

> *“Has additional sampling stopped providing new information?”*

---

### 3. `monte_carlo/mc_engine.py`

**Purpose:**
Orchestrate **Monte Carlo sampling** in a controlled, reproducible manner.

**Responsibility:**

* Load sampling configuration
* Invoke simulation backends
* Compute observables using metrics
* Update convergence tracking
* Stop sampling only when justified

**Key characteristics:**

* Backend-agnostic (Vivado / Icarus)
* Batch-based sampling
* Deterministic stopping logic
* Explicit handling of non-convergence

This module produces **baseline statistical models**, not detection results.

---

## Design Principles Enforced

The analysis layer is built around the following non-negotiable principles:

* **Separation of concerns**
  Measurement, sampling, and inference are never mixed.

* **Statistical transparency**
  Mean and variance are derived from data, never assumed.

* **Reproducibility**
  All randomness is controlled via configuration.

* **No hidden heuristics**
  Convergence and sampling behavior are explicit and inspectable.

---

## What This Layer Produces

The output of the analysis layer consists of:

* baseline mean and variance estimates
* convergence diagnostics
* sampling metadata (number of samples, backend used)

These outputs serve as **inputs** to higher-level inference and experimental evaluation.

---

## What This Layer Does *Not* Do

To avoid methodological errors, this layer explicitly avoids:

* making binary “Trojan / no Trojan” decisions
* applying detection thresholds
* tuning parameters based on outcomes
* incorporating design-specific knowledge

Those responsibilities belong to **separate layers**.

---
