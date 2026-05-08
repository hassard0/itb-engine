# Scenario: amplitude-only

_Only amplitude-bootstrap (class A) constraints active._

# ITB Engine — Full Battery: amplitude-only

_Generated: 2026-05-08T04:18:01+00:00_

- Constraints: 5
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
| causality_bound | amplitude_bootstrap |

## Per-framework status

| framework | feasible | n_binding | fragility distance | nearest binding |
|---|---|---|---|---|
| pure_gr | True | 5 | 0.0000 | scalar_positivity_g4 |
| string_tree_eft | True | 0 | 0.1061 | scalar_convexity_g6_vs_g4 |
| asymptotic_safety | True | 0 | 0.1093 | scalar_convexity_g6_vs_g4 |
| lqg_induced | True | 0 | 0.0576 | scalar_convexity_g6_vs_g4 |

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

- Allowed cells: 63 / 441 (14.3 %)
- Phase components: 1 (sizes [63])

## Constraint importance ranking

- Baseline allowed: 63 / 441

| constraint | growth (cells) | growth fraction |
|---|---|---|
| scalar_convexity_g6_vs_g4 | 94 | 1.492 |
| causality_bound | 13 | 0.206 |
| graviton_mixed_positivity | 1 | 0.016 |
| scalar_positivity_g4 | 0 | 0.000 |
| scalar_positivity_g6 | 0 | 0.000 |

## Cross-class duality (A vs B)

_skipped: requires at least one constraint in each of class A and class B_

## Boundedness

- Bounded: False
- Final box size tested: 8.0
- Unbounded directions: ['g_6']

## Adversarial bootstrap (analytic center)

- Adversarial point: {'g_4': -2.7755575615628914e-17, 'g_6': 2.383082243163712e-16, 'g_R2': 5.551115123125783e-17}
- Simultaneously binding constraints: 5
  - scalar_positivity_g4, scalar_positivity_g6, scalar_convexity_g6_vs_g4, graviton_mixed_positivity, causality_bound
- Objective value: 1.212853e-31

---

_End of full-battery report._