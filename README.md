# ITB Engine — Information-Theoretic Bootstrap for Quantum Gravity

**A research platform that constrains the space of possible quantum-gravity theories by imposing every consistency condition we can encode — amplitude positivity, causality, holographic-information bounds, the swampland, anomaly flow, black-hole thermodynamics — then confronts the survivors with *real experimental data* and asks what's left.**

> **Status:** v2.196 research loop · **1452 local tests, 7 skipped** · **1459 Vulcan tests with LALSuite installed** · **38 theoretical constraints (+4 ingested-data)** · **14 framework encoders** · **8 Wilson coefficients** · **9 observables** · **307 indexed result notes**
>
> Honest by construction: most constraint prefactors are O(1) placeholders ("the right streets, the wrong house numbers"). A dedicated **realism program** stress-tests every headline claim against that toy-prefactor uncertainty, so the repo distinguishes *robust conclusions* from *artifacts*. Read every claim below with that in mind — and see [Honest limitations](#honest-limitations).

📍 **Start here:** [**v2.196 R4 ParSpec published-bound surrogate**](docs/results/2026-06-20-v2.196-r4-parspec-published-bound-surrogate.md) (aligns the published qEFT bounds with the v2.195 source-event packet without promoting them to a public posterior) · [**v2.195 R4 ParSpec source-event covariance export**](docs/results/2026-06-20-v2.195-r4-parspec-source-event-covariance-export.md) (exports event-specific and combined covariance from the v2.194 source-event topology likelihood) · [**v2.194 R4 ParSpec event-topology likelihood**](docs/results/2026-06-20-v2.194-r4-parspec-event-topology-likelihood.md) (reruns the source-event likelihood with GW150914 H1/L1 and GW200129 H1/L1/V1 topology) · [**v2.193 R4 ParSpec same-event H1/L1 likelihood**](docs/results/2026-06-20-v2.193-r4-parspec-same-event-h1l1-likelihood.md) (reruns the coarse R4 H1/L1 likelihood on GW150914/GW200129 public strain) · [**v2.192 R4 ParSpec source-event alignment manifest**](docs/results/2026-06-20-v2.192-r4-parspec-source-event-alignment-manifest.md) (maps GW150914/GW200129 to exact GWOSC event versions and HDF5 strain URLs) · [**v2.191 R4 ParSpec qEFT source-asset audit**](docs/results/2026-06-20-v2.191-r4-parspec-qeft-source-asset-audit.md) (preserves source-package qEFT facts and resolves the source-axis power subpiece) · [**v2.190 R4 ParSpec engine-axis map contract**](docs/results/2026-06-20-v2.190-r4-parspec-engine-axis-map-contract.md) (turns the missing `ell_qEFT -> g_R4_*` map into an executable packet contract) · [**v2.189 R4 continuity ledger**](docs/results/2026-06-20-v2.189-r4-research-continuity-ledger.md) (preserves the v2.170-v2.188 run details) · [**v2.188 R4 ParSpec ringdown bridge**](docs/results/2026-06-20-v2.188-r4-parspec-ringdown-source-bridge.md) (source bridge) · [**v2.187 R4 waveform-likelihood posterior**](docs/results/2026-06-20-v2.187-r4-lalsuite-waveform-likelihood-posterior.md) (GW170608 baseline) · [**v2.186 R4 nuisance covariance export**](docs/results/2026-06-20-v2.186-r4-nuisance-covariance-export.md) (covariance scaffold) · [**v2.185 R4 LALSuite-calibrated GWOSC projection**](docs/results/2026-06-20-v2.185-r4-lalsuite-calibrated-gwosc-projection.md) (calibrated projection) · [**v2.184 R4/GWOSC/LALSuite report**](docs/results/2026-06-20-v2.184-r4-gwosc-lalsuite-research-report.md) (frontier summary) · [**v2.10 capstone**](docs/results/2026-06-09-v2.10-capstone.md) (the program in one page) · [**v2.0 research report**](docs/results/2026-06-09-v2.0-RESEARCH-REPORT.md) (full overview) · [**FINDINGS.md**](docs/FINDINGS.md) (what the engine discovered, in one page) · [**TAXONOMY.md**](docs/results/TAXONOMY.md) (all notes grouped by theme) · [**Predictions scorecard**](docs/results/2026-06-08-v1.83-master-scorecard.md) · [**Results index**](docs/results/INDEX.md) (chronological)

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

The program ran ~90 research cycles. The throughline:

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
The latest loop, v2.170-v2.196, turns the most promising gravitational-wave route into an executable nonclaiming pipeline:
- **v2.170-v2.171:** the symbolic R4 scale route now has a strict packet contract for a future source-backed `Lambda_R4` policy; no numeric policy is present yet.
- **v2.172-v2.173:** the parallel Weyl/G8 route now has a joint-likelihood packet contract; it remains blocked on a real `g_C+g_8` likelihood.
- **v2.174:** the engine selected the Bresciani-axis plus public-GWOSC reanalysis path after checking source/public candidates.
- **v2.175-v2.181:** the route gained a Bresciani R4 axis dictionary, public GW170608 H1/L1 HDF5 ingestion, source-backed 5PN/7PN R4 PN kernels, and a source-backed GWOSC projection seed.
- **v2.182-v2.183:** Vulcan runs LALSuite 7.7.1/IMRPhenomD, and the H1/L1 detector response now has a LALSuite-calibrated target.
- **v2.185:** the real GWOSC projection now uses that calibrated H1/L1 response instead of the v2.181 deterministic detector proxy.
- **v2.186:** the projection now exports a deterministic 81-point nuisance-grid covariance contribution over event mass, symmetric mass ratio, coalescence time, and phase.
- **v2.187:** Vulcan now builds a coarse network likelihood/posterior over the three R4 axes using real GWOSC strain, LALSuite IMRPhenomD baselines, calibrated H1/L1 channel response, and the established nuisance grid; the next blocker is replacing the linearized PN/IMR bridge with a source-owned full R4 IMR sampler.
- **v2.188:** the source-owned sampler blocker is split by importing the ParSpec higher-curvature ringdown route as a primary-source bridge for quartic EFT, including the published `ell_qEFT <= 51.3 km` bound; the remaining blockers are the engine-axis map, public posterior samples, event-set alignment, and systematics export.
- **v2.189:** the continuity ledger preserves every run from v2.170-v2.188 with note paths, artifact paths, retained details, numeric digests, frontier changes, and remaining blockers so top-level summaries do not drop intermediate results.
- **v2.190:** the missing ParSpec `ell_qEFT -> (g_R4_c1,g_R4_c2,g_R4_c3)` map is now an executable packet contract with explicit subrequirements for source-axis power, Bresciani-basis orientation, normalization, covariance pushforward, likelihood export, event alignment, and systematics.
- **v2.191:** the public arXiv source package is audited and hashed; it resolves the source-axis power subpiece with `p_qEFT = 6`, preserves the qEFT QNM deformation coefficients and event bounds, and confirms that no machine-readable qEFT likelihood object is present in the package.
- **v2.192:** the ParSpec source events are mapped to exact GWOSC event versions (`GW150914-v3`, `GW200129_065458-v1`) and public 4 kHz HDF5 strain URLs; the remaining event blocker is the actual same-event R4 likelihood rerun plus the GW200129 V1 detector-policy choice.
- **v2.193:** Vulcan reruns the coarse R4 likelihood on H1/L1 public strain for `GW150914-v3` and `GW200129_065458-v1`; the H1/L1 same-event subpiece is ready, while the GW200129 V1 response, source-event nuisance covariance, ParSpec likelihood, and qEFT axis map remain claim blockers.
- **v2.194:** Vulcan reruns the source-event likelihood with event-specific detector topology: `GW150914` uses H1/L1 and `GW200129` uses H1/L1/V1 with event-time LALSuite antenna responses; the V1 detector-response blocker is removed, while source-event nuisance covariance, ParSpec likelihood, and the qEFT axis map remain claim blockers.
- **v2.195:** the v2.194 source-event likelihood now exports event-specific and combined nuisance-marginalized R4 covariance for GW150914 and GW200129; the source-event covariance blocker is removed, while the public ParSpec/qEFT likelihood, source-backed operator-basis/axis map, posterior sampler, systematics, and external review remain claim blockers.
- **v2.196:** the published ParSpec qEFT 90% bounds are converted into an event-aligned, nonclaiming `ell_qEFT_km` surrogate attached to the v2.195 source-event packet; this removes the stale event-set mismatch and source-axis mismatch subpieces, while the machine-readable public likelihood and engine-axis map remain claim blockers.

The latest source-axis surrogate artifact is [v2.196 R4 ParSpec published-bound surrogate](docs/results/2026-06-20-v2.196-r4-parspec-published-bound-surrogate.md). The latest covariance artifact is [v2.195 R4 ParSpec source-event covariance export](docs/results/2026-06-20-v2.195-r4-parspec-source-event-covariance-export.md). The latest event-topology likelihood artifact is [v2.194 R4 ParSpec event-topology likelihood](docs/results/2026-06-20-v2.194-r4-parspec-event-topology-likelihood.md). The previous same-event H1/L1 artifact is [v2.193 R4 ParSpec same-event H1/L1 likelihood](docs/results/2026-06-20-v2.193-r4-parspec-same-event-h1l1-likelihood.md). The latest event-set manifest is [v2.192 R4 ParSpec source-event alignment manifest](docs/results/2026-06-20-v2.192-r4-parspec-source-event-alignment-manifest.md). The latest source-asset preservation artifact is [v2.191 R4 ParSpec qEFT source-asset audit](docs/results/2026-06-20-v2.191-r4-parspec-qeft-source-asset-audit.md). The latest executable blocker split is [v2.190 R4 ParSpec engine-axis map contract](docs/results/2026-06-20-v2.190-r4-parspec-engine-axis-map-contract.md). The run-detail preservation artifact is [v2.189 R4 research continuity ledger](docs/results/2026-06-20-v2.189-r4-research-continuity-ledger.md). The latest source bridge is [v2.188 R4 ParSpec ringdown source bridge](docs/results/2026-06-20-v2.188-r4-parspec-ringdown-source-bridge.md). The last GW170608-centered live-data baseline is [v2.187 R4 LALSuite waveform-likelihood posterior](docs/results/2026-06-20-v2.187-r4-lalsuite-waveform-likelihood-posterior.md), with [v2.186 R4 nuisance covariance export](docs/results/2026-06-20-v2.186-r4-nuisance-covariance-export.md) as the covariance bridge, [v2.185 R4 LALSuite-calibrated GWOSC projection](docs/results/2026-06-20-v2.185-r4-lalsuite-calibrated-gwosc-projection.md) as the calibrated projection, and the [v2.184 R4/GWOSC/LALSuite report](docs/results/2026-06-20-v2.184-r4-gwosc-lalsuite-research-report.md) as the frontier summary. This is progress toward a live gravitational-wave discriminator, not a framework exclusion or discovery claim.

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
pytest -q                                         # current full suite: 1452 passed, 7 skipped locally

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

Most experiments parallelize across cores; the heavy Monte-Carlo runs were done on a 16-core box.

For remote research-agent and Vulcan compute helpers:

```bash
pip install -e ".[agent,remote]"
python tools/vulcan.py run "hostname && python3 --version"
```

`tools/vulcan.py` defaults to `admin@192.168.4.178` and key auth through `~/.ssh/id_ed25519`; set `VULCAN_HOST`, `VULCAN_USER`, or `VULCAN_KEY` to override.

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
├── experiments/              265 cycle scripts (island census, center, data ingestion,
│                              meta-experiments) + stack.py (the constraint assembler)
├── tools/                    vulcan.py (remote compute), consult_drm.py, build_index.py
├── tests/                    308 test files (1452 local passing tests, 7 skipped)
├── docs/
│   ├── FINDINGS.md           ← curated findings (read this)
│   ├── CONSTRAINTS.md        ← the constraint stack, by class
│   └── results/              307 indexed result notes + INDEX.md (grouped by arc)
└── legacy/                   early-program report generators (v1.0–v1.19)
```

---

## License

See [LICENSE](LICENSE). Built with a local Gemma-4 physics co-theorist ("Dr. M.") as an adversarial check; computations run on a local 16-core server.
