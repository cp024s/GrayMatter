# `analysis/` — Statistical Analysis Layer

## Overview

The `analysis/` directory implements the **statistical analysis layer** of the project.
Its role is to transform **raw internal switching activity** obtained from simulation into **quantitative statistical evidence** that can be used for anomaly detection.

This layer sits **between simulation and detection**:

```
Simulation → Switching Activity → Analysis → Statistical Evidence → Detection
```

The analysis layer does **not** simulate RTL, trigger Trojans, or inspect design structure.
It operates purely on **measured behavior**.

---

## Why This Layer Exists

Hardware Trojans are often:

* functionally silent
* rarely triggered
* invisible to output-based verification

However, **internal switching activity always exists**, even when malicious logic is dormant.

The analysis layer exists to answer one question:

> **Is the observed internal behavior statistically consistent with a known-clean design?**

This is a statistical question, not a functional one.

---

## Core Concept

### Behavior as a Random Variable

Each simulation run produces a different internal activity profile due to:

* randomized stimulus
* state evolution
* timing interactions

We model switching activity as a random variable:

```
X = switching activity metric from one simulation run
```

Analysis does **not** reason about a single value of `X`.
It reasons about the **distribution of X**.

---

## Baseline Modeling

For a clean design, repeated sampling yields a baseline distribution:

```
X ~ D0(μ0, σ0²)
```

where:

* `μ0` is the mean switching activity
* `σ0²` is the natural variance

This baseline represents **normal internal behavior**, including noise and benign variation.

All later analysis compares observations **against this baseline**.

---

## High-Level Flow

```
Parsed switching activity
        ↓
Metric computation (X)
        ↓
Monte Carlo sampling
        ↓
Convergence validation
        ↓
Baseline model (μ, σ²)
        ↓
Hypothesis evaluation
        ↓
Detection evidence
```

Each stage is implemented in a **separate module** to enforce correctness and reproducibility.

---

## Directory Structure and Responsibilities

### `metrics/`

**Purpose:** Define *what is measured*.

* Converts parsed switching activity into a scalar metric `X`
* No statistics
* No thresholds
* No Trojan assumptions

Primary metric used:

```
X = total_toggles / observation_cycles
```

This abstraction enables statistical modeling while remaining tool-agnostic.

---

### `monte_carlo/`

**Purpose:** Define *how sampling is performed*.

* Executes repeated sampling of `X`
* Uses batch-based Monte Carlo sampling
* Prevents arbitrary sample counts

#### Convergence

Sampling stops only when **both mean and variance stabilize**:

```
|μk − μk−1| < εμ
|σk² − σk−1²| < εσ
```

for multiple consecutive batches.

This ensures the baseline is statistically reliable.

---

### `statistics/`

**Purpose:** Define *how normal behavior is represented and validated*.

#### Baseline Model

* Stores `(μ0, σ0², N)`
* Immutable once created
* Rejects non-converged baselines
* Serializable and reusable

#### False Positive Analysis

* Evaluates clean observations against clean baselines
* Estimates false alarm rate
* Provides empirical justification for thresholds

---

### `inference/`

**Purpose:** Quantify deviation from the baseline.

Given an observed value `Xobs`, deviation is measured using a Z-score:

```
Z = (Xobs − μ0) / sqrt(σ0²)
```

A two-sided confidence value is derived from `|Z|`.

This stage produces **statistical evidence**, not decisions.

---

### `detector.py`

**Purpose:** Combine evidence with policy.

Detection uses externally defined thresholds:

```
decision =
(|Z| > Z_threshold) AND (confidence > confidence_threshold)
```

* Thresholds are provided via configuration
* No hard-coded tuning
* Output includes full evidence, not just a boolean

---

## What This Layer Produces

The analysis layer produces:

* baseline statistical models
* convergence diagnostics
* deviation metrics
* confidence values
* false positive estimates

These outputs are **inputs** to higher-level experiments and evaluation.

---

## What This Layer Does NOT Do

Explicitly excluded responsibilities:

* RTL inspection
* Trojan trigger detection
* functional verification
* machine learning classification
* threshold tuning based on results

This separation prevents bias and preserves reproducibility.

---

