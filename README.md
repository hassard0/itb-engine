# ITB Engine — Information-Theoretic Bootstrap for Quantum Gravity

**A research platform that constrains the space of possible quantum-gravity theories by imposing every consistency condition we can encode — amplitude positivity, causality, holographic-information bounds, the swampland, anomaly flow, black-hole thermodynamics — then confronts the survivors with *real experimental data* and asks what's left.**

> **Status:** v2.219 research loop · **local and remote Linux validation current** · **38 theoretical constraints (+4 ingested-data)** · **14 framework encoders** · **8 Wilson coefficients** · **9 observables** · **330 indexed result notes**
>
> Honest by construction: most constraint prefactors are O(1) placeholders ("the right streets, the wrong house numbers"). A dedicated **realism program** stress-tests every headline claim against that toy-prefactor uncertainty, so the repo distinguishes *robust conclusions* from *artifacts*. Read every claim below with that in mind — and see [Honest limitations](#honest-limitations).

**Start here:** [**v2.219 first-principles ringdown resolvability**](docs/results/2026-06-29-v2.219-qnm-ringdown-resolvability.md) (self-contained Fisher-matrix calc turning a QNM deviation into a detector SNR: the universal coefficients rho*sigma_f/f=0.554, rho*sigma_tau/tau=2.00 for the l=2 n=0 mode [validated scale-invariant / function-of-Q-only, matching Berti-Cardoso-Will]; a fractional deviation delta needs rho>2.8/delta at 5sigma, so the source-backed axial R4 reach sharpens from eta_2~0.04 at current SNR~8 [edge of perturbative] to ~0.003 at 3G/LISA SNR~100) · [**v2.218 axial<->polar QNM isospectrality + R4 parity-splitting discriminator**](docs/results/2026-06-29-v2.218-qnm-isospectrality.md) (self-contained, needs no blocked appendix: the axial Regge-Wheeler and polar Zerilli potentials yield the SAME QNM spectrum through the in-house solver to ~1e-6 [l=3], confirming GR isospectrality; the ~9e-4 residual is the parity-splitting noise floor, and the source-backed axial R4 shift sits ~3.5e4x above it -- so isospectrality breaking is the parity-resolved R4 discriminator the v2.209 'g_R4_c3 is dark' finding flagged; full splitting magnitude stays gated on the un-sourceable even-parity correction) · [**v2.217 R4 ringdown overtone-sensitivity hierarchy**](docs/results/2026-06-29-v2.217-qnm-r4-overtone-sensitivity.md) (source-backed: the n=1 first overtone is ~491x more sensitive to the R4 quartic operator than the n=0 fundamental, with an OPPOSITE-sign damping response -- overtone ringdown is the dominant lever for higher-curvature gravity; the full odd-parity delta_V stays un-sourceable so that McManus cross-check negative is preserved) · [**v2.216 R4 ringdown cross-validation**](docs/results/2026-06-29-v2.216-qnm-r4-cross-validation.md) (two independent source-backed routes to the R4 QNM shift agree on SIGNS -- frequency down, damping up -- but the convention-independent damping/frequency ratio disagrees ~2.6x: the single-(r_g/r)^10 term is qualitatively right, quantitatively incomplete; honest negative preserved) · [**v2.215 source-backed R4 ringdown sensitivity**](docs/results/2026-06-29-v2.215-qnm-r4-sensitivity.md) (the engine computes the R4 quartic odd-parity sensitivity -1728 e_10 by fusing the SGB potential with the McManus e_10) · [**v2.214 operator->QNM sensitivity via the published parametrized basis**](docs/results/2026-06-29-v2.214-qnm-parametrized-basis.md) (the contraction route: decompose delta_V in the McManus (r_H/r)^j basis, contract with peer-reviewed e_j) · [**v2.213 Riccati QNM solver + sensitivity precision requirement**](docs/results/2026-06-29-v2.213-qnm-riccati-precision-requirement.md) (independent QNM cross-check; scoped that recomputing the sensitivity in-house needs ~1e-3 precision) · [**v2.212 operator->QNM sensitivity vs published parametrized-ringdown**](docs/results/2026-06-29-v2.212-qnm-parametrized-validation.md) (honest negative: the WKB-at-peak sensitivity is stable but NOT accurate vs the McManus et al. e_j) · [**v2.211 QNM solver validation suite**](docs/results/2026-06-29-v2.211-qnm-validation-suite.md) (the in-house QNM solver reproduces 8 tabulated modes across the scalar/EM/gravitational Regge-Wheeler family) · [**v2.210 first-principles WKB QNM solver**](docs/results/2026-06-29-v2.210-qnm-wkb-solver.md) (validated in-house black-hole-spectroscopy: reproduces omega_220/omega_221 to ~0.2% and computes operator->QNM sensitivities) · [**v2.209 R4 ParSpec qNM sourceable-rank determination**](docs/results/2026-06-29-v2.209-r4-parspec-qnm-sourceable-rank-determination.md) (source-cited finding that a full-rank R4 ringdown discriminator is not source-backed and the parity-odd axis g_R4_c3 is dark) · [**v2.208 R4 ParSpec pyRing likelihood-rerun packet**](docs/results/2026-06-21-v2.208-r4-parspec-pyring-likelihood-rerun-packet.md) (specifies the reproducible pyRing runtime-coordinate rerun packet) · [**v2.207 R4 ParSpec qNM-to-Bresciani source-route graph**](docs/results/2026-06-21-v2.207-r4-parspec-qnm-bresciani-source-route-graph.md) (records the public-source route graph and the remaining missing operator edge) · [**v2.206 R4 ParSpec public-likelihood packet gate**](docs/results/2026-06-21-v2.206-r4-parspec-public-likelihood-packet.md) (documents the public-likelihood acceptance gate and current no-public-packet finding) · [**FINDINGS.md**](docs/FINDINGS.md) (curated findings) · [**ROADMAP.md**](docs/ROADMAP.md) (where the research should go next) · [**Results index**](docs/results/INDEX.md) (chronological)

---

## What this is

The engine represents a higher-derivative gravitational EFT by **8 dimensionless Wilson coefficients**:

| sector | coefficients | meaning |
|---|---|---|
| matter | `g_4, g_6, g_8` | forward-limit scattering positivity moments (s², s³, s⁴) |
| graviton | `g_R2` (R²/Euler), `g_C` (Weyl²), `g_R3` (R³) | curvature couplings |
| parity | `g_R2_parity, g_R3_parity` | gravitational Chern–Simons / Pontryagin |

It then asks three questions, in order:

1. **Which theories are even consistent?** Intersect 38 theoretical constraints (positivity, causality, holography, swampland, anomaly flow, BH-entropy/WGC). The survivors form a thin "island" in coefficient space.
2. **What do the consistent theories predict?** Each is a point with a falsifiable observable fingerprint (sub-mm gravity, η/s, cosmic birefringence, GW signals, BH entropy, inflation…).
3. **What does the data say?** Ingest real measurements as additional constraints (sub-mm gravity, cosmic birefringence, GW speed & dispersion) and watch the island shrink — sometimes to a tension.

---

## The big picture — what the engine found

The program has generated 300+ indexed research notes. The throughline:

### A consistent quantum-gravity EFT is rare and low-dimensional
The consistent "island" is **~0.6% of a comparable-magnitude coefficient box** and **~3.4 effective dimensions** — one stiff collective-scale mode with several sloppy directions (the swampland's "thin landscape," made quantitative). The most-robustly-consistent point (the island's Chebyshev center) predicts a near-holographic `a/c ≈ 0.92`, a KSS-violating `η/s ≈ 0.81`, and a **sub-mm fifth force at ~93 µm** that independently reproduces a dark-energy-scale scenario. *(v1.73–75)*

### One operator, many epochs
The single R² coupling `g_R2` plays three roles depending on its scale: the **Starobinsky inflaton** at a high cutoff (n_s ≈ 0.964, r ≈ 0.004 — dead-center in the Planck+BICEP sweet spot), the **dark-energy scalaron / sub-mm fifth force** at the meV cutoff, and the **holographic η/s and a/c** of a putative dual. The engine connects amplitude positivity, holography, black-hole thermodynamics, inflation, and dark energy as facets of the *same* coefficients. *(v1.67, 71, 72, 82, 86)*

### Data ingested — and a sharp tension
The engine is one of few QG-phenomenology tools that **folds in real experiments**:
- **Sub-mm gravity (Eöt-Wash)** *excludes* the naive unscreened dark-energy scalaron by ~7×, collapsing the island to ~2% of its theoretical volume. *(v1.76–77)*
- **Cosmic birefringence (Minami–Komatsu, β = 0.34°±0.09°)** makes the engine *prefer a nonzero, positive-handed parity coupling* — the first data-driven preference for a parity-violating universe. *(v1.78)*
- These two, plus the engine's own anomaly-inflow axiom, are in **~2.8σ tension** (robust across the toy-mapping uncertainty): a consistent EFT can match the birefringence only if the scalaron is **screened**. *(v1.79–80)*
- **GW170817 speed** is *blind* to higher-derivative gravity (frequency-suppressed), but **LIGO's GW dispersion test** reaches the dark-energy cutoff — *which observable* matters as much as which sector. *(v1.84–85)*

### Current live-data frontier: R4 through GWOSC and LALSuite
The latest loop, v2.170-v2.208, turns the most promising gravitational-wave route into an executable nonclaiming pipeline:
- **v2.170-v2.171:** the symbolic R4 scale route now has a strict packet contract for a future source-backed `Lambda_R4` policy; no numeric policy is present yet.
- **v2.172-v2.173:** the parallel Weyl/G8 route now has a joint-likelihood packet contract; it remains blocked on a real `g_C+g_8` likelihood.
- **v2.174:** the engine selected the Bresciani-axis plus public-GWOSC reanalysis path after checking source/public candidates.
- **v2.175-v2.181:** the route gained a Bresciani R4 axis dictionary, public GW170608 H1/L1 HDF5 ingestion, source-backed 5PN/7PN R4 PN kernels, and a source-backed GWOSC projection seed.
- **v2.182-v2.183:** remote Linux validation runs LALSuite 7.7.1/IMRPhenomD, and the H1/L1 detector response now has a LALSuite-calibrated target.
- **v2.185:** the real GWOSC projection now uses that calibrated H1/L1 response instead of the v2.181 deterministic detector proxy.
- **v2.186:** the projection now exports a deterministic 81-point nuisance-grid covariance contribution over event mass, symmetric mass ratio, coalescence time, and phase.
- **v2.187:** remote Linux validation builds a coarse network likelihood/posterior over the three R4 axes using real GWOSC strain, LALSuite IMRPhenomD baselines, calibrated H1/L1 channel response, and the established nuisance grid; the next blocker is replacing the linearized PN/IMR bridge with a source-owned full R4 IMR sampler.
- **v2.188:** the source-owned sampler blocker is split by importing the ParSpec higher-curvature ringdown route as a primary-source bridge for quartic EFT, including the published `ell_qEFT <= 51.3 km` bound; the remaining blockers are the engine-axis map, public posterior samples, event-set alignment, and systematics export.
- **v2.189:** the continuity ledger preserves every run from v2.170-v2.188 with note paths, artifact paths, retained details, numeric digests, frontier changes, and remaining blockers so top-level summaries do not drop intermediate results.
- **v2.190:** the missing ParSpec `ell_qEFT -> (g_R4_c1,g_R4_c2,g_R4_c3)` map is now an executable packet contract with explicit subrequirements for source-axis power, Bresciani-basis orientation, normalization, covariance pushforward, likelihood export, event alignment, and systematics.
- **v2.191:** the public arXiv source package is audited and hashed; it resolves the source-axis power subpiece with `p_qEFT = 6`, preserves the qEFT QNM deformation coefficients and event bounds, and confirms that no machine-readable qEFT likelihood object is present in the package.
- **v2.192:** the ParSpec source events are mapped to exact GWOSC event versions (`GW150914-v3`, `GW200129_065458-v1`) and public 4 kHz HDF5 strain URLs; the remaining event blocker is the actual same-event R4 likelihood rerun plus the GW200129 V1 detector-policy choice.
- **v2.193:** remote Linux validation reruns the coarse R4 likelihood on H1/L1 public strain for `GW150914-v3` and `GW200129_065458-v1`; the H1/L1 same-event subpiece is ready, while the GW200129 V1 response, source-event nuisance covariance, ParSpec likelihood, and qEFT axis map remain claim blockers.
- **v2.194:** remote Linux validation reruns the source-event likelihood with event-specific detector topology: `GW150914` uses H1/L1 and `GW200129` uses H1/L1/V1 with event-time LALSuite antenna responses; the V1 detector-response blocker is removed, while source-event nuisance covariance, ParSpec likelihood, and the qEFT axis map remain claim blockers.
- **v2.195:** the v2.194 source-event likelihood now exports event-specific and combined nuisance-marginalized R4 covariance for GW150914 and GW200129; the source-event covariance blocker is removed, while the public ParSpec/qEFT likelihood, source-backed operator-basis/axis map, posterior sampler, systematics, and external review remain claim blockers.
- **v2.196:** the published ParSpec qEFT 90% bounds are converted into an event-aligned, nonclaiming `ell_qEFT_km` surrogate attached to the v2.195 source-event packet; this removes the stale event-set mismatch and source-axis mismatch subpieces, while the machine-readable public likelihood and engine-axis map remain claim blockers.
- **v2.197:** the qEFT source-axis route now has a checked `ell_qEFT -> qNM deformation` Jacobian using the source coefficients preserved in v2.191; the missing `qNM deformation -> Bresciani R4 engine axes` operator-basis map remains the decisive claim blocker.
- **v2.198:** the ParSpec continuity ledger preserves the v2.190-v2.197 run chain with note paths, artifact paths, retained details, numeric digests, blocker changes, validation counts, and claim gates so README/FINDINGS/reports do not lose intermediate details.
- **v2.199:** the source-event absolute gamma metadata is now attached from GWOSC preferred PE rows: `M_f,z = 63.1,0.09` for GW150914 and `60.2,0.18` for GW200129; absolute gamma is computable for the source events while the qNM-to-Bresciani operator map and public likelihood remain blockers.
- **v2.200:** the qNM-to-Bresciani gate now defines the exact source-backed packet shape needed next: a finite 3x4 matrix from qNM deformation axes into `g_R4_c1/c2/c3`, with row rank 3. The current qEFT source object is only a rank-1 gamma-to-qNM ray, so the engine blocks any map or claim promotion.
- **v2.201:** the public pyRing `EFT_QNMs` branch is now a hash-pinned source probe. It confirms six quartic plus/minus branch tables and a rank-4 local branch-column QNM matrix, while preserving the decisive blockers because plus/minus are mode-splitting branches, not independent Bresciani operator axes.
- **v2.202:** pyRing's imaginary-frequency convention now has a source-backed linearized conversion into fractional damping-time axes. The exported spin-zero tau matrix is rank 2, while the route remains blocked on pyRing-to-Bresciani orientation, independent operator-axis interpretation, public likelihood, systematics, and adversarial review.
- **v2.203:** the pyRing quartic EFT frequency and damping-time rows are now evaluated at source-event remnant spins for GW150914 and GW200129. This exposes a few-percent pyRing-runtime Berti-GR versus ParSpec-high-spin normalization gap and keeps the claim gate closed.
- **v2.204:** the pyRing-runtime-to-ParSpec-high-spin normalizer gap now has an explicit nonclaiming policy. Runtime Berti-GR normalization is allowed for internal pyRing reruns, while ParSpec high-spin rows are comparison-only until a source-backed operator-axis map exists.
- **v2.205:** the pyRing-to-Bresciani orientation source audit is now complete as a no-map ledger. pyRing branch directions remain local QNM branch-splitting columns, and synthetic branch-to-operator maps are explicitly forbidden.
- **v2.206:** the public ParSpec/qEFT likelihood route now has a tested packet gate. The current public recheck finds no machine-readable posterior samples, covariance matrix, or log-likelihood grid; the published-bound surrogate remains nonclaiming continuity evidence only.
- **v2.207:** the source-route graph for the qNM-to-Bresciani hard blocker is now explicit. Public sources provide ParSpec qNM axes, qEFT and pyRing/Cano QNM pieces, and Bresciani K-to-engine projection, but no source-backed qNM-to-K operator edge; the best next build is a pyRing EFT likelihood-rerun packet in runtime coordinates.
- **v2.208:** the pyRing EFT likelihood-rerun packet is now concrete. It pins public pyRing and GWOSC inputs, the paper-named pyRing execution commit, source-event remnant spins, a 12-row event/direction config grid, runtime-coordinate policy, and the required posterior/log-likelihood export contract; execution, systematics, external review, and the qNM-to-Bresciani map remain blockers.

The latest artifact is [v2.208 R4 ParSpec pyRing likelihood-rerun packet](docs/results/2026-06-21-v2.208-r4-parspec-pyring-likelihood-rerun-packet.md). The latest route graph is [v2.207](docs/results/2026-06-21-v2.207-r4-parspec-qnm-bresciani-source-route-graph.md), and the latest public-likelihood gate is [v2.206](docs/results/2026-06-21-v2.206-r4-parspec-public-likelihood-packet.md). The current roadmap is [docs/ROADMAP.md](docs/ROADMAP.md). This is progress toward a live gravitational-wave discriminator, not a framework exclusion or discovery claim.

### The "data-driven EFT"
Folding consistency + the two ingested experiments points to a specific, registered theory — `discovered_data_driven` — a **screened-scalaron, positive-handed-parity EFT** that matches cosmic birefringence and predicts GW/PTA parity signals just below current reach. It sits where *none* of the 13 textbook frameworks do. `itb predict discovered_data_driven`. *(v1.79)*

### Meta-experiments: auditing the engine itself
- **The Gödel test:** the ~37 theoretical axioms are **internally consistent** (no contradiction among the principles); every minimal inconsistent core contains a *data* constraint — the tensions are empirical, not logical. *(v1.87)*
- **The minimum decisive experiment set:** **6 measurements** pin all 8 coefficients (matter scattering ×2, GW/CMB birefringence, BH entropy, η/s, a cubic-graviton amplitude). The inflation detection contributes *nothing* to pinning; g_8 and g_R3 are genuine blind spots with no current probe. *(v1.88)*
- **The phylogenetic tree:** treated as RG-running couplings under a toy asymptotic-safety flow, the frameworks form a **rooted tree** — with a connected clade of discrete-spacetime approaches and **LQG flowing to Group Field Theory** (its actual proposed UV completion). *(v1.89)*

A full, navigable account of every cycle is in [docs/FINDINGS.md](docs/FINDINGS.md) and the [results index](docs/results/INDEX.md).

---

## Quickstart

```bash
git clone https://github.com/hassard0/itb-engine && cd itb-engine
python -m venv .venv && . .venv/bin/activate     # (Windows: .venv\Scripts\activate)
pip install -e ".[dev]"
pytest -q                                         # current full suite is recorded in the latest run note

# the affirmative answer: what a consistent QG EFT looks like + its full fingerprint
itb predict discovered_data_driven
itb predict string_tree_eft --json

# write the current multi-persona research-swarm agenda
itb swarm-plan

# run a flagship experiment (each writes a figure + JSON to /tmp and prints a summary)
python experiments/island_census.py 300000        # how rare/low-dimensional is the island
python experiments/min_experiment_set.py           # what is the minimum experiment program
python experiments/godel_test.py 1500000           # is the engine internally consistent
```

Most experiments parallelize across cores; heavy Monte-Carlo runs are intended for a multi-core workstation or a separately configured remote Linux worker.

Remote validation is intentionally configured outside committed documentation.
Use your own SSH configuration or environment-specific wrapper when reproducing
remote checks; do not commit private access details.


---

## How it works

### The constraint stack (`experiments/stack.py`)
`build_stack(...)` assembles the **38 theoretical constraints** (3 classes: A amplitude, B information, C universality). Real data is **opt-in** so the theoretical-only stack is preserved:

```python
from stack import build_stack
theory = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")     # 38 theoretical constraints
with_data = build_stack(..., include_data=True,          # + Eöt-Wash sub-mm
                             include_birefringence=True,  # + Minami–Komatsu
                             include_gw_speed=True,        # + GW170817 speed
                             include_gw_dispersion=True)   # + LVK dispersion
```

Each constraint exposes `.evaluate(theory) → (satisfied, margin, signed_distance_margin)`, `.gradient(...)`, and a `.constraint_class`. Full list in [docs/CONSTRAINTS.md](docs/CONSTRAINTS.md).

### The realism program
Six "knife-edge" prefactors are tunable knobs with stated factor-of-~2 plausibility windows (`CANONICAL`, `PLAUSIBLE_RANGES` in `stack.py`). Every headline result is re-checked across that uncertainty — e.g. the birefringence-vs-gravity tension survives 99% of the mapping box (v1.80). This is the repo's core discipline: **which conclusions survive when we admit we only know the house numbers to within a factor of two.**

### Observables & predictions (`src/itb/predict.py`, `src/itb/gravitational_observables.py`)
Each framework has a falsifiable fingerprint — sub-mm Yukawa range, η/s (KSS units), GW/cosmic birefringence, chiral Hellings–Downs (PTA), BH extremal-entropy shift (WGC), Starobinsky (n_s, r). `itb predict <framework>` renders it; the Jacobians power the Fisher / experimental-design analyses.

### Frameworks (`src/itb/frameworks/`)
14 encoders: catalogued (string tree-EFT, asymptotic safety, LQG-induced, CDT, causal sets, group field theory, Hořava–Lifshitz, emergent gravity, Penrose–Diósi, pure GR), engine-discovered (`discovered_novel`, `discovered_parity_violating`, `discovered_high_g8`), and the data-driven (`discovered_data_driven`).

---

## Honest limitations

- **Toy prefactors.** Most constraint coefficients are O(1) placeholders; the realism program tells you which conclusions are robust to that, but exact coordinates move with the numbers.
- **Order-of-magnitude observable mappings.** Cross-sector maps (κ_β for birefringence, lam_map for η/s, the BH-entropy and GW-dispersion normalizations) are schematic; the robust content is signs, orderings, and scalings — not precise values.
- **Hints, not discoveries.** Cosmic birefringence is a ~3.6σ hint; screening is modeled as a binary flag (really density-dependent); CMB β is the axion–*photon* coupling while GW/PTA are axion–*graviton* (linked only under a single-axion assumption).
- **Schematic RG / ghost.** The phylogeny uses toy beta functions; higher-derivative gravity is scheme-dependent and has a massive spin-2 ghost — the flow is *structure*, not trajectories.

The program is built to surface these honestly rather than hide them; several cycles are *negative* or *self-correcting* results (e.g. the a-theorem is redundant in this basis, v1.70; GW170817 is blind, v1.84).

---

## Architecture

```
itb-engine/
├── src/itb/
│   ├── theory.py              Wilson-coefficient dataclass
│   ├── constraints/           38 theoretical constraints + 4 opt-in data constraints
│   ├── frameworks/            14 framework encoders
│   ├── gravitational_observables.py, observables.py, holographic_ac.py
│   ├── predict.py             `itb predict` fingerprint
│   ├── fisher.py              Fisher metric on theory space
│   ├── scope.py               engine-validity (local / Lorentz / fundamental flags)
│   ├── cli.py                 `itb` command
│   └── api/server.py          FastAPI web app
├── experiments/              277 cycle scripts (island census, center, data ingestion,
│                              meta-experiments) + stack.py (the constraint assembler)
├── tools/                    reproduction helpers, validation helpers, build_index.py
├── tests/                    319 test files (latest full-suite count is in the v2.208 report)
├── docs/
│   ├── FINDINGS.md           ← curated findings (read this)
│   ├── CONSTRAINTS.md        ← the constraint stack, by class
│   └── results/              319 indexed result notes
└── legacy/                   early-program report generators (v1.0–v1.19)
```

---

## License

See [LICENSE](LICENSE).
