# ITB Engine — Information-Theoretic Bootstrap for Quantum Gravity

Constrain the space of possible quantum-gravity theories by imposing every consistency condition we can encode —
amplitude positivity, causality, holography, the swampland, anomalies, black-hole thermodynamics — then confront
the survivors with real experimental data and see what's left.

> **Status:** v2.471 · full suite green · **[FINDINGS.md](docs/FINDINGS.md)** = curated results ·
> **[Research Report II](docs/results/2026-07-02-v2.428-RESEARCH-REPORT-II.md)** = publication-style synthesis ·
> 42 rigor-tagged constraints · 14 framework encoders · ~582 result notes.

---

## The result, in one paragraph

Intersecting every consistency condition over the space of Wilson coefficients leaves a **single, tiny, connected
region** — one candidate low-energy quantum-gravity EFT, not a landscape. It is **matter-dominant, near-Planckian,
ghost-safe, and string-like**, with its gravitational sector *forced into existence and capped in size* by its
matter sector. Its leading (but not unique) UV completion is a **heterotic string + its model-independent axion**;
its late universe is a **two-field cosmology** (an R² scalaron driving inflation — and *bounding* a separate
quintessence dark energy, not being it — plus a parity-odd axion driving cosmic birefringence). The near-uniqueness is a **consilience** — the candidate is the one point
where seven independent areas of theoretical physics *and* six measurements agree — and it is sharply falsifiable
(see [FINDINGS.md](docs/FINDINGS.md) for the full picture and the honest tiering of every claim).

**Sharpest, most scale-clean predictions** (dimensionless — no string scale, no toy coefficient):
- **Cosmic birefringence β ~ α_EM** — the heterotic axion's EM anomaly coupling gives β ~ 0.03–0.3°,
  matching the measured 0.34° in order of magnitude.
- **Inflation line r = 3(1−n_s)²** — pins r ≈ 0.0037 from the measured n_s (LiteBIRD-testable).
- **Dark-energy thawing line wa ≈ −1.5(1+w0), w ≥ −1** — the *most vulnerable* front, in mild tension with DESI's
  steep-wa / phantom-past hint.

---

## What it is

The engine represents a higher-derivative gravitational EFT by a vector of **dimensionless Wilson coefficients**:

| sector | coefficients | meaning |
|---|---|---|
| matter | `g_4, g_6, g_8, g_10` | forward-limit scattering positivity moments |
| curvature | `g_R2` (R²), `g_C` (Weyl²), `g_R3` (R³), `g_R4` (R⁴) | curvature couplings |
| parity | `g_R2_parity, g_R3_parity` | gravitational Chern–Simons / Pontryagin |
| vacuum | `g_Lambda` | cosmological constant (opt-in) |

It then asks three questions in order:

1. **Which theories are consistent?** Intersect the 42 rigor-tagged constraints (positivity, causality, holography,
   swampland, anomalies, BH thermodynamics). The survivors form a thin region in coefficient space.
2. **What do they predict?** Each survivor is a point with a falsifiable observable fingerprint (cosmic
   birefringence, inflation n_s/r, dark-energy w, sub-mm gravity, GW signals, BH entropy…).
3. **What does the data say?** Fold in real measurements (cosmic birefringence, sub-mm gravity, GW speed &
   dispersion) as extra constraints and watch the region shrink — sometimes to a tension.

**Rigor tiering is first-class.** Every constraint is tagged `rigorous` (source-exact positivity / causality /
bootstrap, zero toy input — 19), `sourced_proxy` (a real conjecture or theorem via an O(1) proxy form — 17), or
`data` (a real measurement via an observable map — 6). The candidate's entire *matter-gravity content is rigorous*;
the honest caveats and what survives the O(1)-prefactor uncertainty are laid out in FINDINGS and Report II.

---

## Navigation

- **[docs/FINDINGS.md](docs/FINDINGS.md)** — the curated, current summary of what the engine found (start here).
- **[Research Report II](docs/results/2026-07-02-v2.428-RESEARCH-REPORT-II.md)** — publication-style synthesis:
  method, candidate, rigor tiering, UV completion, cosmology, consilience, falsifiability, limits.
- **[docs/ROADMAP.md](docs/ROADMAP.md)** — where the program is and the remaining (external) levers.
- **[docs/CONSTRAINTS.md](docs/CONSTRAINTS.md)** — the full constraint stack, by class.
- **[docs/results/INDEX.md](docs/results/INDEX.md)** — every research cycle, chronologically (the per-cycle log).

---

## Quickstart

```bash
git clone https://github.com/hassard0/itb-engine && cd itb-engine
python -m venv .venv && . .venv/bin/activate      # (Windows: .venv\Scripts\activate)
pip install -e ".[dev]"
pytest -q

# render a framework's observable fingerprint
itb predict string_tree_eft --json

# flagship experiments (each prints a summary; writes a figure + JSON)
python experiments/island_census.py 300000        # how rare / low-dimensional is the feasible region
python experiments/min_experiment_set.py           # the minimum experiment set that pins the theory
```

Heavy Monte-Carlo runs parallelize across cores and are intended for a multi-core workstation. Remote-validation
access is configured outside committed docs — use your own SSH/env wrapper; don't commit private details.

---

## How it works

- **The constraint stack** (`experiments/stack.py`) — `build_stack(...)` assembles the 42 constraints; real data is
  opt-in (`include_data`, `include_birefringence`, `include_gw_speed`, `include_gw_dispersion`) so the
  theoretical-only stack is preserved. Each constraint exposes `.evaluate(theory) → (satisfied, margin, …)`,
  `.gradient(...)`, a `.constraint_class`, and a rigor tag.
- **Observables & predictions** (`src/itb/predict.py`, `src/itb/gravitational_observables.py`) — each framework
  has a falsifiable fingerprint (birefringence, η/s, Starobinsky n_s/r, BH extremal-entropy shift, …); the
  Jacobians power the Fisher / experimental-design analyses.
- **Frameworks** (`src/itb/frameworks/`) — 14 encoders: string tree-EFT, asymptotic safety, CDT, causal sets, LQG,
  group field theory, Hořava–Lifshitz, emergent gravity, Penrose–Diósi, pure GR, plus the engine-discovered ones.

---

## Honest framing

The engine is built to surface its own limits, not hide them. Most constraint prefactors and cross-sector
observable maps are **O(1) / order-of-magnitude** — so the robust content is **signs, orderings, structure, and
which experiment constrains what**, not precise coordinates. A dedicated *realism program* re-checks every headline
against that factor-of-~2 uncertainty and separates robust conclusions from artifacts; the rigor tags mark what
needs zero toy input at all. Several results are deliberately *negative* or *self-correcting*. Read every claim
with the tiering in FINDINGS / Report II in mind — e.g. cosmic birefringence is still a ~3.6σ hint, and the
inflation / dark-energy relations are plateau-*class* (they validate the class, not uniquely this candidate).

---

## Architecture

```
itb-engine/
├── src/itb/
│   ├── theory.py              Wilson-coefficient dataclass
│   ├── constraints/           theoretical constraints + opt-in data constraints
│   ├── frameworks/            14 framework encoders
│   ├── predict.py             `itb predict` fingerprint;  fisher.py  Fisher metric
│   ├── gravitational_observables.py, observables.py, holographic_ac.py
│   └── cli.py, api/server.py  `itb` command + FastAPI app
├── experiments/               cycle scripts + stack.py (the constraint assembler)
├── docs/
│   ├── FINDINGS.md            ← curated findings (read this)
│   ├── ROADMAP.md, CONSTRAINTS.md
│   └── results/               ~566 indexed result notes + INDEX.md
├── tests/                     full suite (run `pytest -q`)
└── tools/                     reproduction + validation helpers, build_index.py
```

## License

See [LICENSE](LICENSE).
