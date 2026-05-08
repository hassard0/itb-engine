# Theorizing New Models for Quantum Gravity

**Date:** 2026-05-08
**Context:** Captured for v0.4. The user asked me to "learn more about the problem space and theorize new models we should try to crack this mystery." This is my honest deep-dive plus the new directions I think are most worth attempting numerically.

---

## What the field has actually tried

A frank inventory. Each of these has decades of work behind it; each has stalled at a different obstacle.

| Program | Strongest claim | Where it is stuck |
|---|---|---|
| **Perturbative QFT of gravity** | Linearized graviton, one-loop works | Non-renormalizable; loops diverge at 2-loop level (Goroff-Sagnotti 1986) |
| **String theory** | Finite, unitary; predicts gravitons | No unique vacuum; landscape of ~10⁵⁰⁰ vacua; no testable low-energy prediction |
| **Loop quantum gravity** | Discrete spacetime, area/volume operators | Recovers smooth GR semiclassical limit poorly; matter coupling unclear |
| **Causal Dynamical Triangulations** | Numerically produces emergent 4D dS phase | Hard to add matter; phase transitions not fully understood |
| **Asymptotic safety** | UV fixed point would resolve renormalizability | Existence of non-trivial fixed point is debated; truncation-dependent |
| **Causal sets** | Spacetime as partial order; fundamentally simple | Dynamics underconstrained; recovering GR is non-trivial |
| **Holography (AdS/CFT)** | Geometry from entanglement; precise duality | Only proven for negative cosmological constant; ours is positive |
| **Penrose-Diósi gravity-induced collapse** | Testable; bridges QM/GR through measurement | Limited scope; if experiments rule it out, framework is dead |

What every program shares: a starting commitment to a particular *substance* (strings, loops, simplices, sets). The starting substance dictates the difficulties. Maybe the substance is the wrong primitive.

## What I think the field is actually missing

After staring at this for a while, my honest read:

**The substance debate is a distraction.** What the candidate programs really differ on is not what spacetime is "made of" but what *primitives* they take as fundamental — geometry, algebra, computation, information, causality. These choices are interchangeable in surprising ways (e.g., Connes' spectral triples make algebra and geometry equivalent). The real differences between programs are *which constraints* they take seriously, not which substance.

If that's right, then the productive move is not to pick a better substance — it's to map the *constraint space itself* and look for which constraints are doing real work, redundant, or contradictory across programs. That is exactly what the ITB engine is built to do. v0.3 already produced one such result: it found `g_6 ≥ 0` is redundant given `g_4 ≥ 0` and the convexity bound. That kind of automatic redundancy detection, scaled up, is genuinely useful.

## Ten new theoretical directions worth attempting

Numerically tractable. Some genuinely original; some recombinations of known ideas in directions the field hasn't pushed.

### 1. **Spectral gravity from random matrices**

Connes' spectral triples make algebra and geometry equivalent: the eigenvalue spectrum of the Dirac operator determines the manifold up to isometry. Now postulate the universe is a random Hermitian operator drawn from a known ensemble (Wishart, GUE, GOE). The expected spectrum *is* the metric. The variance is the quantum fluctuations of geometry.

What's new: numerical experiments on small-matrix ensembles to see what spectrum-derived geometries look like. To my knowledge, no one has done a systematic numerical exploration of this.

What it would predict: spectral dimension reduction at the Planck scale (the spectrum has a UV cutoff intrinsically), specific corrections to Einstein-Hilbert from the spectral action.

### 2. **Enriched causal sets**

Standard causal sets (Bombelli-Sorkin) take partial order as primitive; spacetime distance falls out of interval cardinality. Push: each link in the partial order carries a quantum amplitude. The partial order itself is in superposition — different orderings have different probabilities.

What's new: a partial-order quantum process where the order isn't fixed. This dissolves "what was the first event" because the order is a quantum variable.

What it would predict: a natural reason why entanglement entropy scales with area (causal proximity is the entanglement structure), with calculable corrections.

### 3. **Computational complexity as the cutoff**

The universe doesn't compute beyond some complexity. Susskind's "complexity = action" connects this to gravity. Take complexity bounds as primitive — let *they* set the discreteness scale, instead of the Planck length.

What's new: a model where the UV cutoff is an *algorithmic* notion (BQP, PH boundaries), not a length. This naturally connects QG to computability.

What it would predict: black hole evaporation time bounded by holographic complexity (Susskind has argued for this); dimensional reduction at high complexity (the spectrum of compute thins out); a complexity-theoretic proof of the no-cloning theorem applied to gravitational degrees of freedom.

### 4. **Generative dynamics via amplitude bootstrap**

Don't postulate a Lagrangian. Postulate consistency conditions on amplitudes (unitarity, crossing, analyticity, soft theorems) and let amplitudes *be* the theory. Modern S-matrix bootstrap pushed all the way to QG.

What's new: this is what Caron-Huot and collaborators have been doing for gravity since 2021, but no one has built a localhost engine that combines all known consistency conditions across multiple frameworks. **This is what we are actually building.**

### 5. **De Sitter holography as a tensor network**

AdS/CFT works on hyperbolic geometry (negative cosmological constant). MERA tensor networks reproduce hyperbolic AdS automatically. Our universe is dS (positive cosmological constant). What tensor network reproduces dS?

Recent work (Susskind, Maldacena, Cotler-Strominger) suggests: the network has finite Hilbert dimension, lives on a "stretched horizon," and has a specific asymmetric entanglement structure.

What's new: numerically simulating proposed dS tensor networks and seeing whether they reproduce de Sitter physics.

What it would predict: a finite number of observables in our observable universe (because Hilbert dim is finite), specific forms for vacuum decay rates.

### 6. **Octonionic gravitational coupling space**

Furey, Dixon, and others have argued the Standard Model's particle content is encoded in octonions. Extend: treat gravitational couplings as octonion-valued quantities. Spin, torsion, and higher-rank curvature naturally fit into the non-associative algebra.

What's new: nearly-zero numerics on this. Furey's program is mostly algebraic.

What it would predict: 3 generations of matter as a consequence of octonion structure, specific relations between gauge and gravitational couplings.

### 7. **Anomaly-flow as theory-fixing**

In 1D, anomaly cancellation completely fixes the theory (free fermion at c=0). In 2D, gravitational anomaly fixes the 26-dim bosonic string. In 4D, can generalized anomaly conditions nearly-fix QG?

What's new: very little numerical work. Most anomaly arguments are formal.

What it would predict: a finite number of consistent QG theories, classified by their anomaly content.

### 8. **The "no privileged constraint set" duality**

Conjecture: every amplitude-bootstrap constraint has an information-theoretic partner that gives the same allowed region in their overlap regime. This would mean the constraint classes A, B, C aren't fundamentally different — they're related by a duality similar to S-duality in string theory.

What's new: testing this numerically by computing the same allowed region two ways (amplitude side and info-theoretic side) and checking they agree. Our engine architecture is set up to do exactly this.

What it would predict: if the duality holds, we don't need both classes — picking the easier one suffices. If it fails, the failure modes tell us where the classes provide independent information.

### 9. **Theory-space phase transitions**

If the allowed region has multiple disconnected components, those are phases. The boundaries are constraints. Different phases would correspond to different *kinds* of UV completion (e.g., string-like vs. asymptotic-safety-like). Mapping the phase diagram of QG would be a real new thing.

What's new: nobody has computed a phase diagram for the allowed-EFT space. The engine v0.3 can already detect disconnected components in 2D.

What it would predict: distinct universality classes of QG completions, each with characteristic predictions for low-energy observables.

### 10. **Experiments-as-constraints (the inverse problem)**

Most QG work is forward: postulate theory, predict observable. Invert: take well-measured experimental results (cosmological constant, particle masses, gauge coupling unification, gravitational wave dispersion bounds) and treat them as defining constraints on QG. Then ask: what's the *minimal* extension of GR + QFT that respects all of them?

What's new: as a Bayesian theory inference problem, this is barely attempted at the QG level. Cosmologists do similar work for dark energy models; the QG version is open.

What it would predict: a posterior distribution over QG theories, weighted by experimental data. Most likely a multimodal distribution with peaks corresponding to different theoretical frameworks.

## Picking one for v0.4

Out of these ten, which to attempt now?

**Honest leverage analysis:**
- #1, #5, #7 are massive subprojects (full lattice simulations / random matrix studies / anomaly classifications).
- #6 (octonions) is too speculative for a first numerical attack.
- #2, #3, #10 are full programs that don't fit in our current EFT-on-flat-space scaffold.
- #4 is what we are already building.
- **#8 (duality between constraint classes) and #9 (phase transitions) are uniquely well-fitted to our existing architecture.**

I'm going to extend the engine to make a real concrete graviton EFT (adding the R² coefficient as a third Wilson coefficient and a Caron-Huot-style mixed positivity bound that couples it to `g_4` and `g_6`). That moves us out of the toy scalar EFT into actual graviton physics, and gives us the substrate to attempt #8 and #9 in v0.5.

The other v0.4 ideas — #A adversarial, #C path distance, #E completeness — are tools that pay dividends regardless of which model we run them on.

## Logged for v0.5+

- **#8 Cross-class duality test** — check whether amplitude-bootstrap and (eventual) holographic-info constraints give the same allowed region in their overlap.
- **#9 Phase diagram of theory space** — once #C path-distance is in place, run it on a 3D coefficient space and see if the allowed region is connected.
- **#10 Experiments-as-constraints** — encode a known measured Wilson coefficient as a one-sided inequality + uncertainty.
- **#7 Anomaly-flow constraints** — write down 4D generalized gravitational anomaly cancellation as a constraint module. Hard but novel.
- **#3 Complexity-as-cutoff** — define a complexity functional on Wilson coefficients and use it as a constraint.

These are the directions for the next several iterations.
