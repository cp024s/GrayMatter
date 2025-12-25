# Simulation Backends — Architecture and Interface

## 1. Purpose of the `sim/backends` Layer

The `sim/backends/` directory implements the **simulation execution layer** of the project.

Its sole responsibility is to:

> **Run a single hardware simulation using a specific tool and return internal switching activity in a standardized format.**

This layer acts as a **strict boundary** between:

* simulation tools (Icarus, Vivado, future tools), and
* the analysis layer (which consumes activity data).

The backend layer exists to ensure that **analysis remains tool-agnostic**.

---

## 2. Why a Backend Abstraction Is Necessary

Different simulators:

* use different invocation mechanisms
* produce different activity formats (VCD, SAIF)
* expose different runtime controls

Without a backend abstraction:

* analysis code becomes tool-dependent
* experiments become fragile
* results become irreproducible across tools

The backend layer isolates **tool-specific behavior** behind a **single contract**.

---

## 3. What the Backend Layer Does (and Does Not Do)

### 3.1 Responsibilities

Each backend is responsible for:

* invoking a simulator
* executing exactly one simulation run
* collecting internal switching activity
* returning activity data in a standard structure

### 3.2 Explicit Non-Responsibilities

Backends must **not**:

* compute statistical metrics
* normalize activity
* perform Monte Carlo sampling
* apply thresholds
* reason about Trojans
* interpret results

Backends produce **measurements**, not conclusions.

---

## 4. The Backend Contract

All backends implement the same interface, defined in:

```
sim/backends/base.py
```

### 4.1 Required Method

Every backend must implement:

```
run(sim_cfg) → activity_dict
```

### 4.2 Required Output Structure

The return value **must contain**:

```
{
  "total_toggles": int,
  "cycles": int
}
```

Where:

* `total_toggles` = total number of signal transitions observed
* `cycles` = number of clock cycles executed

Additional fields may be returned, but these two keys are **mandatory**.

---

## 5. Determinism and Sampling Semantics

Each call to `run()` represents:

> **One independent sample of internal hardware behavior.**

Assumptions:

* stimulus randomness is controlled externally
* backends are deterministic given the same seed and config
* independence is enforced at the experiment layer

The backend layer does **not** manage randomness directly.

---

## 6. High-Level Backend Flow

The abstract execution flow is identical across tools:

```
Simulation Configuration
        ↓
Backend Setup
        ↓
Simulator Invocation
        ↓
Activity Dump Generation
        ↓
Activity Parsing
        ↓
Standardized Activity Output
```

Only the **implementation details** differ between backends.

---

## 7. Simulation Configuration (`sim_cfg`)

The backend receives a configuration dictionary containing:

Typical fields include:

* `rtl_files` — list of RTL source paths
* `top` — top module name
* `clock` — clock signal name
* `sim_time` — simulation duration
* `activity` — activity format (vcd / saif)

The backend:

* validates required keys
* does not modify configuration
* does not inject defaults silently

Configuration policy lives **outside** the backend.

---

## 8. Why Activity Is Returned as Aggregates

Backends return **aggregated activity**, not raw waveforms.

Reasons:

* analysis operates on scalar observables
* waveforms are large and tool-specific
* aggregation improves reproducibility
* separation prevents accidental coupling

Raw VCD/SAIF files are considered **intermediate artifacts**, not analysis inputs.

---

## 9. Relationship to the Analysis Layer

The backend layer is a **producer**.

The analysis layer is a **consumer**.

```
Backend → {total_toggles, cycles} → Metric → Analysis
```

Neither layer:

* knows the internal logic of the other
* makes assumptions about the other’s behavior

This separation is intentional and enforced.

---

## 10. Why This Layer Is Implemented Before Experiments

Backend correctness must be established before:

* Monte Carlo sampling
* baseline construction
* false positive estimation
* detection experiments

Any ambiguity at the backend level contaminates all higher-level results.

---

## 12. Unified Execution Model

Although Icarus Verilog and Vivado are very different tools, the backend layer enforces a **unified execution model**.

From the perspective of the analysis layer, **every backend behaves identically**:

```
run(sim_cfg)
    ↓
single simulation execution
    ↓
activity extraction
    ↓
{ total_toggles, cycles }
```

All tool-specific complexity is hidden inside the backend implementation.

---

## 13. Icarus Verilog Backend (`iverilog.py`)

### 13.1 Why Icarus Is Used

Icarus Verilog is:

* lightweight
* open-source
* scriptable
* ideal for rapid RTL experimentation

It serves as the **reference backend** for correctness and reproducibility.

---

### 13.2 Icarus Execution Flow

```
sim_cfg
  ↓
temporary work directory
  ↓
iverilog (compile)
  ↓
vvp (simulate)
  ↓
VCD generation
  ↓
VCD parsing
  ↓
{ total_toggles, cycles }
```

Each invocation of `run()` produces **exactly one independent activity sample**.

---

### 13.3 Compilation Stage

The backend performs:

```
iverilog -g2012 -s <top> -o sim.out <rtl_files>
```

Key properties:

* SystemVerilog support enabled
* explicit top-module selection
* no optimization assumptions
* deterministic compilation

Compilation errors propagate immediately and abort the run.

---

### 13.4 Simulation Stage

Simulation is executed using:

```
vvp sim.out
```

Assumptions:

* the testbench controls stimulus
* the testbench enables VCD dumping
* simulation length is testbench-defined

The backend does **not** inject stimulus or timing.

---

### 13.5 VCD-Based Activity Extraction

The Icarus backend parses the generated VCD file to extract:

* signal value transitions (toggles)
* clock rising edges (cycles)

A **toggle** is defined as:

```
any change in signal value (0↔1, x↔0, etc.)
```

A **cycle** is defined as:

```
a rising edge on the configured clock signal
```

These definitions are:

* simple
* transparent
* consistent across tools

---

### 13.6 Why Cycle Normalization Matters

Raw toggle counts scale with simulation length.

By returning both:

* `total_toggles`
* `cycles`

the analysis layer can define normalized metrics such as:

```
X = total_toggles / cycles
```

This decouples:

* activity intensity
* simulation duration

---

## 14. Vivado Backend (`vivado.py`)

### 14.1 Why Vivado Is Included

Vivado represents:

* FPGA-grade tooling
* industry-relevant flows
* synthesis-aware simulation environments

Including Vivado ensures that results are **not tool-specific artifacts**.

---

### 14.2 Vivado Execution Flow

```
sim_cfg
  ↓
temporary work directory
  ↓
TCL script generation
  ↓
vivado -mode batch
  ↓
RTL simulation
  ↓
VCD or SAIF generation
  ↓
activity parsing
  ↓
{ total_toggles, cycles }
```

Vivado is always invoked in **batch mode** to guarantee reproducibility.

---

### 14.3 TCL-Based Control

Unlike Icarus, Vivado is controlled via **TCL scripts**.

The backend generates a script that:

1. creates a temporary project
2. adds RTL sources
3. sets the top module
4. launches simulation
5. enables activity dumping
6. runs for a fixed duration
7. exits cleanly

This avoids:

* GUI state
* interactive dependencies
* hidden configuration

---

### 14.4 Activity Formats: VCD vs SAIF

Vivado supports multiple activity formats.

#### VCD

* waveform-based
* cycle-aware
* easier to parse
* larger files

#### SAIF

* aggregate switching counts
* smaller files
* synthesis-friendly
* no explicit cycle notion

The backend supports **both**, but with different semantics.

---

### 14.5 VCD Handling in Vivado

When VCD is selected:

* the same parsing logic as Icarus is used
* toggles are counted from value changes
* cycles are counted from clock edges

This ensures **cross-tool consistency**.

---

### 14.6 SAIF Handling in Vivado

When SAIF is selected:

* total toggles are extracted from `(T ...)` entries
* cycle count is provided externally via configuration

This is an intentional limitation of SAIF, not a backend flaw.

---

## 15. Tool-Agnostic Guarantees

Regardless of backend, the following guarantees hold:

* one `run()` call = one activity sample
* output format is identical
* analysis code remains unchanged
* metrics are comparable across tools

This allows experiments such as:

```
Icarus baseline vs Vivado observation
Vivado baseline vs Icarus observation
```

without modifying analysis logic.

---

## 16. Error Handling Philosophy

Backend errors are treated as **fatal**:

* missing clock signal → error
* zero cycles → error
* missing activity file → error

Silent fallbacks are **not allowed**, because they corrupt statistics.

---

## 17. Why Backends Do Not Return Waveforms

Returning raw waveforms would:

* increase coupling
* increase storage cost
* reduce reproducibility
* violate separation of concerns

The backend layer returns **only what analysis needs**.

---

## 19. Modeling Assumptions

The backend layer operates under a set of **explicit assumptions**.
These are not hidden constraints — they define the validity domain of results.

### 19.1 Clock-Based Time Model

* A **single primary clock** is assumed
* Clock cycles are counted via **rising edges**
* All normalization is performed relative to this clock

This assumption is valid for:

* synchronous digital designs
* most SoCs, accelerators, and controllers

Multi-clock designs are **out of scope** for the current backend layer.

---

### 19.2 Toggle Definition

A **toggle** is defined as:

```
any change in signal value (0 ↔ 1, x ↔ 0, z ↔ 1, etc.)
```

Implications:

* unknown (`x`) transitions are counted
* high-impedance (`z`) transitions are counted
* initialization effects contribute to activity

This choice intentionally **biases toward sensitivity**, not silence.

---

### 19.3 One Run = One Sample

Each backend invocation represents:

> **one independent sample of internal behavior**

The backend:

* does not control randomness
* does not reseed generators
* does not enforce independence

Those responsibilities belong to:

* the testbench
* the experiment harness

---

## 20. Known Limitations

### 20.1 No Structural Awareness

Backends:

* do not inspect RTL structure
* do not differentiate between signal types
* do not localize activity

All signals contribute equally to toggle count.

This is a deliberate design choice to:

* avoid design-specific bias
* maintain tool independence

---

### 20.2 No Temporal Correlation Modeling

Backends aggregate toggles over time.

They do **not**:

* preserve ordering
* model burst behavior
* detect temporal patterns

Temporal analysis is an **analysis-layer extension**, not a backend feature.

---

### 20.3 SAIF Cycle Ambiguity

SAIF does not encode cycle counts.

As a result:

* cycles must be supplied externally
* normalization may be approximate
* comparisons with VCD-based runs require care

This is a limitation of SAIF, not the backend.

---

### 20.4 Initialization Effects

Early simulation phases often exhibit:

* reset toggles
* uninitialized signals
* transient bursts

Backends **do not discard** this activity.

If exclusion is desired, it must be handled at:

* the testbench level, or
* the metric definition stage

---

## 21. Correctness Boundaries

Backend correctness is defined narrowly and intentionally.

A backend is considered **correct** if:

* it executes exactly one simulation run
* it returns correct aggregate activity
* it respects the output contract
* it fails loudly on invalid conditions

A backend is **not** responsible for:

* detecting Trojans
* reducing noise
* improving detection rates

Those are higher-layer concerns.

---

## 22. Why Backends Avoid Heuristics

Backends do **not** apply:

* filtering
* thresholds
* signal weighting
* region selection

Reasons:

* heuristics introduce bias
* heuristics reduce reproducibility
* heuristics contaminate statistics

All interpretation must occur **after** measurement.

---

## 23. Extension Points

The backend layer is designed to be **extended safely**.

### 23.1 Adding a New Simulator Backend

To add a new backend (e.g., Verilator, Questa):

1. Subclass `SimulationBackend`
2. Implement `run(sim_cfg)`
3. Return `{ total_toggles, cycles }`
4. Add no analysis logic

If these rules are followed, the analysis layer will work unchanged.

---

### 23.2 Supporting New Activity Sources

Possible extensions:

* gate-level switching
* post-layout SAIF
* FPGA on-chip counters

These must:

* preserve the output contract
* document new assumptions
* not alter existing backends

---

### 23.3 Multi-Metric Backends (Future)

Backends may eventually return:

```
{
  "total_toggles": ...,
  "cycles": ...,
  "region_activity": ...,
  "entropy_terms": ...
}
```

As long as required keys remain intact, this is safe.

---

## 24. Why This Layer Is Deliberately Conservative

The backend layer prioritizes:

* correctness over cleverness
* transparency over performance
* reproducibility over optimization

This conservatism is intentional.

It ensures that:

* analysis conclusions are defensible
* cross-tool comparisons are valid
* results survive scrutiny

---
