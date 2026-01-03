# Hardware Trojan Detection via Statistical Analysis of Switching Activity
---

## 1. Problem Statement

Hardware Trojans are malicious logic insertions designed to evade functional verification by remaining dormant or conditionally active. In pre-silicon settings, direct observation of Trojan payloads or trigger conditions is often infeasible. As a result, detection must rely on **indirect observables** under uncertainty.

This work addresses the following problem:

> Given only simulated internal switching activity under random stimulus, determine whether the observed behavior is statistically consistent with a clean implementation of the design.

The emphasis is not on functional deviation, but on **behavioral consistency** under stochastic observation.

---

## 2. Detection Assumptions

The methodology operates under a minimal and explicit assumption set.

| Assumption                                | Implication                                |
| ----------------------------------------- | ------------------------------------------ |
| Internal switching activity is observable | Trojan effects may be inferred indirectly  |
| Simulation length is finite               | Detection decisions are probabilistic      |
| Input stimulus is randomized              | Measurements are stochastic                |
| Trojan triggers are unknown               | Functional activation is not required      |
| Clean behavior is non-deterministic       | Baseline must be modeled as a distribution |

No assumptions are made about payload behavior, trigger structure, or golden functional signatures.

---

## 3. Observable and Measurement Model

The primary observable is **post-synthesis internal switching activity**, treated as a random variable induced by input stimulus and circuit structure.

Rather than analyzing individual signals, activity is aggregated into metrics that capture global or regional behavior while reducing sensitivity to local noise.

| Quantity     | Description                           |
| ------------ | ------------------------------------- |
| ( X )        | Aggregate switching activity metric   |
| ( \mu_0 )    | Baseline mean activity (clean design) |
| ( \sigma_0 ) | Baseline activity variance            |
| ( X_{obs} )  | Observed activity under test          |

Switching activity is chosen because it:

* persists even when outputs are functionally correct,
* reflects internal logic evaluation,
* is accessible in pre-silicon simulation.

---

## 4. Detection as Statistical Inference

Detection is formulated as a **statistical inference problem**, not a deterministic comparison.

Let ( P_0(X) ) denote the baseline distribution of switching activity for a clean design. Given an observation ( X_{obs} ), the task is to assess whether the observation is consistent with ( P_0(X) ) within acceptable confidence bounds.

Decisions are based on:

* deviation magnitude relative to baseline variance,
* statistical confidence rather than absolute thresholds,
* convergence of the estimated baseline distribution.

The output of the detector is therefore **evidence-based**, not binary.

---

## 5. Monte Carlo Sampling and Convergence

Because switching activity depends on input stimulus, baseline behavior cannot be derived analytically. Monte Carlo sampling is used to estimate the distribution empirically.

Sampling proceeds in batches, with incremental updates to mean and variance. Simulation continues until **statistical convergence** is observed.

| Convergence Indicator         | Purpose                                |
| ----------------------------- | -------------------------------------- |
| Mean stabilization            | Prevents under-sampling                |
| Variance stabilization        | Enables reliable confidence estimation |
| Confidence interval stability | Supports termination decision          |

This avoids arbitrary choices such as fixed vector counts and allows the data itself to determine sampling sufficiency.

---

## 6. Baseline Modeling and False Alarms

Clean designs exhibit non-trivial switching variability due to stimulus randomness and synthesis effects. Treating clean behavior as a single reference value leads to fragile detectors and uncontrolled false alarms.

This framework explicitly models **baseline variance** using repeated clean simulations.

| Aspect         | Naive Detection    | This Framework     |
| -------------- | ------------------ | ------------------ |
| Clean behavior | Single measurement | Distribution       |
| Thresholding   | Fixed heuristic    | Variance-aware     |
| False alarms   | Implicitly ignored | Explicitly modeled |
| Decision       | Binary             | Confidence-based   |

Anomalies are evaluated relative to the modeled noise floor rather than assumed separability.

---

## 7. Trojan Activation Regimes

Trojan logic is categorized by activation behavior to expose detectability limits.

| Activation Regime | Activity Impact | Detectability           |
| ----------------- | --------------- | ----------------------- |
| Continuous        | Persistent      | Reliable                |
| Conditional       | Intermittent    | Probabilistic           |
| Dormant           | Minimal         | Often indistinguishable |

These regimes are not assumed to be equally detectable; their inclusion is intended to characterize failure modes.

---

## 8. Experimental Protocol

All experiments follow a controlled and repeatable protocol:

1. Select a clean reference design.
2. Generate Monte Carlo stimulus in batches.
3. Estimate baseline activity distribution and convergence.
4. Apply identical stimulus methodology to Trojan variants.
5. Compare observed behavior against baseline statistics.
6. Report deviation metrics and confidence measures.

All parameters governing simulation, sampling, and inference are externalized and script-driven.

---

## 9. Output Artifacts and Visuals

The framework produces quantitative artifacts rather than single-point results. All visuals are generated programmatically using Python and matplotlib.

| Artifact                       | Purpose                     |
| ------------------------------ | --------------------------- |
| Convergence curves             | Verify sampling sufficiency |
| Baseline distributions         | Characterize noise floor    |
| Clean vs anomalous plots       | Assess separability         |
| Confidence vs threshold curves | Examine trade-offs          |
| Activation-regime comparisons  | Expose failure modes        |

No conclusions are drawn from isolated observations.

---

## 10. Observed Behaviors and Failure Modes

Across experiments, the following behaviors are consistently observed:

* Baseline activity exhibits measurable variance.
* Convergence rates differ significantly across designs.
* Continuous Trojans are readily distinguishable.
* Conditional Trojans require extensive sampling.
* Dormant Trojans may remain statistically indistinguishable from baseline noise.

These outcomes are intrinsic to the observable and define the limits of activity-based detection.

---

## 11. Reproducibility and Execution

The framework is executed through scripted, non-interactive flows.

* Simulation, analysis, and plotting are automated.
* Configuration files control all parameters.
* Results are reproducible given identical toolchains and configurations.

Reproducibility is treated as a first-class requirement.

---

## 12. Extensions and Open Directions

The formulation naturally extends to:

* entropy-based observables for rare-event sensitivity,
* spatially localized activity metrics,
* process-variation-aware baseline modeling,
* post-silicon observables such as ring-oscillator networks,
* hybrid inference with adaptive threshold selection.

These directions follow directly from the detection formulation.

---

## 13. Conceptual Lineage

This work draws conceptual grounding from prior efforts in:

* side-channel hardware Trojan detection,
* Monte Carlo activity and power estimation,
* statistical hypothesis testing,
* entropy-based anomaly detection,
* FPGA post-synthesis activity analysis.

The contribution lies in structuring these ideas into a **coherent, inference-driven methodology**, rather than proposing a new side channel.

---

### Closing Remark

This repository is intended to function as a **technical reference implementation** for statistically grounded pre-silicon Trojan detection. Emphasis is placed on clarity of assumptions, rigor of formulation, and transparency of limitations over empirical spectacle.
