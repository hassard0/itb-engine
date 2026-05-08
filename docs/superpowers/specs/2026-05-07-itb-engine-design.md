# ITB Engine — Design Spec

**Date:** 2026-05-07
**Status:** Draft, pending user review
**Working title:** Information-Theoretic Bootstrap Engine (ITB)

---

## Goal

Build a localhost research platform that constrains the space of possible quantum gravity theories by simultaneously imposing every well-established consistency condition we know of — amplitude consistency, holographic entropy bounds, modular flow constraints, swampland-style positivity bounds — as a single semidefinite-programming feasibility problem. The output is a *map of allowed theory space*: which gravitational EFT Wilson coefficients survive every constraint at once, and how the major candidate frameworks (string theory, asymptotic safety, LQG-induced corrections) sit relative to that allowed region.

The deeper bet: the bootstrap methodology has demonstrated, in adjacent problems, the ability to extract surprising precision results from pure consistency. No one has yet unified the modern information-theoretic constraints on quantum gravity with the S-matrix bootstrap into a single solver. That gap is engineering, not physics, which means we can plausibly close it — and the result is a real research tool that produces theory-space exclusions as its native output.

A first-class architectural commitment: the platform must remain *open* to new constraints, new framework encoders, and new hypotheses that occur to us during development. The act of building it is itself a research process.

---

## Background and motivation

Quantum gravity has been an open problem since the 1930s. Major frameworks (string theory, loop quantum gravity, causal dynamical triangulations, asymptotic safety, causal sets) each have internal merits but no observational discriminator and no agreed-upon discriminator on the horizon. The field is stuck in a state of multiple internally-consistent candidates with no way to choose between them.

Two methodological developments changed what is possible in the last 15 years:

1. **The conformal bootstrap** (Rattazzi, Rychkov, Tonni, Vichi 2008+ → modern numerical bootstrap, Simmons-Duffin et al). By imposing crossing symmetry, unitarity, and analyticity as semidefinite constraints, the bootstrap solved the 3D Ising critical point to eight decimal places — a problem considered intractable for decades. The methodology generalizes to any consistency-constrained theory.

2. **Information-theoretic bounds on quantum gravity.** Work on holographic entanglement entropy (Ryu-Takayanagi 2006), the holographic entropy cone (Bao-Nezami-Ooguri-Stoica-Sully-Walter 2015), Bousso bounds, modular flow (Connes-Rovelli, Tomita-Takesaki), and gravitational positivity bounds (Caron-Huot, de Rham, Tolley, Zhou 2021-2024) has produced a growing list of *universal* constraints any consistent quantum theory of gravity must satisfy.

These two threads have not been unified. The bootstrap community works primarily with S-matrix consistency. The information-theoretic community works primarily analytically. A semidefinite-programming engine that imposes both classes of constraints simultaneously is the natural next step — and it is buildable on a single workstation with current SDP tooling.

---

## Approach: the ITB

### Core method

For a given parameterization of gravitational physics — at minimum, the Wilson coefficients of the leading-order gravitational EFT (R, R², Riemann², Riemann_μνρσ Riemann^μνρσ, Riemann³ terms, plus matter couplings) — pose the following question to a solver:

> Is there *any* theory consistent with all of the following constraints simultaneously?

Then sweep over parameter space and map out the allowed region. The constraints divide into three classes:

**A. Amplitude / S-matrix bootstrap conditions**
- Crossing symmetry of 2→2 graviton scattering
- Unitarity (Im T(s) ≥ 0 in partial waves)
- Analyticity in the Mandelstam variables, with poles only at physical states
- Causality / positivity bounds on EFT coefficients (Adams-Arkani-Hamed-Dubovsky-Nicolis-Rattazzi 2006, generalized to gravity by Caron-Huot et al)
- Soft graviton theorems (Weinberg's universal IR structure)

**B. Information-theoretic / holographic conditions**
- Holographic entropy cone inequalities (subadditivity, strong subadditivity, monogamy of mutual information, Bao-Nezami inequalities)
- Bousso covariant entropy bound: entropy on a light-sheet ≤ A/4G
- Bekenstein bound: S ≤ 2π R E for any localized system
- Quantum focusing conjecture (Bousso-Fisher-Leichenauer-Wall 2015)
- Modular flow consistency (Tomita-Takesaki structure must close)

**C. Universality / gravitational uniqueness conditions**
- Equivalence principle (universal coupling to stress-energy)
- Diffeomorphism invariance constraints on counterterms
- Black hole entropy formula: S_BH = A/4G + corrections
- ANEC and its quantum generalizations (averaged null energy condition)

Each constraint is encoded as a feasibility condition (equality, inequality, or semidefinite condition) on the Wilson coefficients. The unified solver checks whether the conjunction is feasible. If yes, the point is in the allowed region. If no, it is excluded — and the engine records *which* constraint was binding, which is itself useful information.

### Why this can work on a localhost

Modern SDP solvers (SDPB, MOSEK, SCS) handle problems with thousands of constraints and modest variable counts on a single workstation. The bootstrap community routinely runs problems of this scale on laptops; the largest 3D Ising bootstrap papers used a few hundred CPU-hours on commodity hardware. The user has access to vulcan (Linux + 4× V100, plenty of CPU) for runs that exceed the Windows box.

---

## Architecture

The platform is a localhost web app with a Python compute backend and a browser UI. It is structured around five components, each with a clear interface so they can be developed and tested independently:

### 1. Theory Encoder
**Purpose:** Translate any candidate parameterization of QG physics into a vector of Wilson coefficients (or a more general structured object: SDP variables + auxiliary parameters).

**Inputs:** User-specified gravitational EFT terms (textual / form-based), or one of the built-in framework encoders (string-theory low-energy EFT, asymptotic safety predictions, etc.).

**Outputs:** A structured `Theory` object that downstream constraints can be evaluated against.

**Why a separate component:** This is the natural place for *new* parameterizations to be added as we think of them. Adding a framework should not require touching the constraint engine.

### 2. Constraint Catalog
**Purpose:** A registry of constraint modules. Each constraint is a self-contained module with a single interface: `evaluate(theory) → SDPCondition`.

Each module declares:
- Its name and source citation
- Which class it belongs to (A/B/C above)
- Its constraint type (linear, quadratic, semidefinite, etc.)
- Its required theory parameters
- A test suite: "this theory is known to satisfy/violate this constraint"

**Why this matters for the novelty hook:** Adding a newly-discovered constraint should be a single-file addition, not a refactor. If during development I realize, say, that the c-theorem-like monotonicity of holographic entanglement under RG flow is a constraint we haven't encoded, I should be able to add it as a new module without disturbing anything else.

### 3. Constraint Engine (the SDP solver)
**Purpose:** Given a `Theory` and a subset of constraints, solve the feasibility problem and return:
- Feasible / infeasible
- If infeasible: which constraints are binding (the certificate of infeasibility)
- If feasible: the dual variables (which constraints are tight)
- Numerical certificates so results are reproducible

**Implementation:** Python with `cvxpy` as the modeling layer; backend solvers configurable (SCS for fast/loose, MOSEK or SDPB for tight bounds). A `dry-run` mode for symbolic checking before invoking the solver.

### 4. Theory-Space Mapper
**Purpose:** Sweep over parameter space, call the Constraint Engine at each point, and build a map of the allowed region.

**Strategies:**
- Grid sweep (low-dim, exhaustive)
- Active-learning / Bayesian sweep (focus near the boundary)
- Analytic boundary tracing where the constraint geometry permits

**Output:** A structured dataset that the Visualizer consumes.

### 5. Visualizer + Research Notebook
**Purpose:** Browser UI showing the allowed theory space, with controls for which constraints are imposed, which are relaxed, where the major frameworks sit. Also: an integrated *research notebook* where novel hypotheses, observed regularities, and "this constraint should exist but isn't in the catalog yet" notes get captured during exploration.

**Why a notebook is part of the system:** The user's directive is to consider new solutions as we build. The notebook is the structural commitment to that — a place where insight gets captured and turned into new constraint modules or new framework encoders.

### Component diagram

```
┌──────────────────────┐    ┌────────────────────────┐
│   Theory Encoder     │ ←→ │  Framework Library     │
│ (parameterizations)  │    │  (string, AS, LQG, …)  │
└──────────┬───────────┘    └────────────────────────┘
           │
           ▼
┌──────────────────────┐    ┌────────────────────────┐
│  Constraint Engine   │ ←─ │   Constraint Catalog   │
│   (SDP solver)       │    │  (A/B/C modules, ext.) │
└──────────┬───────────┘    └────────────────────────┘
           │
           ▼
┌──────────────────────┐
│ Theory-Space Mapper  │
│   (sweep / active)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Visualizer + Notes  │
│   (browser UI)       │
└──────────────────────┘
```

---

## Tech stack

- **Backend:** Python 3.11+, FastAPI, cvxpy, NumPy, SciPy, SymPy. Optional: SDPB binding for tight bootstrap bounds (used on vulcan for heavy runs).
- **Frontend:** Plain HTML + JS + Plotly for v1; upgrade to React if interactions get complex. No framework lock-in early.
- **Storage:** SQLite for the research notebook + run history; flat files (JSON / Parquet) for theory-space sweep results.
- **Compute deployment:** primarily Windows localhost; long-running sweeps may shell out to vulcan (Linux, 4× V100, more CPU). Compute backend is split so this is a config flip, not a rewrite.

---

## Built-in framework encoders (initial set)

These are the "candidate theories" we drop onto the allowed-space map to see where each sits:

1. **Pure GR + minimal matter** — the baseline. Should be allowed by all constraints. If not, the engine has a bug.
2. **String-theory low-energy EFT** — Wilson coefficients from tree-level α' expansion. Known to satisfy all swampland positivity bounds in established checks.
3. **Asymptotic safety** — couplings from the Reuter fixed-point predictions. Whether AS satisfies all info-theoretic bounds is debated, so this is genuinely informative.
4. **LQG-induced effective action** — leading-order corrections from spin-foam amplitudes (when a translation exists; partial in some regimes).
5. **Higher-derivative gravity (R², Gauss-Bonnet, Lovelock)** — a parameterized family used as a fitness landscape.

Each framework is a separate module under `frameworks/`, mirroring the constraint catalog structure.

---

## Novelty hooks (the "consider new solutions" commitment)

To keep the platform a research tool rather than a closed implementation:

1. **Pluggable constraints.** Adding a new constraint is a single-file `.py` module that exports `evaluate(theory) → SDPCondition` plus metadata. The engine auto-discovers modules in `constraints/`.
2. **Pluggable framework encoders.** Same shape under `frameworks/`.
3. **Research notebook (DB-backed).** A "novel hypothesis" entry has fields for: the conjecture, where it came from, whether it has been encoded as a constraint, and any preliminary tests. Tied to the codebase via git commit references.
4. **Hypothesis-testing mode.** Ad-hoc constraint injection: state a candidate constraint in the UI, have the engine evaluate it against the existing allowed region, and see whether it tightens or contradicts current results — *without* committing it to the catalog.
5. **Periodic structural review.** Every milestone, an explicit step: "are there constraints we have not yet encoded? Does the architecture suggest new connections?" This is a calendar item on the project, not a vague intention.

The expected value of this discipline is one or more genuinely new constraints, framework encodings, or insights surfacing during the build that would not have surfaced if the platform were rigidly scoped at the start.

---

## Success criteria

Tiered honestly so we can measure against them:

- **Minimum (high confidence, ~90%):** The platform reproduces the published constraint regions of Caron-Huot et al on gravitational EFT positivity, plus the holographic entropy cone for small numbers of regions, in a single unified codebase. This alone is a useful tool; we have a faster way to ask "does this theory pass?" than the literature provides.
- **Likely (medium confidence, ~50%):** Combining constraints that have not been combined in the literature *tightens* known exclusions by a measurable amount. Publishable as a methods + results paper.
- **Stretch (low but real, ~15%):** The intersection of all imposed constraints rules out a *named candidate framework* (e.g., shows that asymptotic safety's predicted Wilson coefficients sit outside the allowed region). Significant result.
- **Moonshot (small, ~2-3%):** The intersection narrows to a one-parameter family or a single point. Functionally solves QG. I do not expect this; the rigor of the methodology means a null result here is itself a real datum.

A "fail" outcome — the constraints are too weak to rule anything new out — is itself a publishable null result and tells the field something important about where to look next.

---

## Risk and mitigation

- **SDP scaling.** Some constraints (full holographic entropy cone for many regions) generate semidefinite programs too large for a workstation. Mitigation: tier the engine — small-region cones run locally; large ones go to vulcan; some inequalities can be sampled rather than enforced uniformly.
- **Translation friction.** Holographic constraints are formulated in AdS/CFT; bulk EFT statements need translation. Mitigation: stay explicit about the regime each constraint applies to. The Constraint Catalog metadata records this.
- **Constraint redundancy.** Some constraints imply others. Mitigation: redundancy is fine for correctness; the engine just records which is binding. We document known logical implications for clarity.
- **My own theoretical errors.** I will get some constraint encodings wrong. Mitigation: the test suite per constraint module — every constraint ships with examples of theories that pass and theories that fail, drawn from literature. Tests run on every change.

---

## Out of scope (v1)

- Solving the matter-side Standard Model. We treat matter content as input, not output.
- Full numerical simulation of bulk quantum gravity dynamics. The engine is a *constraint solver*, not a dynamical simulator.
- Non-perturbative effects beyond what the constraint catalog captures. Some non-perturbative input (black hole entropy formulas, etc.) is encoded as constraints; full non-perturbative dynamics is not.
- A discovery-grade statistical framework on observational data. Bayesian inference against LIGO/CMB/etc. data is an obvious v2 extension; v1 is theory-space-only.

---

## Open questions to resolve in the implementation plan

1. **Initial constraint set ordering.** Which constraints to encode first? My instinct: positivity bounds (well-formulated, smaller SDPs) → holographic entropy cone for n ≤ 4 regions → modular flow consistency. To be confirmed in the plan.
2. **Wilson-coefficient parameterization depth.** How many higher-curvature operators to include? Trade-off: more operators = bigger SDP, more interesting theory space, slower runs.
3. **Vulcan handoff protocol.** When does a sweep get punted to vulcan? Manual flag, automatic threshold, or hybrid?
4. **Initial UX shape.** Single-page dashboard vs multi-page (encoder / engine / map / notebook as separate routes)? Decide during plan.

---

## Next steps

1. User reviews this spec.
2. Adjustments per feedback.
3. Move to writing-plans skill and produce a detailed implementation plan with milestones, task breakdown, and review checkpoints.
4. Begin implementation with the constraint catalog and a minimal end-to-end pipeline (one constraint, one framework, one feasibility check, one plot) before broadening.
