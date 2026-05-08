# Scenario: baseline

_All known constraints, all known frameworks, default tolerances, g_R2 fixed at 0.3._

# ITB Engine — Full Battery: baseline

_Generated: 2026-05-08T04:18:01+00:00_

- Constraints: 8
- Frameworks: 4
- Sweep: (g_4 ∈ (-1.0, 2.0), 21 steps) × (g_6 ∈ (-1.0, 2.0), 21 steps)
- Fixed coefficients: {'g_R2': 0.3}

## Constraints in scope

| name | class |
|---|---|
| scalar_positivity_g4 | amplitude_bootstrap |
| scalar_positivity_g6 | amplitude_bootstrap |
| scalar_convexity_g6_vs_g4 | amplitude_bootstrap |
| graviton_mixed_positivity | amplitude_bootstrap |
| bekenstein_tight | information_theoretic |
| eft_validity_box | gravitational_universality |
| causality_bound | amplitude_bootstrap |
| anomaly_cancellation | gravitational_universality |

## Per-framework status

| framework | feasible | n_binding | fragility distance | nearest binding |
|---|---|---|---|---|
| pure_gr | True | 6 | 0.0000 | scalar_positivity_g4 |
| string_tree_eft | True | 0 | 0.0530 | anomaly_cancellation |
| asymptotic_safety | True | 0 | 0.0960 | bekenstein_tight |
| lqg_induced | True | 0 | 0.0208 | anomaly_cancellation |

## Coefficients

| framework | g_4 | g_6 | g_R2 |
|---|---|---|---|
| pure_gr | 0.000 | 0.000 | 0.000 |
| string_tree_eft | 0.500 | 0.400 | 0.200 |
| asymptotic_safety | 0.400 | 0.300 | 0.150 |
| lqg_induced | 0.600 | 0.450 | 0.300 |

## Pairwise framework distance (fingerprint)

| framework | pure_gr | string_tree_eft | asymptotic_safety | lqg_induced |
|---|---|---|---|---|
| pure_gr | 0.000 | 0.671 | 0.522 | 0.808 |
| string_tree_eft | 0.671 | 0.000 | 0.150 | 0.150 |
| asymptotic_safety | 0.522 | 0.150 | 0.000 | 0.292 |
| lqg_induced | 0.808 | 0.150 | 0.292 | 0.000 |

## 2D sweep summary

- Allowed cells: 3 / 441 (0.7 %)
- Phase components: 2 (sizes [2, 1])

## Constraint importance ranking

- Baseline allowed: 3 / 441

| constraint | growth (cells) | growth fraction |
|---|---|---|
| anomaly_cancellation | 57 | 19.000 |
| scalar_convexity_g6_vs_g4 | 6 | 2.000 |
| causality_bound | 4 | 1.333 |
| bekenstein_tight | 3 | 1.000 |
| scalar_positivity_g4 | 0 | 0.000 |
| scalar_positivity_g6 | 0 | 0.000 |
| graviton_mixed_positivity | 0 | 0.000 |
| eft_validity_box | 0 | 0.000 |

## Cross-class duality (A vs B)

- IoU(A, B): 0.3191
- A only: 3 cells
- B only: 125 cells
- Both: 60 cells

## Boundedness

- Bounded: True
- Final box size tested: 4.0

## Adversarial bootstrap (analytic center)

- Adversarial point: {'g_4': 0.6616378181651229, 'g_6': 0.4377646024158468, 'g_R2': 0.38055329220371864}
- Simultaneously binding constraints: 2
  - scalar_convexity_g6_vs_g4, bekenstein_tight
- Objective value: 2.523642e+00

---

_End of full-battery report._