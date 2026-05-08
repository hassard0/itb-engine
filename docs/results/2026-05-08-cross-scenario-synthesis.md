# Cross-scenario synthesis

Per-framework feasibility across all scenarios.

| scenario | framework | feasible | fragility | binding |
|---|---|---|---|---|
| baseline | pure_gr | True | 0.0000 | — |
| baseline | string_tree_eft | True | 0.0530 | — |
| baseline | asymptotic_safety | True | 0.0960 | — |
| baseline | lqg_induced | True | 0.0208 | — |
| amplitude-only | pure_gr | True | 0.0000 | — |
| amplitude-only | string_tree_eft | True | 0.1061 | — |
| amplitude-only | asymptotic_safety | True | 0.1093 | — |
| amplitude-only | lqg_induced | True | 0.0576 | — |
| info-only | pure_gr | True | 0.0000 | — |
| info-only | string_tree_eft | True | 0.1171 | — |
| info-only | asymptotic_safety | True | 0.0960 | — |
| info-only | lqg_induced | True | 0.0636 | — |
| strict-anomaly | pure_gr | True | 0.0000 | — |
| strict-anomaly | string_tree_eft | False | 0.0000 | anomaly_cancellation |
| strict-anomaly | asymptotic_safety | True | 0.0043 | — |
| strict-anomaly | lqg_induced | False | 0.0000 | anomaly_cancellation |
| loose-eft | pure_gr | True | 0.0000 | — |
| loose-eft | string_tree_eft | True | 0.0530 | — |
| loose-eft | asymptotic_safety | True | 0.0960 | — |
| loose-eft | lqg_induced | True | 0.0208 | — |

## Survival rates

| framework | survived / total | rate |
|---|---|---|
| asymptotic_safety | 5 / 5 | 100% |
| lqg_induced | 4 / 5 | 80% |
| pure_gr | 5 / 5 | 100% |
| string_tree_eft | 4 / 5 | 80% |

## Mean fragility per framework

| framework | mean fragility | min fragility | max fragility |
|---|---|---|---|
| asymptotic_safety | 0.0803 | 0.0043 | 0.1093 |
| lqg_induced | 0.0326 | 0.0000 | 0.0636 |
| pure_gr | 0.0000 | 0.0000 | 0.0000 |
| string_tree_eft | 0.0658 | 0.0000 | 0.1171 |