# Detection Methodology

This document formally describes the detection methodology implemented in this repository. It specifies the measurement process, statistical modeling, and decision procedure independently of implementation details. The intent is to make the detection logic explicit, analyzable, and reproducible.

---

## 1. Methodological Overview

The detection method treats hardware Trojan identification as a **statistical inference problem** over indirect observables. Rather than attempting to activate Trojan payloads or infer trigger conditions, the methodology evaluates whether observed internal behavior is statistically consistent with that of a clean design under randomized stimulus.

The method consists of four conceptual stages:

1. Measurement of an internal observable
2. Empirical modeling of baseline behavior
3. Statistical convergence assessment
4. Confidence-based decision making

Each stage is described formally below.

---

## 2. Observable Definition

Let the digital design under analysis be denoted as ( D ).

### 2.1 Primary Observable

The primary observable is **post-synthesis internal switching activity**, measured over a finite simulation window. Switching activity is defined as the count or weighted aggregation of signal transitions within the synthesized netlist.

Formally, each simulation produces a scalar or vector-valued observation:

[
X = f(D, S, T)
]

where:

* ( S ) is the applied input stimulus,
* ( T ) is the observation window,
* ( f(\cdot) ) is the activity aggregation function.

The observable ( X ) is treated as a **random variable** due to its dependence on randomized stimulus.

---

## 3. Monte Carlo Sampling Procedure

### 3.1 Stimulus Generation

Input stimulus is generated via a Monte Carlo process. Each stimulus batch consists of a sequence of randomly generated input vectors applied to the design.

Let:

* ( {S_1, S_2, \dots, S_n} ) denote independent stimulus batches.

Each batch produces an independent sample ( X_i ) of the observable.

### 3.2 Batch-Based Sampling

Sampling proceeds incrementally in batches rather than as a single fixed-length simulation. This allows the estimation process to adaptively determine when sufficient data has been collected.

---

## 4. Baseline Distribution Modeling

### 4.1 Clean Baseline Estimation

For a clean reference design ( D_0 ), repeated Monte Carlo sampling yields a set of observations:

[
\mathcal{X}_0 = {X_1, X_2, \dots, X_N}
]

From this set, the baseline distribution ( P_0(X) ) is estimated using empirical statistics.

The baseline is characterized by:

* empirical mean ( \mu_0 ),
* empirical variance ( \sigma_0^2 ),
* optional higher-order statistics if required.

### 4.2 Interpretation

The baseline distribution represents **normal switching variability** under randomized stimulus. It explicitly models noise introduced by stimulus randomness and synthesis effects.

---

## 5. Statistical Convergence Assessment

Because baseline statistics are estimated from finite samples, convergence must be verified before decisions are made.

### 5.1 Convergence Criteria

Convergence is assessed using one or more of the following conditions:

* stabilization of the running mean:
  [
  |\mu_{k} - \mu_{k-1}| < \epsilon_\mu
  ]

* stabilization of variance:
  [
  |\sigma_{k}^2 - \sigma_{k-1}^2| < \epsilon_\sigma
  ]

* stability of confidence intervals across successive batches.

Sampling continues until convergence criteria are satisfied.

### 5.2 Rationale

Without convergence, any deviation assessment is unreliable. Convergence is therefore treated as a **precondition** for inference, not an optional refinement.

---

## 6. Detection as Hypothesis Testing

### 6.1 Problem Formulation

Given an observation ( X_{obs} ) from a design under test ( D_t ), the detection problem is formulated as:

* **Null hypothesis ( H_0 )**:
  ( X_{obs} \sim P_0(X) )

* **Alternative hypothesis ( H_1 )**:
  ( X_{obs} \not\sim P_0(X) )

The objective is not to classify Trojan presence directly, but to evaluate **statistical consistency** with the baseline distribution.

---

## 7. Decision Metric and Confidence Estimation

### 7.1 Deviation Measurement

Deviation from baseline behavior is quantified using normalized metrics such as:

[
Z = \frac{X_{obs} - \mu_0}{\sigma_0}
]

or equivalent confidence measures derived from the baseline distribution.

### 7.2 Confidence Interpretation

Decision outcomes are expressed in terms of confidence or significance level rather than binary labels. High deviation indicates statistical inconsistency, not definitive malicious behavior.

---

## 8. False Alarm Modeling

False alarms arise naturally due to baseline variance and finite sampling.

To quantify false alarm behavior:

* clean-versus-clean comparisons are performed,
* deviation statistics are computed for baseline samples,
* empirical false alarm rates are estimated.

This ensures that detection thresholds are grounded in observed noise characteristics.

---

## 9. Trojan Activation Regime Analysis

Trojan behavior is analyzed across activation regimes characterized by their impact on the observable:

* **Continuous activation** produces persistent deviation.
* **Conditional activation** produces intermittent deviation.
* **Dormant behavior** may remain within baseline variance.

The methodology does not assume universal detectability and explicitly documents failure regimes.

---

## 10. Output and Interpretation

The methodology produces:

* baseline distributions,
* convergence diagnostics,
* deviation statistics,
* confidence measures.

These outputs constitute **evidence**, not proof. Interpretation must respect the assumptions and convergence conditions under which the results were obtained.

---

## 11. Methodological Limitations

The following limitations are intrinsic to the method:

* reliance on indirect observables,
* dependence on stimulus coverage,
* inability to guarantee detection of low-activity Trojans,
* abstraction from physical process variation.

These limitations are explicitly acknowledged and not treated as implementation defects.

---

## 12. Summary

This methodology formalizes pre-silicon hardware Trojan detection as a statistically grounded inference problem. It prioritizes explicit assumptions, convergence validation, and confidence-aware decision making over deterministic claims or heuristic thresholds.