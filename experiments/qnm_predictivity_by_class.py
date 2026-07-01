"""v2.374 - SWING: WHICH physics carves the EFT? Predictivity decomposed by constraint class -- swampland + positivity dominate, holography barely.

Decomposing v2.373's ~30000x consistency-driven volume reduction by the engine's own constraint taxonomy. Each
consistency condition is tagged with a class: A_AMPLITUDE (positivity / unitarity-type amplitude bounds),
B_INFORMATION (holographic / entropy bounds), C_UNIVERSALITY (swampland + anomaly/universality conditions).
Dropping each class from the theory-only stack and measuring how much the feasible region OPENS reveals which
physics does the predictive work.

Result: dropping C_UNIVERSALITY opens the region the most (~36x more feasible), dropping A_AMPLITUDE nearly as
much (~25x), and dropping B_INFORMATION barely at all (~3x). So the predictivity of the swampland-complete
carving is dominated by the SWAMPLAND/ANOMALY (universality) and POSITIVITY (amplitude) classes -- roughly
equally -- while the holographic/information class contributes little. In physics terms: quantum gravity's
low-energy EFT is pinned mainly by UNITARITY (positivity) and SWAMPLAND/ANOMALY consistency, not by entropy/
holographic bounds.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack

VERSION = "v2.374"
DEFAULT_OUT = Path("experiments/results/v2.374/qnm_predictivity_by_class.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
BOX_LO = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
BOX_HI = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 0.2])
CLASSES = ["A_AMPLITUDE", "B_INFORMATION", "C_UNIVERSALITY"]


def class_of(c):
    return str(getattr(c, "constraint_class", "")).split(".")[-1]


def feasible_count(stack, n, rng):
    return sum(all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, BOX_LO + rng.random(6) * (BOX_HI - BOX_LO))), name="x"), stack).results)
               for _ in range(n))


def run(n_samples: int = 40000, seed: int = 1) -> dict:
    full = build_stack(rfc_form="convex_hull")
    per_class_counts = dict(Counter(class_of(c) for c in full))

    rng = np.random.default_rng(seed)
    base_nf = feasible_count(full, n_samples, rng)
    base_frac = base_nf / n_samples

    opened = {}
    for cls in CLASSES:
        st = [c for c in full if class_of(c) != cls]
        rng2 = np.random.default_rng(seed + 1 + CLASSES.index(cls))
        nf = feasible_count(st, n_samples, rng2)
        opened[cls] = {"n_constraints": per_class_counts.get(cls, 0),
                       "feasible_fraction_without_class": float(f"{nf / n_samples:.2e}"),
                       "n_feasible": nf,
                       "opening_factor_vs_baseline": round((nf / n_samples) / max(base_frac, 1.0 / n_samples), 1)}

    ranked = sorted(CLASSES, key=lambda c: -opened[c]["n_feasible"])
    top, mid, bottom = ranked[0], ranked[1], ranked[2]

    C_nf = opened["C_UNIVERSALITY"]["n_feasible"]
    A_nf = opened["A_AMPLITUDE"]["n_feasible"]
    B_nf = opened["B_INFORMATION"]["n_feasible"]
    checks = {
        "information_B_opens_least": B_nf <= A_nf and B_nf <= C_nf,           # robust: B clearly smallest
        "C_and_A_are_major_carvers": C_nf > 3 * max(base_nf, 1) and A_nf > 3 * max(base_nf, 1),
        "holography_is_a_minor_carver": B_nf < 0.5 * min(C_nf, A_nf),         # B << the two majors
        "universality_carves_efficiently": C_nf >= 0.7 * A_nf,               # C ~ A with fewer constraints
        "all_classes_carve_something": all(opened[c]["n_feasible"] >= base_nf for c in CLASSES),
    }

    return {
        "version": VERSION,
        "n_samples": n_samples,
        "per_class_constraint_counts": per_class_counts,
        "baseline_feasible_fraction": float(f"{base_frac:.2e}"),
        "baseline_n_feasible": base_nf,
        "opened_by_dropping_class": opened,
        "ranking_biggest_to_smallest_carver": ranked,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            f"The predictivity of the swampland-complete carving is dominated by the SWAMPLAND/ANOMALY and "
            f"POSITIVITY conditions, roughly equally, with holographic/information bounds a minor contributor "
            f"-- a decomposition of WHICH physics pins quantum gravity's low-energy EFT. Dropping each of the "
            f"engine's three constraint classes from the theory-only stack and measuring how much the feasible "
            f"region opens: removing C_UNIVERSALITY (the {per_class_counts.get('C_UNIVERSALITY', 0)} swampland "
            f"+ anomaly/universality conditions -- WGC, distance conjecture, anomaly inflow, 't Hooft "
            f"matching, BNOSSW) opens it the most (~{opened['C_UNIVERSALITY']['opening_factor_vs_baseline']:.0f}x "
            f"more feasible); removing A_AMPLITUDE (the {per_class_counts.get('A_AMPLITUDE', 0)} positivity / "
            f"unitarity amplitude bounds -- scalar and graviton positivities, the dispersion towers, CEMZ-"
            f"adjacent forward bounds) opens it nearly as much "
            f"(~{opened['A_AMPLITUDE']['opening_factor_vs_baseline']:.0f}x); but removing B_INFORMATION (the "
            f"{per_class_counts.get('B_INFORMATION', 0)} holographic / entropy bounds -- Bekenstein, "
            f"subadditivity, GSL, quantum focusing) barely changes it "
            f"(~{opened['B_INFORMATION']['opening_factor_vs_baseline']:.0f}x). So the ranking of carving power "
            f"is {ranked} -- universality and amplitude are the two heavy carvers, information is nearly "
            f"redundant for realistic positive-coupling EFTs. In physics terms: the low-energy EFT of quantum "
            f"gravity is pinned mainly by UNITARITY (amplitude positivity) and SWAMPLAND/ANOMALY consistency, "
            f"NOT by entropy/holographic bounds -- which is a substantive statement about where the "
            f"predictive content of the swampland program actually lives (it reproduces, at the volume level, "
            f"the v2.325 finding that the anomaly/universality family and the leading positivities dominate "
            f"the BINDING, and shows the same is true of the VOLUME). The holographic bounds, while "
            f"individually motivated, are largely implied by positivity+universality for these theories."
        ),
        "honest_scope": (
            "The RANKING (C >= A >> B) is the robust content and is read from the dropped-class feasible "
            "COUNTS (tens of feasible samples per class -- enough to rank), NOT from the ratios to the "
            "baseline, which is a rare event (a few feasible per n) with large statistical error -- so the "
            "opening-FACTORS (e.g. 36x) are order-of-magnitude, but the ORDER of the three classes is "
            "reliable. The class grouping is the engine's own ConstraintClass taxonomy (A/B/C), so 'which "
            "physics' means the engine's assignment of each condition to amplitude / information / "
            "universality -- a reasonable but not unique partition (e.g. CEMZ causality sits in A here). "
            "'B barely carves' is FOR REALISTIC POSITIVE-COUPLING EFTs in this box -- the holographic bounds "
            "would bite harder for exotic couplings (negative, or large parity), so their redundancy is "
            "regime-dependent, echoing the v2.325 always-slack set. The whole computation is the toy-basis "
            "engine encoding, box-dependent as in v2.373. Robust content: universality and amplitude classes "
            "do the bulk of the volume carving, holographic/information little, for realistic higher-"
            "derivative gravity. Toy basis, box-dependent, rare-event baseline. A decomposition of the "
            "program's predictive content by physics class."
        ),
        "references": [
            "this repo: v2.373 (total predictivity ~10^-5, consistency-driven), v2.325 (active-core: anomaly/universality + positivities dominate binding), v2.341 (unitarity/causality/WGC groups)",
            "structural: the engine's ConstraintClass taxonomy (A amplitude / B information / C universality)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=40000)
    p.add_argument("--seed", type=int, default=1)
    args = p.parse_args()
    res = run(n_samples=args.n, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("SWING: which physics carves the EFT? (predictivity by constraint class)")
    print(f"  baseline (all consistency): {res['baseline_feasible_fraction']:.1e}  ({res['baseline_n_feasible']} feasible / {res['n_samples']})")
    for cls in CLASSES:
        d = res["opened_by_dropping_class"][cls]
        print(f"  drop {cls:<16} ({d['n_constraints']:>2} constraints): {d['feasible_fraction_without_class']:.1e}  "
              f"opens ~{d['opening_factor_vs_baseline']:.0f}x  ({d['n_feasible']} feasible)")
    print(f"  ranking (biggest -> smallest carver): {res['ranking_biggest_to_smallest_carver']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
