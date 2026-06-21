# ITB Engine Research Roadmap

This roadmap starts from the v2.203 state. It is a research plan, not a solved
quantum-gravity claim.

## Current State

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
  boundary.

The decisive current blocker is still unresolved:

```text
qnm_deformation_to_bresciani_engine_r4_map_missing
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
rows. That still does not make the pyRing branch columns Bresciani operator
axes. The route still lacks:

```text
pyring_quartic_direction_to_bresciani_axis_orientation_missing
pyring_plus_minus_branches_not_independent_operator_axes
pyring_runtime_to_parspec_high_spin_normalization_policy_missing
public_parspec_qeft_likelihood_or_posterior_samples_missing
claim_grade_systematics_export_missing
external_adversarial_review_missing
```

## Roadmap

1. Acquire a real qNM-to-Bresciani sensitivity source.
   The target is a source-backed relation from the ParSpec qNM deformation axes
   to `K_plus`, `Re(K_minus)`, `Im(K_minus)` or directly to
   `g_R4_c1/c2/c3`. Public fragments to continue from are Silva/Ghosh/Buonanno
   qEFT ParSpec, Cano et al. higher-derivative QNM shifts, Maenaut et al.
   rotating-EFT ringdown, pyRing EFT QNM coefficient tables, and the Bresciani
   spin-2 R4 amplitude basis.

2. Derive the pyRing-to-Bresciani orientation if it exists.
   The immediate route is to identify whether pyRing `quartic_1/2/3` and the
   plus/minus branch splitting can be mapped into the Bresciani
   `K_plus/Re(K_minus)/Im(K_minus)` basis with a closed normalization and
   field-redefinition policy. If not, the result should be a negative theorem
   or source-backed no-map ledger, not a synthetic map.

3. Resolve the pyRing runtime to ParSpec high-spin normalization policy.
   v2.203 shows that event-spin rows can be computed, but pyRing runtime EFT
   rows are normalized against Berti GR fits while the ParSpec high-spin
   polynomial gives slightly different frequency and damping-time normalizers.
   The next artifact should either choose a source-backed normalization policy
   or prove that the two normalizations cannot be mixed in a claim-grade map.

4. Acquire a machine-readable qEFT likelihood.
   A public posterior sample file, covariance matrix, or log-likelihood grid
   would be enough to replace the current published-bound surrogate. If the
   original ParSpec samples are unavailable, the fallback is a reproducible
   pyRing/LALSuite rerun that exports a likelihood packet with event metadata,
   priors, waveform versions, and calibration/systematics policy.

5. Attach claim-grade systematics.
   The current route has deterministic controls and coarse likelihood grids. A
   defensible discriminator needs waveform-family comparisons, calibration
   priors, detector topology, event-selection policy, EFT validity bounds, and
   covariance propagation through the qNM-to-engine map.

6. Run an adversarial review pass.
   Before any framework exclusion claim, an independent reviewer should be able
   to reproduce the source packet, verify the operator-basis orientation,
   inspect the likelihood export, and challenge the EFT validity domain.

7. Only then promote the discriminator.
   A claimable result requires: full-rank source-backed map, public likelihood
   or reproducible likelihood export, claim-grade systematics, remote Linux
   reproduction, and external adversarial review. Without all five, the route
   remains nonclaiming.

## Near-Term Next Artifact

The next best artifact is one of:

- `r4_parspec_pyring_to_bresciani_orientation.py`, if the pyRing quartic
  theory labels can be source-mapped to Bresciani coordinates;
- `r4_parspec_pyring_runtime_to_parspec_normalization_policy.py`, if the
  v2.203 runtime-vs-ParSpec normalizer gap can be closed or formally isolated;
- `r4_parspec_public_likelihood_packet.py`, if public or reproducible qEFT
  samples/log-likelihood data can be obtained;
- `r4_parspec_qnm_to_bresciani_sensitivity.py`, if a source-backed 3x4
  sensitivity relation can be derived or imported;
- `r4_parspec_pyring_likelihood_rerun_packet.py`, if pyRing becomes the most
  practical bridge toward a reproducible likelihood rerun.

Each artifact should include a JSON result, focused tests, a result note, and a
claim gate that remains closed unless the packet is source-backed and complete.
