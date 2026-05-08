# v0.2 Learnings + New Ideas

**Date:** 2026-05-08

## Surprises from v0.2

1. **The binding-class diagnostic is uniformly red** — and that's a feature, not a bug. It is telling us we have zero information-theoretic constraints in the engine. The visualization is teaching us where we're anemic. Good diagnostics should be uncomfortable.

2. **The toy physics is too linear to exercise the new machinery.** Fisher metric is constant; Newton tracer converges in one step; perturbation analysis is trivially correct. The architecture is over-engineered for the physics it currently encodes. The next moves should add curvature, not more linearity.

3. **Signed-distance margin ≈ Bayesian model evidence in the Gaussian limit.** This was unintended. The perturbation analysis is doing partial Bayesian inference, not just distance.

## New ideas (post-v0.2)

- **#A Adversarial bootstrap** — find the theory that maximally distinguishes the constraint set; the one whose existence would force one constraint to be wrong.
- **#B Constraint-importance ranking** — remove each constraint, measure allowed-region growth. Reveals which constraints carry the load.
- **#C Theory-path distance** — shortest path through allowed region between two theories. Disconnected components = different phases.
- **#D Fragility heatmap** — apply perturbation analysis across the whole sweep, color by distance-to-nearest-violation.
- **#E Completeness check** — is the allowed region bounded? If not, the constraint set is incomplete.
- **#F Per-constraint coloring** — v0.2 colors by class but multiple constraints in one class bind in different regions; need per-constraint resolution.
- **#G Curved class-A constraint** — `g_6 ≥ g_4²` is a real next-order forward-dispersion fact. First non-linear boundary, exercises Newton tracing.

## v0.3 commitment

Build #G + #F + #D + #B. Combined, they let the engine produce a physics-decomposed allowed region with quantified fragility and per-constraint blame.

Deferred to v0.4+: #A (adversarial), #C (path distance), #E (completeness).
