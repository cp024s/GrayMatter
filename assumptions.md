# Assumptions and Operational Conditions

This document enumerates the assumptions under which the detection methodology implemented in this repository is valid. These assumptions are made explicit to clarify the scope of applicability, avoid over-interpretation of results, and expose inherent limitations of pre-silicon, activity-based detection.

---

## 1. Observability Assumptions

1. **Internal Switching Activity is Observable**
   The methodology assumes access to internal switching activity through simulation artifacts (e.g., VCD or SAIF). No assumptions are made regarding visibility of silicon-level power, electromagnetic, or thermal signals.

2. **Post-Synthesis Netlist Availability**
   Detection is performed on synthesized logic. It is assumed that synthesis preserves sufficient structural and activity characteristics for meaningful analysis, despite optimization and technology mapping.

3. **Aggregate Observables are Sufficient**
   Switching activity is analyzed in aggregated form (global or region-level metrics). The methodology does not assume reliable identification of individual malicious signals.

---

## 2. Sampling and Stimulus Assumptions

1. **Randomized Input Stimulus**
   Input vectors are assumed to be generated from a randomized process without bias toward Trojan trigger conditions.

2. **Finite Observation Window**
   Only a finite number of simulation cycles can be observed. As a result, all measurements are treated as stochastic samples rather than exact representations of system behavior.

3. **Monte Carlo Independence Approximation**
   Successive stimulus batches are treated as approximately independent samples for the purpose of statistical estimation, acknowledging that perfect independence is not guaranteed.

---

## 3. Baseline Behavior Assumptions

1. **Clean Design Variability**
   Clean designs are assumed to exhibit non-zero switching variance due to stimulus randomness and synthesis effects. Baseline behavior is therefore modeled as a distribution rather than a single reference value.

2. **Stationarity During Observation**
   The baseline distribution is assumed to be stationary over the duration of observation. Long-term temporal drift effects are not modeled.

3. **No Adversarial Baseline Manipulation**
   It is assumed that the clean reference design is not intentionally crafted to mimic Trojan-induced activity patterns.

---

## 4. Trojan Behavior Assumptions

1. **Activity Influence**
   The methodology assumes that Trojan logic, if present, influences internal switching activity at some level, even if functional outputs remain correct.

2. **Unknown Trigger Conditions**
   Trojan trigger conditions are assumed unknown and may never be activated during observation.

3. **No Guaranteed Detectability**
   Trojans with negligible activity footprint or extremely rare activation may be statistically indistinguishable from baseline behavior within finite sampling limits.

---

## 5. Decision and Inference Assumptions

1. **Probabilistic Decision Model**
   Detection decisions are probabilistic and expressed in terms of confidence and deviation from baseline statistics, not absolute correctness.

2. **Confidence Does Not Imply Certainty**
   High confidence indicates statistical inconsistency with baseline behavior, not proof of malicious intent.

3. **False Alarms are Unavoidable**
   Non-zero false alarm probability is assumed and explicitly modeled. Zero false positives are neither expected nor claimed.

---

## 6. Toolchain and Environment Assumptions

1. **Tool Determinism**
   Simulation and synthesis tools are assumed to be deterministic under identical configurations, seeds, and environments.

2. **Technology Abstraction**
   The methodology does not attempt to model detailed process variation, temperature effects, or voltage noise beyond what is implicitly captured by synthesis.

---

## 7. Non-Claims

The following are explicitly **not** claimed by this methodology:

* Guaranteed detection of all hardware Trojans
* Applicability to post-silicon measurement domains
* Identification of Trojan trigger logic or payload structure
* Security certification or production-level assurance

---

## 8. Interpretation Guidance

Results produced by this framework should be interpreted as **evidence of statistical inconsistency**, not definitive proof of malicious behavior. Conclusions are valid only within the assumptions stated above.
