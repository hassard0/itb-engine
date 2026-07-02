# ITB Engine Research Roadmap

A research plan, not a solved quantum-gravity claim. The program has run through several phases: the
**foundational phase** (island census -> data confrontation -> R4/GWOSC live-data frontier, up to ~v2.208); the
**swing / candidate phase** (v2.367-v2.407), which constructed and exhaustively stress-tested a single candidate
low-energy QG EFT; the **de-toying arc** (v2.411-419), which made the toy-vs-rigorous distinction first-class and
showed the candidate's matter-gravity content is source-exact; and the **cosmological-constant sector**
(v2.422-425), a new opt-in dark-energy sector. See [FINDINGS.md](FINDINGS.md) for what was found.

## Current frontier (v2.425)

The candidate theory is **complete** and its status is precisely tiered ([v2.415 rigor ledger](results/2026-07-01-v2.415-qnm-rigor-ledger.md)):
a matter-dominant, near-Planckian, ghost-safe, string-like, globally-unique consistent EFT whose **matter-gravity
content is rigorous** (source-exact amplitude positivity / causality: LQG excluded, matter dominance's ceiling
and BH decay implied, the leading curvature coupling forced by matter x cubic-curvature -- de-toying arc
v2.411-419), with the toy-dependence chased down to a single parity-magnitude coefficient (itself rigorously
capped + data-pinned, [v2.418]). Rigor determines a **family**; data (cosmic birefringence) selects the
**point** ([v2.419]). The candidate is falsifiable on **three independent observable fronts** -- parity
(CMB + GW birefringence), matter (CMB-S4 inflation), and dark energy (DESI/Euclid w(z)) -- atop a rigorous
backbone ([v2.421 falsification portfolio](results/2026-07-01-v2.421-qnm-falsification-portfolio.md)). The new
CC sector adds a coherent dark-energy story ([v2.425 capstone](results/2026-07-01-v2.425-qnm-cc-capstone.md)):
the candidate admits dark energy (capped at g_R2), selects de Sitter over anti-de Sitter, and predicts w >~ -1.

Both the candidate program and the CC sector are now **comprehensively developed**. The genuine next major
thrusts (in rough order of value vs tractability):

1. **New sectors** (the productive vein, like the CC sector). Candidates: a matter-content / spin-decomposed
   sector, a neutrino/flavour sector, or the conformal-anomaly-induced vacuum energy (a *rigorous* CC ingredient
   ~ the Euler charge a = g_R2 -- flagged but deferred, needs careful encoding to avoid a mis-attribution).
2. **More rigorous constraints.** Add source-exact EFThedron / higher-positivity bounds the engine lacks, moving
   more of the stack into the rigorous tier (extends the de-toying program).
3. **Real normalization / live data.** Every magnitude is O(1)-toy; a physical prefactor calibration would turn
   the robust *structure* into quantitative predictions. The R4/GWOSC live-data route (parked below) remains
   blocked on the missing source-backed qNM->R4 map ([v2.209]).
4. **Observation** (not ours to run): CMB-S4 (~2030, matter + parity), DESI/Euclid (w(z), now), next-gen
   GW-birefringence (parity chirality).
5. **Write-up.** The candidate + rigor tiering + CC sector are at a natural point for a publication-style
   synthesis (the [v2.0 research report](results/2026-06-09-v2.0-RESEARCH-REPORT.md) predates all of the above).

## Parked route: R4/GWOSC live-data (foundational phase, from v2.208)

The strongest live-data route is the R4/GWOSC/ParSpec path. The repo can now:

- load public GWOSC strain and build nonclaiming R4 likelihood scaffolds;
- align the ParSpec qEFT source events with public GWOSC event versions;
- attach published qEFT bounds as nonclaiming surrogates;
- compute source-event absolute ParSpec gamma from final-mass/redshift metadata;
- define an executable acceptance gate for the missing qNM-to-Bresciani map;
- hash-pin and parse the public pyRing quartic EFT QNM coefficient tables;
- convert pyRing imaginary-frequency coefficients into linearized fractional
  damping-time axes for the checked spin-zero table slice;
- evaluate pyRing quartic EFT frequency and damping-time rows at the source
  event remnant spins while preserving the runtime-vs-ParSpec normalization
  boundary;
- formally isolate the pyRing runtime-to-ParSpec high-spin normalizer gap so
  runtime Berti-GR rows are allowed for internal pyRing reruns while ParSpec
  high-spin rows remain comparison-only;
- complete the pyRing-to-Bresciani orientation audit as a no-map ledger that
  forbids synthetic branch-to-operator projections;
- specify a reproducible pyRing EFT likelihood-rerun packet with public input
  pins, the paper-named pyRing execution commit, a 12-row event/direction config
  grid, runtime-coordinate policy, and an output contract for posterior samples
  or a log-likelihood grid.

The decisive current blocker is still unresolved as a *map*, but v2.209 now determines
its sourceable rank from the primary literature (fetched 2026-06-29): a source-backed
**rank-3** qNM-to-Bresciani map does NOT exist. The Bresciani operator basis
(arXiv:2504.12855) is rank 3 but carries no QNM apparatus; the only public ringdown
analysis (arXiv:2411.17893) is **rank 1 per parity-even theory** and **explicitly defers
the parity-violating sector**, so the engine's third axis `g_R4_c3 = Im(c_minus)` (the
parity-odd `Q2.Q2tilde` operator) is a **dark axis** — unconstrained by current ringdown
observables. The defensible R4 ringdown product is therefore at most a parity-even,
rank-1-per-theory nonclaiming null test; a full-rank discriminator needs a
polarization/rotation-resolved source for the parity-odd operator that does not yet exist
in public form.

```text
qnm_deformation_to_bresciani_engine_r4_map_missing       (full rank unsourceable)
parity_odd_axis_g_R4_c3_dark_to_current_ringdown         (v2.209)
```

v2.200 makes that blocker concrete. The next source-backed packet must provide a
finite 3x4 sensitivity matrix:

```text
rows = g_R4_c1, g_R4_c2, g_R4_c3
columns = delta_omega_qeft_0, delta_tau_qeft_0, delta_omega_qeft_1, delta_tau_qeft_1
required row rank = 3
```

The current qEFT source object is only a rank-1 gamma-to-qNM ray, so it cannot
be inverted into the three Bresciani engine axes.

v2.201 shows that public pyRing is useful but not sufficient by itself. It
provides three quartic EFT theory labels with plus/minus QNM mode-splitting
branches, not independent Bresciani operator axes. The checked table slice has
full rank in local branch-column QNM coordinates.

v2.202 resolves the narrow imaginary-frequency-to-damping-time conversion by
deriving the source-backed pyRing `tau_EFT` linearization and exporting a rank-2
spin-zero tau-axis matrix for `(2,2,0)` and `(2,2,1)`.

v2.203 evaluates those pyRing frequency and damping-time rows at the source
event remnant spins for GW150914 and GW200129. It also exposes that pyRing's
runtime `QNM_EFT` normalization uses Berti GR fits, while the ParSpec high-spin
polynomial normalization differs by up to a few percent across the checked
rows.

v2.204 resolves that normalization-policy ambiguity by selecting pyRing runtime
Berti-GR normalization for internal pyRing reruns and making ParSpec high-spin
rows comparison-only.

v2.205 audits the pyRing-to-Bresciani orientation route and records that the
current public pyRing tables do not supply a source-backed map from
`quartic_1/2/3` plus/minus branch-splitting directions to
`K_plus/Re(K_minus)/Im(K_minus)` or `g_R4_c1/c2/c3`. Synthetic branch-to-operator
maps are forbidden. The route still lacks:

```text
pyring_plus_minus_branches_not_independent_operator_axes
public_parspec_qeft_likelihood_or_posterior_samples_missing
claim_grade_systematics_export_missing
external_adversarial_review_missing
```

v2.206 documents the public ParSpec/qEFT likelihood acceptance gate and rechecks
public source surfaces. The available source package still provides TeX and
figure PDFs, not a machine-readable `ell_qEFT_km` posterior sample file,
covariance matrix, or log-likelihood grid. The published-bound surrogate remains
available only as nonclaiming continuity evidence.

v2.207 records the public-source route graph for the missing qNM-to-Bresciani
bridge. It confirms that public sources provide ParSpec qNM axes, a rank-1 qEFT
ray, pyRing/Cano quartic QNM branch coefficients, and Bresciani K-to-engine
projection, but no source-backed field-redefinition/operator edge from qNM
deformation coordinates to Bresciani K coordinates. The best executable next
route is a pyRing EFT likelihood-rerun packet in runtime coordinates, with the
Bresciani map gate still closed.

v2.208 makes that rerun packet concrete. It pins the public pyRing `EFT_QNMs`
branch probe, the fixed pyRing commit named by the public EFT ringdown analysis,
public GWOSC event and strain handles for GW150914 and GW200129, source-event
remnant spins, the pyRing runtime coordinate scope, paper-faithful priors and
runtime settings where available, and the exact output contract needed for a
reproducible likelihood export. It does not execute the sampler, export
posterior samples, export a log-likelihood grid, close systematics, or provide
the qNM-to-Bresciani operator map.

## Roadmap

1. Acquire a real qNM-to-Bresciani sensitivity source.
   The target is a source-backed relation from the ParSpec qNM deformation axes
   to `K_plus`, `Re(K_minus)`, `Im(K_minus)` or directly to
   `g_R4_c1/c2/c3`. Public fragments to continue from are Silva/Ghosh/Buonanno
   qEFT ParSpec, Cano et al. higher-derivative QNM shifts, Maenaut et al.
   rotating-EFT ringdown, pyRing EFT QNM coefficient tables, and the Bresciani
   spin-2 R4 amplitude basis.

2. Search for a different source-backed sensitivity route.
   v2.205 closes the current pyRing-orientation attempt as a no-map ledger, so
   the next route should use another source that directly relates QNM
   deformation axes to `K_plus/Re(K_minus)/Im(K_minus)` or to
   `g_R4_c1/c2/c3`. If no source supplies that, preserve the negative result
   rather than manufacturing a projection.

   **In-house alternative (opened by v2.210).** The engine now has a validated
   from-scratch QNM solver (3rd-order WKB, `experiments/qnm_wkb_solver.py`,
   omega_220/omega_221 reproduced to ~0.2%) with an operator->QNM sensitivity
   function. This lets the engine *derive* the operator->QNM map instead of
   importing one: build the **physical** higher-derivative (quartic-curvature)
   modification of the Regge-Wheeler/Bardeen-Press potential, feed its `delta_V`
   to `qnm_potential_sensitivity`, and read off `d(omega_R, omega_I)/d(coupling)`.
   The parity-even sector is computable this way; the parity-odd axis (`g_R4_c3`)
   stays dark to non-polarization-resolved ringdown (v2.209). This route still
   requires a *source-backed* modified potential (not a manufactured `delta_V`)
   before any claim, but it removes the dependence on a published sensitivity
   matrix.

3. Execute the reproducible pyRing EFT likelihood-rerun packet.
   v2.208 defines the packet shape. The practical next build is an executable
   config exporter that writes pyRing runtime configs for the 12 event/direction
   rows, hashes those configs, locks the environment, runs the sampler, and
   exports either posterior samples or a log-likelihood grid with diagnostics.
   The export must preserve whether each row is paper-reported `quartic_1/2` or
   a `quartic_3` branch-extension control.

4. Attach claim-grade systematics.
   The current route has deterministic controls and coarse likelihood grids. A
   defensible discriminator needs waveform-family comparisons, calibration
   priors, detector topology, event-selection policy, EFT validity bounds, and
   covariance propagation through the qNM-to-engine map.

5. Run an adversarial review pass.
   Before any framework exclusion claim, an independent reviewer should be able
   to reproduce the source packet, verify the operator-basis orientation,
   inspect the likelihood export, and challenge the EFT validity domain.

6. Only then promote the discriminator.
   A claimable result requires: full-rank source-backed map, public likelihood
   or reproducible likelihood export, claim-grade systematics, remote Linux
   reproduction, and external adversarial review. Without all five, the route
   remains nonclaiming.

## Near-Term Next Artifact

The next best artifact is one of:

- `r4_parspec_pyring_runtime_config_exporter.py`, to materialize and hash the
  v2.208 pyRing runtime rerun configs before sampler execution;
- `r4_parspec_pyring_runtime_likelihood_export.py`, after the sampler can
  produce posterior samples or a log-likelihood grid in runtime coordinates;
- `r4_parspec_qnm_to_bresciani_sensitivity.py`, if a source-backed 3x4
  sensitivity relation can be derived or imported;
- `r4_parspec_qeft_likelihood_rerun_packet.py`, if a source-backed ParSpec/qEFT
  sampler rerun becomes more practical than the pyRing route.

Each artifact should include a JSON result, focused tests, a result note, and a
claim gate that remains closed unless the packet is source-backed and complete.
