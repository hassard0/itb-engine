# Scenario: info-only

_Only information-theoretic (class B) constraints active._

# ITB Engine — Full Battery: info-only

_Generated: 2026-05-08T04:18:01+00:00_

- Constraints: 1
- Frameworks: 4
- Sweep: (g_4 ∈ (-1.0, 2.0), 21 steps) × (g_6 ∈ (-1.0, 2.0), 21 steps)
- Fixed coefficients: {'g_R2': 0.3}

## Constraints in scope

| name | class |
|---|---|
| bekenstein_tight | information_theoretic |

## Per-framework status

| framework | feasible | n_binding | fragility distance | nearest binding |
|---|---|---|---|---|
| pure_gr | True | 1 | 0.0000 | bekenstein_tight |
| string_tree_eft | True | 0 | 0.1171 | bekenstein_tight |
| asymptotic_safety | True | 0 | 0.0960 | bekenstein_tight |
| lqg_induced | True | 0 | 0.0636 | bekenstein_tight |

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

- Allowed cells: 185 / 441 (42.0 %)
- Phase components: 2 (sizes [28, 157])

## Constraint importance ranking

- Baseline allowed: 185 / 441

| constraint | growth (cells) | growth fraction |
|---|---|---|
| bekenstein_tight | 256 | 1.384 |

## Cross-class duality (A vs B)

_skipped: requires at least one constraint in each of class A and class B_

## Boundedness

- Bounded: False
- Final box size tested: 8.0
- Unbounded directions: ['g_4', 'g_6']

## Adversarial bootstrap (analytic center)

- Adversarial point: {'g_4': 0.4827317506681016, 'g_6': 0.4827317506681016, 'g_R2': 0.34134262707959545}
- Simultaneously binding constraints: 1
  - bekenstein_tight
- Objective value: 3.330258e-14

---

_End of full-battery report._