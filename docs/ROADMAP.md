# ITB Engine Research Roadmap

This roadmap starts from the v2.200 state. It is a research plan, not a solved
quantum-gravity claim.

## Current State

The strongest live-data route is the R4/GWOSC/ParSpec path. The repo can now:

- load public GWOSC strain and build nonclaiming R4 likelihood scaffolds;
- align the ParSpec qEFT source events with public GWOSC event versions;
- attach published qEFT bounds as nonclaiming surrogates;
- compute source-event absolute ParSpec gamma from final-mass/redshift metadata;
- define an executable acceptance gate for the missing qNM-to-Bresciani map.

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

## Roadmap

1. Acquire a real qNM-to-Bresciani sensitivity source.
   The target is a source-backed relation from the ParSpec qNM deformation axes
   to `K_plus`, `Re(K_minus)`, `Im(K_minus)` or directly to
   `g_R4_c1/c2/c3`. Public fragments to continue from are Silva/Ghosh/Buonanno
   qEFT ParSpec, Cano et al. higher-derivative QNM shifts, Maenaut et al.
   rotating-EFT ringdown, pyRing EFT QNM coefficient tables, and the Bresciani
   spin-2 R4 amplitude basis.

2. Acquire a machine-readable qEFT likelihood.
   A public posterior sample file, covariance matrix, or log-likelihood grid
   would be enough to replace the current published-bound surrogate. If the
   original ParSpec samples are unavailable, the fallback is a reproducible
   pyRing/LALSuite rerun that exports a likelihood packet with event metadata,
   priors, waveform versions, and calibration/systematics policy.

3. Attach claim-grade systematics.
   The current route has deterministic controls and coarse likelihood grids. A
   defensible discriminator needs waveform-family comparisons, calibration
   priors, detector topology, event-selection policy, EFT validity bounds, and
   covariance propagation through the qNM-to-engine map.

4. Run an adversarial review pass.
   Before any framework exclusion claim, an independent reviewer should be able
   to reproduce the source packet, verify the operator-basis orientation,
   inspect the likelihood export, and challenge the EFT validity domain.

5. Only then promote the discriminator.
   A claimable result requires: full-rank source-backed map, public likelihood
   or reproducible likelihood export, claim-grade systematics, remote Linux
   reproduction, and external adversarial review. Without all five, the route
   remains nonclaiming.

## Near-Term Next Artifact

The next best artifact is one of:

- `r4_parspec_public_likelihood_packet.py`, if public or reproducible qEFT
  samples/log-likelihood data can be obtained;
- `r4_parspec_qnm_to_bresciani_sensitivity.py`, if a source-backed 3x4
  sensitivity relation can be derived or imported;
- `r4_parspec_pyring_source_probe.py`, if pyRing coefficient tables are the
  most practical bridge toward a reproducible likelihood rerun.

Each artifact should include a JSON result, focused tests, a result note, and a
claim gate that remains closed unless the packet is source-backed and complete.
