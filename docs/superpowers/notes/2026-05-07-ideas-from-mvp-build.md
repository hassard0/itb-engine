# Ideas Surfaced While Building the MVP

**Date:** 2026-05-07
**Context:** Captured during the v0.1.0 build per the design's "consider new solutions" commitment. None are merely engineering refinements — each is a research-direction or methodology shift worth weighing before the next plan.

---

## 1. Margin as signed distance to boundary, not raw expression value

**What:** Right now `ConstraintResult.margin` carries the raw constraint expression value (e.g., `g_4` for the positivity bound). Reinterpret it as the *signed Euclidean distance to the constraint boundary in coefficient space*, normalised by the constraint's gradient.

**Why it matters:** With true signed distances, boundary tracing becomes a Newton-style root-find — O(d) constraint evaluations per boundary point instead of O(N²) grid evaluations. For a serious sweep (high resolution, many coefficients) this is the difference between minutes and hours.

**Cost:** Each constraint module declares its gradient (or we autodiff symbolically). Modest engineering, big payoff at scale.

## 2. Constraint set-algebra in the API

**What:** The current `engine.check` does AND-intersection of constraints. Add operations to express *which constraints exclude a region*, *the union of regions excluded by a class*, *the symmetric difference between two sub-engines*.

**Why it matters:** The most informative result of a bootstrap is rarely "feasible / infeasible" — it's "this is the boundary the holographic-entropy-cone is enforcing here, and the amplitude bootstrap is enforcing there." Set algebra over regions is how that becomes legible.

**Cost:** A `Region` abstraction layered on the engine. Not a refactor — a layer.

## 3. Boundary-coloring by binding-constraint class

**What:** When the mapper traces boundaries, color each boundary segment by the *class* (A/B/C — amplitude / info-theoretic / universality) of the constraint that's binding there.

**Why it matters:** This turns the visualizer from a yes/no map into a *physics diagnosis*. If the holographic entropy cone is doing all the boundary work in some region, that's a clue that quantum-information-flavored models will be more constrained there than amplitude-flavored ones.

**Cost:** Minor visualizer change once #2 is done.

## 4. Fisher information metric on theory space

**What:** Coefficient space is currently treated as flat Euclidean. But theories that produce nearly-identical observables shouldn't count as "far apart" just because their numerical coefficients differ. Equip coefficient space with the Fisher information metric induced by predicted observables (graviton scattering at fixed kinematics, holographic entropy at fixed regions).

**Why it matters:** A physically-meaningful theory-space metric makes "this region is allowed" mean "these observably-distinct theories are allowed," not "these arbitrarily-coordinatised points are allowed." It's also what experimentalists actually care about — observable distinguishability.

**Cost:** Significant. Requires defining a fiducial set of observables and computing the metric per point. Feasible, but a real subproject.

## 5. Hierarchy of feasibility tolerance

**What:** SDP solvers return continuous "infeasibility certificates" (constraint violations measured in normalized units). Currently we collapse this to a hard bool. Expose a *tolerance level* parameter in the API: "feasible at 1σ" vs "feasible at 5σ". Different scientific questions live at different tolerances.

**Why it matters:** Real bootstrap results are quoted with confidence intervals. Hard yes/no obscures the genuinely interesting margin information.

**Cost:** Small once the engine is real-SDP rather than toy-comparison.

## 6. The "negative-result" research mode

**What:** Add a mode where the engine, given a theory + a set of constraints, *searches for the smallest deformation of the theory that violates feasibility*. The output is "this theory survives, but it's only X away from violating the holographic entropy cone."

**Why it matters:** This is more useful than "feasible / infeasible" for theorists trying to understand *why* their theory survives. It also surfaces the theory's most fragile prediction — the one most worth testing experimentally.

**Cost:** A new optimization layer (smallest-violating-perturbation as a min problem). Tractable.

## 7. Relegate cvxpy to lazy import; add a pure-Python feasibility shim for v1-class constraints

**What:** v1 constraints are linear inequalities on values; cvxpy is overkill and costs ~2× the import time. Make the SDP path opt-in for constraints that need it; v1 evaluations should run in pure Python.

**Why it matters:** Engineering hygiene. Engine startup matters when running thousands of feasibility checks per second during a sweep.

**Cost:** Trivial. Already half-done because v1 doesn't actually call cvxpy.

---

## What this list says about the architecture

The novelty hooks in the design (pluggable constraints + frameworks + research notebook) work — every idea above slots in as a new module or thin layer, none requires touching core types. Good signal that the boundaries we drew are correct.

The most valuable single move from this list, based on research-leverage per engineering-cost: **#3 (boundary-coloring by binding class)** combined with **#2 (constraint set algebra)**. Together they turn the platform from "does this theory work?" into "what physics is doing the constraining here?" — which is the actual question the field is stuck on.

These should be folded into the next plan.
