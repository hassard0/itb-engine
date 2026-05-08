# v0.4 Learnings + v0.5 Direction

**Date:** 2026-05-08

## What v0.4 actually told me

1. **The completeness check produced unsolicited insight.** It flagged `g_6` as unbounded, meaning IR positivity bounds are *incomplete* without a UV cutoff. I had not been treating the constraint set as incomplete; the diagnostic forced the issue. This is the first time the engine surfaced a methodological gap I would not have caught by inspection.
2. **The binding-class plot is still mono-class.** All four constraints we have (`g_4 ≥ 0`, `g_6 ≥ 0`, `g_6 ≥ g_4²`, `g_R²² ≤ g_4·g_6`) are class A (amplitude bootstrap). Until we add class B (information-theoretic) or class C (universality), the diagnostic that distinguishes physical *origins* of constraints is dormant. Adding even one of each lights it up.
3. **No framework encoder besides Pure GR.** We can't yet ask the question that motivated the engine: "where does string theory sit on the allowed-region map?" That requires a `StringTreeEFT` (or similar) framework whose predicted Wilson coefficients we can plot.

## v0.5 commitments

- **F1: EFTValidityBox (class C).** Wilson coefficients of dimension-d operators must be bounded by Λ^d times an O(1) constant. Closes the completeness gap.
- **F2: BekensteinTight (class B).** Bekenstein-style entropy bound translated to a constraint on `g_R²² ≤ (1/2)·g_4·g_6` — tighter than the Caron-Huot mixed positivity. The first information-theoretic constraint in the engine.
- **F3: StringTreeEFT framework.** Predicted Wilson coefficients from tree-level α′ expansion. Enables "where does string theory sit?" plots.
- **F4: Phase components detector.** Count disconnected components of the allowed region. Each is a different "phase" of consistent UV completion.
- **F5: Server + frontend wiring** for the above, plus a framework-comparison overlay on the sweep plot.

## New ideas this round (queued for v0.6+)

- **#i Theory fingerprint.** Vectorize each candidate theory by `(n_binding, fragility, n_path-equivalent-theories, observables, …)` and cluster. UV completions falling in the same cluster are observably equivalent — important for prioritizing experiments.
- **#ii Constraint forward-propagation.** Given two constraints, derive new (tighter) ones via positive-combination closure. Detects redundancy *before* running a sweep.
- **#iii Sensitivity propagation.** Wilson coefficients carry EFT power-counting uncertainty; propagate to a feasibility *probability* per point, not a hard yes/no.
- **#iv Mode-specific positivity.** Spin-2 and spin-0 partial-wave positivity bounds couple sectors differently; adding spin decomposition extracts orthogonal information.
- **#v Catastrophe-theoretic phase boundaries.** Cusps and swallowtails in theory space correspond to second-order transitions in UV completion. Detect them via local curvature analysis on the boundary.
