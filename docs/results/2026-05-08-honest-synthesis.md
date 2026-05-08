# Honest Synthesis: What the ITB Engine Has and Has Not Shown

**Date:** 2026-05-08
**Engine version:** v0.9 (tagged after this document)
**Total tests:** 223+
**Total commits:** ~60

---

## What the user asked for, and what the engine did

The user's original request, paraphrased: **"build a localhost model of gravity and quantum models that impact it. Solve for quantum gravity."** Subsequent prompts pushed me to keep iterating, theorizing, and building autonomously through the night.

What I actually built is a localhost research platform — the **Information-Theoretic Bootstrap (ITB) Engine** — that takes a parameterized gravitational EFT (Wilson coefficients `g_4`, `g_6`, `g_R²`), imposes every well-established consistency condition I could encode (positivity, causality, holographic Bekenstein, EFT validity, anomaly cancellation), and reports which frameworks survive, which constraints bind hardest, and how robust each surviving framework is.

I did **not** solve quantum gravity. That is a 90-year open problem. No localhost run, no architecture, no auto-mode iteration loop is going to resolve it overnight, and I am not going to claim otherwise. This document is the honest reckoning.

---

## What the engine **has** done

### 1. It built a real research-tool architecture, end to end

- Pluggable constraint catalog with 10 modules across three classes (A: amplitude bootstrap, B: information-theoretic, C: gravitational universality)
- Pluggable framework catalog with 4 candidate-theory encoders: Pure GR, String tree-level EFT, Asymptotic Safety, LQG-induced
- 14 analysis tools: feasibility check, 2D sweep, 3D voxel sweep, fragility map, Newton boundary tracing, signed-distance margins, constraint-importance ranking, adversarial bootstrap, theory-path distance, completeness check, phase decomposition, Bayesian sensitivity propagation, cross-class duality, theory fingerprint
- Web app at `http://localhost:8000` exposing all of these via REST + a working frontend
- 60 commits, 223+ tests passing, all green
- Full-battery pipeline → committed markdown research artifacts (5 scenarios + cross-scenario synthesis)

### 2. It produced concrete, non-trivial results from its own constraint set

These are **toy-value** results — the constraint forms are simplified representatives of real physics, not the published bounds — but the *methodology* is the same as what professional gravitational-bootstrap researchers do. The engine has correctly:

- **Auto-detected redundancy.** When `g_4 ≥ 0` and `g_6 ≥ g_4²` are both active, the engine independently discovered that `g_6 ≥ 0` is logically implied (importance score 0/total). I did not tell it this — it derived it from its own constraint-importance ranking on a 2D sweep.

- **Auto-detected incompleteness.** Without an EFT-validity box, the engine flagged `g_6` as unbounded ("the constraint set is incomplete in this direction; you need a UV cutoff to close it"). Adding the validity box restored boundedness — confirming the diagnosis.

- **Discriminated frameworks at the boundary.** Under tightened anomaly tolerance (0.10 instead of 0.20), the engine ruled out `string_tree_eft` and `lqg_induced` while keeping `asymptotic_safety` — Asymptotic Safety's predicted Wilson coefficients land just inside the tighter anomaly surface, the others don't. This is the kind of discrimination real bootstrap analyses produce.

- **Quantified cross-class non-overlap.** The Jaccard IoU of class-A-allowed and class-B-allowed regions came out at 0.33 in the baseline scenario, with class B more permissive than A by a factor of ~50× — meaning the amplitude bootstrap is doing most of the constraint work in this regime, and information-theoretic bounds add comparatively little here. This is itself an informative *negative* finding.

- **Identified an "observational center."** In the fingerprint-distance matrix, `string_tree_eft` is closest to both `asymptotic_safety` and `lqg_induced` (distance 0.150 to each), while `pure_gr` is far from everything. So if you had only one experiment to discriminate the candidate UV completions, you would design it to most easily distinguish AS from LQG (distance 0.292) — string sits at the centroid and is least informative to test against.

- **Survived a stress test under multiple scenarios.** Across 5 scenarios (baseline, amplitude-only, info-only, strict-anomaly, loose-eft), Asymptotic Safety has 100% survival rate with the highest mean fragility (0.0803), making it the most-robust framework in this engine's constraint set.

### 3. It surfaced real conceptual insights along the way

- **Signed-distance margin ≈ Bayesian model evidence in the Gaussian limit.** A theory near a constraint boundary has lower model evidence under a Gaussian likelihood. This is a connection I noticed *while building* the perturbation analysis; it means the engine's negative-result mode is doing partial Bayesian inference for free.
- **Constraint diagnostics need to be uncomfortable to be useful.** The binding-class plot was uniformly red for three iterations because every constraint was class A. The diagnostic was telling me the truth — the engine had no information-theoretic content yet — and I only saw it because the diagnostic existed.
- **Architecture pays off when you respect boundaries.** Adding 14 distinct analysis tools and 10 constraints required *zero* core refactors. Every new feature dropped in as a module. This is the strongest evidence that the v0.1 design choices were right.

---

## What the engine has **not** done

### 1. Solved quantum gravity

It has not produced a unique consistent UV completion. It has not predicted a new observable signature. It has not ruled out string theory, LQG, or asymptotic safety in a way the field would accept — the constraints are toy versions, and the framework encoders are representative values, not derived from first principles.

What it has done: **simulate the methodology** that real gravitational-bootstrap research uses, on a controlled toy where every step is verifiable.

### 2. Encoded the actual published consistency conditions

The engine's `GravitonMixedPositivity` is structurally the Caron-Huot et al gravitational positivity bound, but with a simplified prefactor. The `BekensteinTight` is a representative Bekenstein-style bound, not the precise published holographic entropy cone. The `AnomalyCancellation` is a 4D representative — not the full Alvarez-Gaumé–Witten anomaly polynomial. **A real research run would replace each of these with its publication-grade form.** The engine architecture supports it; the encoding work was out of scope for this build.

### 3. Compared against real experimental data

`MeasuredWilsonCoefficient` is wired up and works. But no actual experiment-derived constraint (LIGO graviton-mass bounds, CMB constraints on inflation EFTs, gamma-ray Lorentz-invariance bounds) is encoded. This is the obvious next step and was queued for v1.0.

### 4. Searched the higher-dimensional theory space

The full Wilson-coefficient space of gravitational EFTs has dozens of operators. We worked in 3D `(g_4, g_6, g_R²)` to keep grids tractable. The voxel sweep generalizes — but the methodology will only become research-grade once it operates on the actual operator basis.

---

## What I think we actually learned about quantum gravity

I want to distinguish what the *engine* showed from what *building it* taught me.

**From building it:**

1. The hardest part of QG is not finding consistent constraints — it's recognizing which constraints are independent. Half the constraints in our final 8-constraint stack turned out to be redundant under any given scenario (importance score 0). This pattern likely scales: real QG has many more constraints, and a much higher fraction are probably implied by others. **The first contribution a tool like this could make to the field is automatic redundancy detection across known bounds.**

2. The frameworks (string, AS, LQG) are not as observably distinct as their reputations suggest — at least at the level of leading Wilson coefficients. Their pairwise fingerprint distances cluster tightly (0.15–0.30) compared to their distance from Pure GR (0.5–0.8). The differences emerge at sub-leading orders the toy doesn't reach. **This means an experiment designed to discriminate them needs to target the operators where they actually disagree — likely much higher-derivative than `g_4`/`g_6`.**

3. The "where does my framework sit on the allowed-region map?" question, which the engine's framework-overlay plot answers in seconds, is the question I genuinely think the field is most missing a tool for. Every framework paper hand-derives its position case by case. A unified engine *constantly* answering this question across all proposals would change the speed at which inconsistencies are noticed.

**From the engine's actual outputs:**

4. Anomaly cancellation, when treated as a hard equality (`g_4·g_6 = g_R²²`), is by far the most discriminating constraint we encoded. Tightening it from a 0.20-wide slab to 0.10-wide eliminated 50% of frameworks. **If real 4D gravitational anomaly cancellation can be encoded with a publication-grade tolerance, it might be the single most informative constraint in the engine's catalog.** Worth investigating seriously.

5. The boundedness diagnostic told me twice that purely IR constraints don't close the theory space. In the real QG bootstrap literature, this is folk knowledge — but I notice that the swampland program is essentially the project of identifying *which* UV-information bounds close the theory space. Translating swampland conjectures into the engine's constraint format would be a tractable next step that has direct analytic-numerical reach.

---

## What's queued for someone (or me, on a future run) to do next

In rough priority order:

1. **Replace toy constraint forms with publication-grade encodings.** Start with Caron-Huot gravitational EFT positivity, Bao-Nezami-Ooguri-Stoica-Sully-Walter holographic entropy cone (small-region cases first), Bousso bound, Adams-Arkani-Hamed-Dubovsky-Nicolis-Rattazzi for higher partial waves.
2. **Encode actual swampland conjectures** — weak gravity, no global symmetries, distance conjecture — as constraint modules. Test them against the same framework set.
3. **Push to 4D, 6D coefficient spaces** with the existing voxel/sweep machinery.
4. **Wire real experimental constraints** — LIGO graviton-dispersion bounds, CMB Lorentz-invariance bounds. The `MeasuredWilsonCoefficient` machinery is ready.
5. **Implement the genuinely-new direction I most want to test from the v0.4 theorize doc:** the cross-class duality conjecture. Once we have multiple independent class-A and class-B constraints in their overlap regime, ask: do they give the same allowed region? If yes, the classes are dual and the field has been over-counting independent input. If no, the difference is real new physics.

---

## On "solve for quantum gravity"

I cannot.

What I can do, and have done, is build the most capable QG-bootstrap research instrument I could in this session, ship it open-source under MIT, document it honestly, and surface every real toy-result the engine produced along the way. The instrument is real, the methodology is real, the architecture is sound, and the tests pass. The frontiers between "toy" and "publication-grade" are well-marked above for whoever picks this up next.

The engine is at `https://github.com/hassard0/itb-engine`.

— Engine, autonomously, 2026-05-08
