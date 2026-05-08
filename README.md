# ITB Engine

**Information-Theoretic Bootstrap engine for quantum gravity theory-space exclusions.**

A localhost research platform that constrains the space of possible quantum gravity theories by simultaneously imposing every well-established consistency condition we can encode — amplitude bootstrap, holographic-information bounds, gravitational universality, anomaly flow, computational complexity bounds — and asking which UV completions survive, how robust they are, and what experiments would tighten the picture.

The engine is at v1.8.0, ~302 tests, 24 active constraints across 7 Wilson coefficients, 4 candidate-framework encoders, 18 iteration cycles documented, and a non-empty intersection of all 24 constraints found by numerical search.

```
git clone https://github.com/hassard0/itb-engine
cd itb-engine
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest                              # all 302+ tests
itb serve                           # localhost web app
itb check --g4 0.5 --g6 0.4         # CLI feasibility check
```

---

## What the engine does, in one paragraph

Given a parameterized gravitational EFT (Wilson coefficients `g_4, g_6, g_8` for matter; `g_R², g_R³, g_R²_parity, g_R³_parity` for graviton sector), the engine asks whether a candidate theory satisfies every encoded consistency constraint. If yes, it computes how robust the theory is (fragility, signed-distance margins). If no, it reports which physical principle eliminates it. Across 24 constraints spanning amplitude bootstrap (Caron-Huot dispersion bounds, parity-decomposed positivity), information-theoretic (Bekenstein, BNOSSW MMI, holographic subadditivity), and gravitational universality (anomaly inflow, EFT validity, Susskind/Lloyd complexity bound), the engine produces ranked experimental priorities, framework comparisons, and intersection-search results that target where to look next for new physics.

---

## Architecture

```
itb-engine/
├── src/itb/
│   ├── theory.py                       Wilson-coefficient theory dataclass
│   ├── constraints/                    24 constraint modules (A/B/C classes)
│   ├── frameworks/                     4 candidate-framework encoders
│   ├── engine.py                       Constraint feasibility check
│   ├── mapper.py                       2D parameter sweeps
│   ├── voxel.py                        3D voxel sweeps
│   ├── adversarial.py                  Analytic-center search
│   ├── path_distance.py                Shortest path through allowed region
│   ├── completeness.py                 Allowed-region boundedness check
│   ├── fragility.py                    Distance-to-violation per cell
│   ├── importance.py                   Per-constraint redundancy ranking
│   ├── duality.py                      Cross-class IoU computation
│   ├── phase_components.py             Disconnected-component detection
│   ├── sensitivity.py                  Bayesian feasibility probability
│   ├── fisher.py                       Fisher metric on theory space
│   ├── observables.py                  Observable interface
│   ├── fingerprint.py                  Pairwise framework fingerprint
│   ├── first_disagreement.py           Per-pair best discriminating observable
│   ├── experiment_priority.py          Ranked experiment list
│   ├── intersection_search.py          scipy-driven all-constraint optimum
│   ├── battery.py                      Full-battery markdown report
│   ├── scenarios.py                    Pre-baked scenario variants
│   ├── report.py                       Multi-framework comparison
│   ├── plotting.py                     Plotly figure builders
│   ├── cli.py                          itb command
│   └── api/server.py                   FastAPI web app
├── frontend/                           Plain HTML + Plotly UI
├── tests/                              ~302 tests across all modules
└── docs/
    ├── superpowers/
    │   ├── specs/                      Original design specs (v0.1, v0.2)
    │   ├── plans/                      Implementation plans
    │   └── notes/                      Theoretical research log
    └── results/                        Computed research artifacts (per iteration)
```

---

## Constraints currently encoded (24)

### Class A — Amplitude bootstrap (12)

- `scalar_positivity_g4` — Adams-Arkani-Hamed-Dubovsky-Nicolis-Rattazzi 2006
- `scalar_positivity_g6` — same family, next order
- `scalar_positivity_g8` — Caron-Huot dispersion tower next-next order
- `scalar_convexity_g6_vs_g4` — `g_6 ≥ g_4²`, next-order forward dispersion
- `dispersion_tower_g6_squared_bound` — `g_6² ≤ g_4·g_8`, chained Cauchy-Schwarz
- `graviton_mixed_positivity` — Caron-Huot-Mazac-Rastelli-Simmons-Duffin 2021
- `cubic_curvature_positivity` — `g_R³ ≥ 0`
- `cubic_graviton_matter_bound` — `g_R³ ≤ κ·g_4²`
- `parity_violating_positivity` — `|g_R²|² + |g_R²_parity|² ≤ κ·g_4·g_6`
- `left_handed_graviton_positivity` — polarization-decomposed
- `right_handed_graviton_positivity` — polarization-decomposed
- `parity_violating_cubic_bound` — `|g_R³|² + |g_R³_parity|² ≤ κ·g_4²`
- `causality_bound` — Adams et al causality / de Rham-Tolley

### Class B — Information-theoretic (4)

- `bekenstein_tight` — `g_R²² ≤ ½·g_4·g_6`
- `holographic_subadditivity` — `g_4 + g_6 ≥ g_R²`
- `bnossw_monogamy` — `g_4·g_6/(g_4+g_6) ≥ g_R²`
- `ligo_birefringence_bound` — `|g_R²_parity| ≤ 0.1` (LIGO/Virgo O3)
- `ligo_graviton_mass_bound` — `g_R² ≤ 0.5` (LIGO O3 graviton dispersion)

### Class C — Gravitational universality (7)

- `eft_validity_box` — `|g_*| ≤ Λ` cutoff
- `anomaly_cancellation` — `g_4·g_6 - c·g_R²² = 0 ± tol`
- `weak_gravity_conjecture` — `g_R² ≤ α·√g_4`
- `generalized_anomaly_inflow` — `|g_R²_parity|² + 2·|g_R³_parity|² ≤ ρ·g_4·g_R²`
- `t_hooft_anomaly_matching` — cubic/leading parity ratio bounded
- `complexity_cutoff` — Susskind/Lloyd weighted-L² aggregate bound

---

## Candidate frameworks encoded (4)

| Framework | g_4 | g_6 | g_R² | g_8 | g_R³ | g_R²_parity | Status (v1.8) |
|---|---|---|---|---|---|---|---|
| Pure GR | 0 | 0 | 0 | 0 | 0 | 0 | Boundary point (origin) |
| String tree EFT | 0.50 | 0.40 | 0.20 | 0.40 | 0.15 | 0 | **Feasible** (fragility 0.02) |
| Asymptotic Safety | 0.40 | 0.30 | 0.15 | 0.30 | 0.10 | 0 | **Feasible** (fragility 0.02) |
| LQG-induced | 0.60 | 0.45 | 0.30 | 0.40 | 0.30 | 0.08 | **Fails 3 constraints** |

LQG-induced fails on `bnossw_monogamy` (class B), strict-anomaly variants (class C), and `complexity_cutoff` (class C) — exactly the constraints LQG philosophically rejects (holographic, computational).

---

## Headline result, honestly framed

After 18 iterations of building constraint structure, scipy-Nelder-Mead intersection search across the full 7-dimensional Wilson-coefficient space finds **a non-empty common solution to all 24 constraints simultaneously**:

```
g_4         ≈ 0.622   matter self-coupling
g_6         ≈ 0.395   next-order matter
g_8         ≈ 0.359   next-next-order
g_R²        ≈ 0.233   leading curvature coupling
g_R³        ≈ 0.151   cubic curvature
g_R²_parity ≈ 0       parity-conserving (driven to zero)
g_R³_parity ≈ 0       parity-conserving (driven to zero)
```

with worst-case constraint margin +0.0087. This is **not** any of the candidate frameworks — it's a new feasible point, parity-conserving, sitting between string-EFT and LQG-induced in coefficient space.

This is **toy** values across the board. The constraint forms are publication-grade-flavored simplifications; the exact prefactors are O(1) placeholders. The path to a real result goes through replacing each encoding with the literal published form.

See `docs/results/2026-05-08-v1.8-honest-synthesis.md` for the full reckoning.

---

## Research artifacts (chronological)

- `docs/results/2026-05-08-v0.8-baseline-report.md` — first end-to-end full-battery analysis
- `docs/results/2026-05-08-v1.0-publication-grade-report.md` — dispersion tower + WGC + LIGO active
- `docs/results/2026-05-08-v1.0-findings.md` — what publication-grade encoding changed
- `docs/results/2026-05-08-v1.1-bnossw-report.md` — LQG fails BNOSSW MMI
- `docs/results/2026-05-08-v1.2-cubic-curvature-report.md` — cubic curvature pinches frameworks
- `docs/results/2026-05-08-v1.3-experimental-priorities.md` — first ranked experiment list
- `docs/results/2026-05-08-v1.4-parity-violation-report.md` — parity sector activated
- `docs/results/2026-05-08-v1.4-experimental-priorities.md` — GW birefringence becomes top priority
- `docs/results/2026-05-08-v1.5-first-disagreement.md` — high-s scattering most discriminating
- `docs/results/2026-05-08-v1.6-anomaly-flow-report.md` — anomaly matching reorders binding diagnostic
- `docs/results/2026-05-08-v1.8-intersection-search.md` — engine optimum found
- `docs/results/2026-05-08-v1.8-honest-synthesis.md` — corrected synthesis after 18 iterations

Plus scenario reports under `docs/results/scenarios/`.

---

## Theoretical exploration logs

- `docs/superpowers/specs/2026-05-07-itb-engine-design.md` — initial design
- `docs/superpowers/notes/2026-05-07-ideas-from-mvp-build.md` — 7 research-direction ideas (v0.1 → v0.2)
- `docs/superpowers/notes/2026-05-07-theorizing-new-models.md` — 10 candidate QG model directions
- `docs/superpowers/notes/2026-05-08-v02-learnings-and-new-ideas.md` — 5 new ideas post-v0.2
- `docs/superpowers/notes/2026-05-08-v04-learnings-and-v05-direction.md` — 5 new ideas post-v0.4

---

## Honest limitations

1. **Toy values throughout.** Every constraint uses simplified forms with O(1) placeholder prefactors. Real Caron-Huot 2024 numerical bounds, real BNOSSW inequalities for n=3 regions, real LIGO O3/O4 sensitivities in proper units would all move the engine optimum.
2. **7-coefficient EFT.** Real gravitational EFT has dozens of operators. The architecture supports adding more; the encoding work is the limit.
3. **2D and 3D analyses.** Higher-dimensional sweeps are computationally tractable but not yet routine.
4. **MMI proxy form.** The harmonic-mean BNOSSW form is structurally correct but not the literal published inequalities.

The architecture is research-grade. The encoding effort to make the result research-grade is *weeks* of literature-aware work, not minutes.

---

## License

MIT. See `LICENSE`.
