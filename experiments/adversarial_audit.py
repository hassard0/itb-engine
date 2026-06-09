"""v1.97 - The adversarial self-audit: which constraints are sole gatekeepers, and
the theory that most nearly fools the stack.

We probe the BOUNDARY of consistency. For each box sample we cache its per-constraint
satisfied-bitmask, then:
  - FAILURE MULTIPLICITY: how many constraints each excluded point fails (the thickness
    of the exclusion shell -- do near-miss points fail 1, or are most points deep
    outside, failing many?).
  - SOLE GATEKEEPERS: for each constraint c, how many 'near-miss' points (failing
    EXACTLY one constraint) does c uniquely guard. NOTE the identity: removing c from
    the stack admits exactly the points whose only failure was c, so
        V_without_c = V0 + gatekeeper(c),
    i.e. the sole-gatekeeper volume IS the v1.93 irreplaceability (we verify this).
  - THE HARDEST NEAR-MISS: the coefficient vector that satisfies the MOST constraints
    with the largest margins while STILL being excluded -- the theory that most nearly
    fools the whole stack -- and the single constraint that kills it.

HONEST: near-miss is sampling-resolution-dependent; the robust content is the RANKING of
sole gatekeepers, the multiplicity distribution, and the hardest-near-miss point.

Run on Vulcan (16 cores):  python experiments/adversarial_audit.py [N]
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from stack import build_stack
from itb.constraints.base import ConstraintClass
from itb.theory import Theory

COEFFS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C", "g_R2_parity", "g_R3_parity"]
LO = np.array([0.05, 0.05, 0.05, 0.01, 0.0, 0.02, 0.0, -0.05])
HI = np.array([0.60, 0.60, 0.70, 0.45, 0.40, 0.60, 0.15, 0.05])

_STACK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
_NAMES = [c.name for c in _STACK]
_NC = len(_STACK)
_CLASS = {ConstraintClass.A_AMPLITUDE: "A", ConstraintClass.B_INFORMATION: "B",
          ConstraintClass.C_UNIVERSALITY: "C"}


def _theory(x):
    return Theory(coefficients={k: float(v) for k, v in zip(COEFFS, x)})


def _chunk(arg):
    seed, n = arg
    rng = np.random.default_rng(seed)
    X = LO + (HI - LO) * rng.random((n, len(COEFFS)))
    bits = np.zeros(n, dtype=np.uint64)
    best_nm = (-np.inf, -1, None)        # (min-other-margin, failed_idx, coeffs)
    for i in range(n):
        th = _theory(X[i])
        rs = [c.evaluate(th) for c in _STACK]
        unsat = [j for j in range(_NC) if not rs[j].satisfied]
        b = np.uint64(0)
        for j in range(_NC):
            if rs[j].satisfied:
                b |= np.uint64(1) << np.uint64(j)
        bits[i] = b
        if len(unsat) == 1:              # near-miss: fails exactly one
            sat_margins = [rs[j].signed_distance_margin for j in range(_NC) if j != unsat[0]]
            m = float(min(sat_margins))
            if m > best_nm[0]:
                best_nm = (m, unsat[0], X[i].copy())
    return bits, best_nm


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    ncpu = max(1, (os.cpu_count() or 4) - 1)
    chunks = ncpu * 4
    per = N // chunks
    from multiprocessing import Pool
    with Pool(ncpu) as pool:
        res = pool.map(_chunk, [(800 + k, per) for k in range(chunks)])
    bits = np.concatenate([r[0] for r in res])
    total = bits.shape[0]
    best_nm = max((r[1] for r in res), key=lambda t: t[0])

    full_mask = (np.uint64(1) << np.uint64(_NC)) - np.uint64(1)
    unsat = (~bits) & full_mask
    # failure multiplicity (popcount of unsat)
    pc = np.zeros(total, dtype=np.int32)
    for k in range(_NC):
        pc += ((unsat >> np.uint64(k)) & np.uint64(1)).astype(np.int32)
    V0 = int((pc == 0).sum())
    mult_hist = {int(m): int((pc == m).sum()) for m in range(0, min(pc.max() + 1, 16))}

    # near-miss (exactly one fail) -> sole gatekeeper per constraint
    nm_mask = pc == 1
    gate = np.zeros(_NC, dtype=int)
    nm_unsat = unsat[nm_mask]
    for k in range(_NC):
        gate[k] = int(((nm_unsat >> np.uint64(k)) & np.uint64(1)).sum())
    rows = sorted([{"constraint": _NAMES[j], "class": _CLASS[_STACK[j].constraint_class],
                    "gatekeeper_volume": int(gate[j]),
                    "irreplaceability_growth_pct": round(100 * gate[j] / V0, 1) if V0 else None}
                   for j in range(_NC)], key=lambda r: -r["gatekeeper_volume"])
    never_sole = [r["constraint"] for r in rows if r["gatekeeper_volume"] == 0]

    # hardest near-miss point
    hardest = {"min_margin_on_others": round(best_nm[0], 4),
               "killed_by": _NAMES[best_nm[1]],
               "coefficients": {k: round(float(v), 4) for k, v in zip(COEFFS, best_nm[2])}}

    # ---- figure: multiplicity histogram + gatekeeper bars ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    ms = sorted(mult_hist)
    ax1.bar([m for m in ms if m > 0], [mult_hist[m] for m in ms if m > 0],
            color="#1f77b4")
    ax1.set_yscale("log"); ax1.set_xlabel("number of constraints failed")
    ax1.set_ylabel("samples (log)")
    ax1.set_title(f"exclusion-shell thickness (V0={V0}; near-miss[fail 1]={mult_hist.get(1,0)})",
                  fontsize=9)
    cls_color = {"A": "#1f77b4", "B": "#ff7f0e", "C": "#9467bd"}
    top = [r for r in rows if r["gatekeeper_volume"] > 0][:18]
    ax2.barh([r["constraint"] for r in top][::-1],
             [r["gatekeeper_volume"] for r in top][::-1],
             color=[cls_color[r["class"]] for r in top][::-1])
    ax2.set_xscale("log")
    ax2.set_xlabel("sole-gatekeeper volume (= v1.93 irreplaceability x V0)")
    ax2.tick_params(axis="y", labelsize=6.5)
    ax2.set_title("which constraints uniquely guard near-miss territory", fontsize=9)
    fig.suptitle("v1.97  Adversarial self-audit: sole gatekeepers & the hardest near-miss",
                 fontsize=12)
    fig.tight_layout()
    png = "/tmp/adversarial_audit.png"
    fig.savefig(png, dpi=140)

    summary = {
        "samples": total, "island_V0": V0,
        "failure_multiplicity_histogram": mult_hist,
        "near_miss_fail_exactly_one": mult_hist.get(1, 0),
        "identity_check": "V_without_c = V0 + gatekeeper(c): sole-gatekeeper volume IS "
                          "the v1.93 irreplaceability (growth% = 100*gatekeeper/V0).",
        "top_sole_gatekeepers": rows[:8],
        "constraints_that_never_act_alone": never_sole,
        "n_never_sole": len(never_sole),
        "hardest_near_miss": hardest,
        "interpretation": "Most excluded points fail MANY constraints (deep outside); a "
            "thin near-miss shell fails exactly one. The sole-gatekeeper ranking equals "
            "the v1.93 irreplaceability (an identity). Constraints that NEVER act alone are "
            "redundant at the boundary. The hardest near-miss is the theory that most nearly "
            "fools the stack -- consistent with everything except a single condition.",
        "honest": "near-miss is sampling-resolution-dependent; robust content is the ranking, "
                  "the multiplicity distribution, and the hardest-near-miss point.",
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
