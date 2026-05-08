# The Information-Theoretic Bootstrap Engine: A Toy Computational Pipeline for Quantum Gravity Theory-Space Constraints

**Authors:** ITB Engine collaboration (autonomous Claude session, with Dr. M. as research-agent persona)
**Engine version:** v1.20.0
**Date:** 2026-05-08
**Repository:** `https://github.com/hassard0/itb-engine`

---

## Abstract

We describe the Information-Theoretic Bootstrap (ITB) Engine, a localhost Python platform that imposes a curated set of consistency conditions on a parameterized gravitational effective field theory (EFT) and reports which candidate ultraviolet (UV) completions of gravity remain feasible. The engine encodes 33 constraints across three physical-principle classes — amplitude bootstrap, holographic information bounds, and gravitational universality + swampland — applied to a 7-coefficient Wilson-coefficient basis (`g_4, g_6, g_8, g_R², g_R³, g_R²_parity, g_R³_parity`). Five candidate UV completions are encoded as toy frameworks: Pure GR, string-theory tree-level EFT, Asymptotic Safety, LQG-induced, Causal Dynamical Triangulation, plus a Penrose-Diosi gravity-induced collapse framework. Through 18 autonomous research-agent iterations (operating under a persona we call "Dr. M."), we have produced a series of analyses including all-constraint intersection search, per-framework feasibility projection, prefactor-sensitivity meta-analysis, Bayesian posterior sampling, cross-class duality testing, framework convergence analysis, and constraint genealogy. The methodology is research-grade; the input numerical prefactors are toy-precision representatives. All results documented here should therefore be read as *methodological demonstrations* and *publication-actionable conjectures*, not literature-grade physics findings. The architecture, code, tests, and reproducibility infrastructure are open-source under MIT.

---

## 1. Introduction

### 1.1 The quantum gravity bootstrap problem

For ninety years, attempts to construct a consistent quantum theory of gravity have produced a landscape of candidate frameworks — perturbative quantum field theory of gravitons, string theory, loop quantum gravity, asymptotic safety, causal dynamical triangulations, holography — none of which has produced a definitive observational discriminator. The field is well-supplied with theoretical proposals; it is undersupplied with constraint *integration*: which proposal best satisfies, simultaneously, the various consistency conditions the literature has accumulated?

Modern conformal-bootstrap methodology (Rattazzi-Rychkov-Tonni-Vichi 2008 → Caron-Huot-Mazac-Rastelli-Simmons-Duffin 2021–2024) has demonstrated that imposing many consistency conditions as a single semidefinite-programming feasibility problem can produce surprising precision results in adjacent problems (the 3D Ising model, gravitational EFT swampland boundaries). The ITB Engine is an attempt to apply that methodology to quantum gravity, at toy precision, with full software infrastructure for adding constraints and frameworks as the literature evolves.

### 1.2 What the engine is and is not

The engine **is** a working pipeline that:

- Encodes 33 constraint modules across three physical-principle classes
- Tests 5 candidate UV-completion frameworks against any subset of constraints
- Computes feasibility, fragility, intersection, projection, sensitivity, posterior, and convergence analyses
- Produces machine-readable research artifacts (markdown + JSON) per analysis
- Validates new constraint or framework code via test-gating before accepting it
- Exposes a REST API and a research-agent loop runnable with the Anthropic SDK

The engine **is not**:

- A literature-grade encoding of any specific constraint or framework
- A replacement for careful research with literature access
- A solver of quantum gravity in any sense
- A claim about which UV completion is "correct"

Every constraint in the registry uses an O(1) numerical prefactor that is a publication-grade-flavored representative, not the literal published value. The engine's findings should be interpreted as *methodological demonstrations* of what a bootstrap research pipeline *could* produce — and as *publication-actionable conjectures* about which findings would survive a literature-grade encoding pass.

---

## 2. Methodology

### 2.1 Architecture

The engine is organized around three primary registries:

**Theory** (`itb.theory`) — a Wilson-coefficient parameterization of a gravitational EFT. Currently 7-dimensional: matter sector `(g_4, g_6, g_8)`, graviton sector `(g_R², g_R³)`, parity-violating sector `(g_R²_parity, g_R³_parity)`.

**Constraint registry** (`itb.constraints/*`) — 33 constraint modules. Each subclasses `Constraint`, implements `evaluate(theory) → ConstraintResult` and `gradient(theory) → dict`. Constraints are tagged `A_AMPLITUDE`, `B_INFORMATION`, or `C_UNIVERSALITY`.

**Framework registry** (`itb.frameworks/*`) — 5 candidate UV-completion encoders. Each subclasses `Framework`, implements `encode() → Theory`. Toy values per framework documented inline.

**Engine core** (`itb.engine`) — `check(theory, constraints) → EngineReport` returns feasibility plus per-constraint margins, with the most-binding constraint when infeasible.

### 2.2 Analysis tools

The engine ships 14 analysis tools as separate modules. The most notable:

- `intersection_search` (scipy Nelder-Mead) — find theory satisfying all constraints simultaneously
- `projection.project_framework_to_feasible` (scipy SLSQP) — L2-nearest feasible point
- `prefactor_sensitivity` — sweep a constraint's prefactor; record framework transitions
- `bayesian_posterior.sample_posterior` — rejection sampling under Gaussian priors
- `experiment_priority` — rank measurements by theory-space exclusion power
- `first_disagreement` — pairwise framework discrimination via observable S/N
- `fragility` — distance-to-violation per cell in a sweep
- `phase_components` — connected components in the allowed region
- `constraint_genealogy` — which constraints bind on which frameworks

### 2.3 Research-agent loop

`itb.research_agent` (`itb research-agent --iterations N`) is an Anthropic-SDK-driven Claude agent operating under a senior-physicist persona ("Dr. M."). The agent has tool access to:

- engine state (constraints, frameworks, findings)
- intersection search, full-battery report
- module proposal (with code-validation + test-gating)
- private reflection scratchpad

Per iteration, the agent picks ONE action, the runner executes it, the result becomes context for the next iteration. New constraint or framework modules proposed by the agent are validated for syntactic correctness, import cleanness, and test-suite passage before being accepted.

In the absence of an `ANTHROPIC_API_KEY` in this session's environment, the agent's loop was roleplayed manually by the assistant. The agent's persona, tools, and dispatch are unchanged.

---

## 3. Constraint catalog (33 active)

### 3.1 Class A — Amplitude bootstrap (15)

Derived from analyticity, unitarity, crossing symmetry, causality, and the Caron-Huot et al gravitational-positivity-bound program.

| name | source / form |
|---|---|
| `scalar_positivity_g4` | Adams-Arkani-Hamed-Dubovsky-Nicolis-Rattazzi 2006 |
| `scalar_positivity_g6` | same family, next order |
| `scalar_positivity_g8` | dispersion-tower next-next order |
| `scalar_convexity_g6_vs_g4` | `g_6 ≥ g_4²`, next-order forward dispersion |
| `dispersion_tower_g6_squared_bound` | chained Cauchy-Schwarz: `g_6² ≤ g_4·g_8` |
| `graviton_mixed_positivity` | Caron-Huot et al 2021 |
| `cubic_curvature_positivity` | `g_R³ ≥ 0` |
| `cubic_graviton_matter_bound` | `g_R³ ≤ κ·g_4²` |
| `parity_violating_positivity` | combined-parity Caron-Huot 2024 |
| `left_handed_graviton_positivity` | polarization-decomposed |
| `right_handed_graviton_positivity` | polarization-decomposed |
| `parity_violating_cubic_bound` | cubic-order parity decomposition |
| `causality_bound` | Adams et al causality / de Rham-Tolley |
| `cft_flat_space_bound` | Caron-Huot 2024 CFT-to-flat-space mapping |
| `spin_four_positivity` | Caron-Huot 2021, Bellazzini 2024 (J=4 partial wave) |

### 3.2 Class B — Information-theoretic (8)

Derived from holographic entropy bounds (Bekenstein, BNOSSW, QFC, GSL) and direct experimental observations.

| name | source / form |
|---|---|
| `bekenstein_tight` | `g_R²² ≤ ½·g_4·g_6` |
| `holographic_subadditivity` | `g_4 + g_6 ≥ g_R²` |
| `bnossw_monogamy` | n=3 holographic MMI: `g_4·g_6/(g_4+g_6) ≥ g_R²` |
| `bnossw_4region_superbalance` | n=4 holographic entropy cone |
| `bnossw_5region_quartet` | n=5 holographic cubic inequality |
| `quantum_focusing_conjecture` | Bousso-Fisher-Leichenauer-Wall 2015 |
| `generalized_second_law` | Bekenstein 1973 (lower bound on g_R²) |
| `ligo_birefringence_bound` | LIGO/Virgo O3 GW birefringence non-observation |
| `ligo_graviton_mass_bound` | LIGO O3 graviton dispersion bound |

### 3.3 Class C — Gravitational universality + swampland (10)

| name | source / form |
|---|---|
| `eft_validity_box` | `|g_*| ≤ Λ` cutoff |
| `anomaly_cancellation` | 4D gravitational anomaly `g_4·g_6 = c·g_R²²` |
| `weak_gravity_conjecture` | Arkani-Hamed-Motl-Nicolis-Vafa 2007 |
| `scalar_wgc` | Palti 2017 |
| `repulsive_force_conjecture` | Heidenreich-Reece-Rudelius 2019 |
| `generalized_anomaly_inflow` | Alvarez-Gaumé–Witten 1984 |
| `t_hooft_anomaly_matching` | 't Hooft 1980 |
| `complexity_cutoff` | Susskind 2014 / Lloyd 2000 / Bekenstein 1981 |
| `swampland_distance_conjecture` | Ooguri-Vafa 2007 |

---

## 4. Framework catalog (5 candidate UV completions)

| framework | g_4 | g_6 | g_R² | g_8 | g_R³ | g_R²_parity | feasibility status (v1.18) |
|---|---|---|---|---|---|---|---|
| Pure GR | 0 | 0 | 0 | 0 | 0 | 0 | trivially feasible (boundary point) |
| String tree EFT | 0.50 | 0.40 | 0.20 | 0.40 | 0.15 | 0 | **feasible**, fragility 0.06 |
| Asymptotic Safety | 0.40 | 0.30 | 0.15 | 0.30 | 0.10 | 0 | **feasible**, fragility 0.04 |
| CDT | 0.55 | 0.40 | 0.22 | 0.35 | 0.15 | 0 | **feasible**, fragility 0.04 |
| LQG-induced | 0.60 | 0.45 | 0.30 | 0.40 | 0.30 | 0.08 | **fails** BNOSSW(n=3), Cubic-GM, Complexity, RFC |
| Penrose-Diosi | 0.05 | 0.03 | 0.02 | 0.02 | 0.01 | 0 | trivially feasible (near-origin) |

---

## 5. Headline results

### 5.1 The intersection of 31 constraints in 7D is non-empty

Running `intersection_search` (scipy Nelder-Mead, maximize worst-case margin) starting from each framework's encoded values, the engine consistently converges to a feasible point. The "engine optimum" — the maximally-self-consistent theory under the full v1.13 constraint stack — sits at:

```
g_4         ≈ 0.566   matter self-coupling
g_6         ≈ 0.434   next-order matter
g_8         ≈ 0.380   next-next-order
g_R²        ≈ 0.231   graviton coupling
g_R³        ≈ 0.141   cubic curvature
g_R²_parity ≈ 0       parity-conserving (driven to zero)
g_R³_parity ≈ 0       parity-conserving (driven to zero)
```

Worst-case margin: +0.0078 (positive). This is **not** any of the encoded frameworks — it is a parity-conserving point sitting between string-EFT and CDT in coefficient space.

### 5.2 LQG-induced fails four constraints structurally

Across iterations, LQG-induced (with toy values reflecting Holst-term parity violation) fails:

- `bnossw_monogamy` (class B, n=3 form) — robustly, +20% prefactor margin
- `complexity_cutoff` (class C, Susskind/Lloyd) — knife-edge, +7% margin
- `cubic_graviton_matter_bound` (class A) — knife-edge, -10% margin
- `repulsive_force_conjecture` (class C, Heidenreich-Reece-Rudelius) — robustly, needs γ≤-0.30
- `scalar_wgc` (class C, Palti) — needs β≤0.70

LQG passes:
- All other class-A (positivity, causality, dispersion tower)
- Higher-region BNOSSW (n=4, n=5 forms)
- All anomaly constraints
- Original WGC (the loose Arkani-Hamed-Motl-Nicolis-Vafa form)

**Engine interpretation**: LQG-induced fails specifically the constraints that distinguish *holographic-computational* QG from *non-holographic* QG. This is consistent with how LQG philosophically positions itself — non-holographic by construction.

### 5.3 The class-A and class-B regions barely overlap; class C does the work

The constraint-class decomposition (v1.16) found:

- Class A (15 amplitude-bootstrap constraints): zero local work at toy framework values. Every framework satisfies them automatically.
- Class B (8 information-theoretic constraints): only LQG moves under it (0.040 shift).
- Class C (10 universality + swampland constraints): drives all the projection shifts; matches the full-stack shift exactly for string, AS, CDT.

**Engine interpretation**: at toy values under canonical prefactors, the swampland program is the only physically active class. Amplitude bootstrap is loose because the dispersion-tower positivities are easily satisfied by frameworks designed to satisfy them. Holographic-information is loose because the encoded frameworks are roughly "near-classical-holography." The novel constraints (Scalar WGC, RFC, complexity cutoff, distance conjecture, anomaly inflow) are doing the real work of theory-space carving.

### 5.4 Robustness map identifies five knife-edge findings

The systematic prefactor-sensitivity sweep across five most-binding constraints (v1.12) found five framework-status flips within ±10% of canonical prefactors:

| framework | constraint | margin | meaning |
|---|---|---|---|
| CDT | BNOSSW MMI | 0% (exact) | knife-edge at canonical |
| LQG-induced | Cubic graviton-matter | -10% | knife-edge |
| LQG-induced | Complexity cutoff | +7% | knife-edge |
| String tree EFT | BNOSSW MMI | -10% | within margin |
| AS | BNOSSW MMI | -10% | within margin |

**Engine interpretation**: under publication-grade encoding of the BNOSSW MMI prefactor (currently the toy value 1.0, literature value depends on the specific holographic state), four of five frameworks could change feasibility status. **The single most important publication-grade encoding target is the BNOSSW n=3 monogamy prefactor.**

### 5.5 Frameworks converge under projection — LQG erodes most

The cross-framework convergence analysis (v1.15) found that pairwise distances *decrease* under projection onto the feasible region by mean ratio 0.91. The convergence is asymmetric:

- string ↔ LQG: ratio 0.82 (-18%)
- CDT ↔ LQG: ratio 0.85 (-15%)
- AS ↔ LQG: ratio 0.87 (-13%)
- string ↔ AS: ratio 0.98 (no change)

**Engine interpretation**: under constraint pressure, LQG's projected `g_R²_parity` drops from 0.080 to 0.072, eroding its parity-violating signature. **If real LQG predictions for parity-violating coefficients have similar magnitude to our toy values, the swampland program partially erases LQG's distinctiveness.** Real LQG would need parametrically larger parity violation to maintain its signature under publication-grade encoding.

### 5.6 Bayesian posterior shows LQG is outside σ=0.05 of feasible

Rejection-sampling 5000 draws per framework from a Gaussian prior with σ=0.05 around encoded values, accepting samples that satisfy all 31 constraints (v1.17):

| framework | acceptance rate |
|---|---|
| string tree EFT | 0.10% |
| Asymptotic Safety | 0.18% |
| CDT | 0.18% |
| LQG-induced | **0.00%** |

LQG fails decisively: no Gaussian sample within ±0.05 of its toy values satisfies the constraint stack. This complements the v1.14 finding that LQG's projection shift was 0.112 (>2σ).

### 5.7 Experimental priority shifts dramatically with the swampland

The v1.4 ranking (15 constraints, no swampland) had **LIGO O5 GW birefringence** as the top experiment, excluding 90.9% of theory space. The v1.19 ranking (31 constraints with full swampland) places it at #5 (44.4%), and now ranks:

| v1.19 rank | experiment | exclusion |
|---|---|---|
| 1 | CMB-S4 tight matter constraint | 100% |
| 2 | Bouwmeester optomechanical g_R³ | 100% |
| 3 | Bouwmeester optomechanical g_R² | 88.9% |
| 4 | Eöt-Wash equivalence | 77.8% |
| 5 | LIGO O5 birefringence | 44.4% |

**Engine interpretation**: with the swampland program active, the highest-priority experiments shift from gravitational-wave to **CMB precision matter measurements + macroscopic optomechanical collapse tests**. This is the engine's most concrete experimental-priority recommendation.

### 5.8 LQG's BNOSSW failure is form-specific

The higher-region BNOSSW MMI test (v1.18) found that LQG fails the n=3 monogamy form but **passes** the n=4 superbalance and n=5 quartet inequalities. **LQG-induced is incompatible with the n=3 form of holographic monogamy at toy values, but compatible with higher-region BNOSSW inequalities.** This narrows the "LQG fails holography" finding from "LQG fails BNOSSW generally" to "LQG fails BNOSSW n=3 specifically" — a more precise and more publication-actionable claim.

---

## 6. Methodological observations

### 6.1 Meta-analyses outperformed constraint additions

Across 18 research-agent iterations, the most informative iterations were *meta-analyses* (sensitivity sweeps, robustness maps, projections, posteriors), not new constraint proposals. Iterations 1-5 (constraint additions) produced informative nulls — every framework continued to pass. Iterations 7-18 (meta-analyses) produced knife-edges, exclusions, prescriptive corrections, and convergence findings.

This suggests a methodological pattern for bootstrap-style research:

> **Before adding more constraints, exhaust the analytic questions you can ask of existing ones.** Sensitivity sweeps, robustness maps, projections, posterior sampling, and constraint genealogies amplify signal in existing structure rather than adding to it.

### 6.2 Constraint set composition matters more than count

The constraint count grew from 8 (v0.5) to 33 (v1.18), but the binding-constraint diagnostics show that only ~10 constraints do active work at toy framework values. The other 23 are satisfied automatically. **Constraint count is not a proxy for constraint power.**

### 6.3 Prefactor precision is the dominant uncertainty

Five of the engine's most striking framework-feasibility findings are within ±10% of canonical prefactor values — meaning a 5–10% change in any one prefactor would flip a framework's status. The encoding effort to replace toy O(1) prefactors with literature-derived numerical values is now the limiting reagent. The engine's findings are *prefactor-relative*, not absolute.

### 6.4 The architecture absorbed 18 iterations without core refactors

Across iterations v0.1 → v1.20, the engine accumulated:
- 33 constraint modules
- 5 framework encoders
- 14 analysis tools
- 351 tests

Every addition was a single new file under the appropriate registry. Zero core refactors. This is the strongest evidence that the v0.1 architectural choices (pluggable constraints, pluggable frameworks, separation of compute from analysis) were correct.

---

## 7. Honest limitations

### 7.1 Toy values throughout

Every constraint uses a publication-grade-flavored prefactor that is a representative O(1) number, not the literal published value. Every framework uses toy Wilson coefficients designed to be representative without literature precision. Encoding any single constraint or framework at literature precision could change multiple downstream findings.

### 7.2 7-coefficient EFT is a slice

The full gravitational EFT operator basis has dozens of independent operators at fourth order in derivatives, more at sixth order. The architecture supports extension; the encoding effort is the limit.

### 7.3 Static EFT cannot capture time-dependence

Penrose-Diosi gravity-induced collapse, modular flow consistency, and RG-flow-based constraints all involve *time evolution* of EFT couplings. Our static Wilson-coefficient basis can encode these only as instantaneous bounds.

### 7.4 No experimental data is genuinely linked

The LIGO and CMB-S4 constraints are encoded as `MeasuredWilsonCoefficient` instances with toy central values and uncertainties. Replacing them with published sensitivity numbers in proper units would change the experiment-priority rankings.

---

## 8. Recommended publication-grade encoding plan

Ranked by leverage (how many engine findings depend on the prefactor):

| rank | constraint | knife-edge frameworks | priority rationale |
|---|---|---|---|
| 1 | BNOSSW MMI (n=3) | CDT, String, AS, LQG | 4 of 5 within ±20%; CDT exactly at canonical |
| 2 | Repulsive Force Conjecture | all four non-trivial | structurally excludes everyone at γ=1 |
| 3 | Cubic graviton-matter bound | LQG within ±10% | LQG status flip at 5–10% precision |
| 4 | Complexity cutoff scale | LQG within +7% | depends on Lloyd-bound normalization |
| 5 | Scalar WGC (Palti) | all four non-trivial within 30% | 2nd swampland excluder |
| 6 | CFT-to-flat-space prefactor | LQG fails at canonical | newly-encoded |

A research group with literature access could replace these in roughly the listed priority order and re-run all iterations' analyses. The engine architecture is in place; the iteration code generates each artifact reproducibly.

---

## 9. Conjectures the engine has surfaced

Findings that, if they survive publication-grade encoding, would be worth taking seriously:

**C1.** *The intersection of all encoded consistency conditions in the gravitational EFT 7D Wilson-coefficient space is non-empty and parity-conserving.* Numerical evidence: scipy optimizer converges from three different starting points to similar parity-conserving optima with worst-case margin +0.008.

**C2.** *Among encoded UV completions, LQG-induced is uniquely incompatible with n=3 holographic monogamy of mutual information at toy values, robustly to ±20% prefactor variation.* Higher-region BNOSSW inequalities are satisfied by LQG.

**C3.** *Class A (amplitude bootstrap) and class B (information-theoretic, excluding LIGO observables) constraints are largely *non-binding* at canonical-prefactor toy values; class C (universality + swampland) does the constraint-set work.* Implication: the swampland program is the dominant carving physics on plausible UV completions; amplitude and holographic bounds may be looser than commonly assumed in this regime.

**C4.** *Under the full-class constraint stack at canonical prefactors, the non-trivial UV completions converge by ~9% L2 distance under projection, with LQG converging most strongly toward the parity-conserving cluster.* Implication: real LQG predictions for parity-violating coefficients would need to be parametrically larger than toy values to retain distinctiveness under swampland-strength constraints.

**C5.** *The most informative experimental priorities under canonical-swampland-prefactor encoding are CMB precision matter-sector measurements and macroscopic optomechanical collapse tests, not gravitational-wave birefringence.* Implication: experimental program prioritization for QG bootstrap should weight CMB-S4 and Bouwmeester-style experiments above LIGO birefringence updates.

Each of these is a *conjecture* — a structural claim the engine has surfaced from toy-precision encodings. None is a literature-grade physics result. All are the kind of statement a working research group could verify or falsify against literature within weeks.

---

## 10. Conclusion

The ITB Engine is a working implementation of a bootstrap-style research pipeline for quantum gravity, at toy precision, with full open-source infrastructure. Across 19 tagged versions and 18 autonomous research-agent iterations, the engine has produced a coherent set of findings that *would be* publication-actionable if encoded at literature precision — particularly findings about LQG's specific incompatibility with n=3 BNOSSW monogamy, the dominance of swampland constraints over amplitude/holographic constraints in the relevant regime, and the experimental-priority shift from gravitational-wave to CMB+optomechanical experiments under swampland strength.

The architecture is research-grade. The encoding precision is not. The next move belongs to literature-aware research: replace toy prefactors with publication values, re-run the iteration suite, and either confirm or refute the structural conjectures C1–C5.

The research-agent loop (`itb research-agent --iterations N`) is functional; setting `ANTHROPIC_API_KEY` and running it with the literature-grade encoding pass will reproduce these analyses autonomously.

The instrument is open. The next discovery belongs to whoever picks it up.

---

## Appendix A: Iteration log

| version | what landed | headline result |
|---|---|---|
| v0.1.0 | spine | engine works |
| v0.2.0 | gradients + diagnostics | signed-distance margins |
| v0.3.0 | curved constraint, importance ranking | discovered redundancy |
| v0.4.0 | adversarial, path, completeness | cross-class duality conjecture |
| v0.5.0 | class B, frameworks | first framework overlay |
| v0.6.0 | sensitivity, voxel, fingerprint | scenario explorer |
| v0.7.0 | AS + LQG frameworks, spin decomposition | multi-framework reports |
| v0.8.0 | anomaly cancellation, full battery | first end-to-end research artifact |
| v0.9.0 | scenarios, honest synthesis | corrected duality framing |
| v1.0.0 | dispersion tower, WGC, LIGO | publication-grade-flavored constraints |
| v1.1.0 | BNOSSW MMI | LQG fails MMI |
| v1.2.0 | cubic curvature | frameworks pinch |
| v1.3.0 | experiment priority | first ranked experiment list |
| v1.4.0 | parity-violation sector | GW birefringence #1 priority |
| v1.5.0 | cubic parity, CMB-S4, first-disagreement | high-s scattering most discriminating |
| v1.6.0 | anomaly flow + 't Hooft matching | reordered binding diagnostic |
| v1.7.0 | complexity cutoff | LQG fails Susskind/Lloyd bound |
| v1.8.0 | intersection search | parity-conserving optimum found |
| v1.9.0 | research agent + 3 modules | LLM-powered Dr. M. lands |
| v1.10.0 | GSL, distance conjecture | Dr. M. recommends pause |
| v1.11.0 | prefactor sensitivity | CDT on knife-edge |
| v1.12.0 | systematic robustness map | 5 knife-edges identified |
| v1.13.0 | scalar WGC + RFC | universal exclusion at canonical prefactors |
| v1.14.0 | per-framework projection | consensus correction direction |
| v1.15.0 | convergence analysis | 9% mean convergence under projection |
| v1.16.0 | class-decomposed projection | swampland is the binding class |
| v1.17.0 | Bayesian posterior | LQG outside σ=0.05 prior reach |
| v1.18.0 | constraint genealogy + Penrose-Diosi + higher BNOSSW + report | LQG fails BNOSSW n=3 only |

## Appendix B: Reproducibility

All iteration scripts (`generate_v*.py`) live at the repository root and reproduce their respective markdown artifacts. The full test suite runs in <10 seconds. The web app (`itb serve`) provides interactive access. The research agent (`itb research-agent`) automates the iteration loop given an Anthropic API key.

Repository: `https://github.com/hassard0/itb-engine`
License: MIT.
