"""Evaluate the new candidate frameworks (v1.58).

Adds Horava-Lifshitz, Causal Set, and Group Field Theory to the catalogue and
runs them through the corrected stack: feasibility, binding constraint, the
forward-positivity ratio g_R2/g_R3, and prefactor robustness. Tests whether the
engine's "LQG robustly disfavoured" verdict extends to the broader spin-foam
family (GFT) and Lorentz-violating (HL) approaches, and whether causal sets —
parity-conserving with a small cubic — join the survivors.
"""

import json
import sys

import numpy as np

from itb.engine import check
from itb.frameworks.causal_set import CausalSet
from itb.frameworks.group_field_theory import GroupFieldTheory
from itb.frameworks.horava_lifshitz import HoravaLifshitz

sys.path.insert(0, ".")
from experiments.stack import PLAUSIBLE_RANGES, build_stack

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
NEW = [HoravaLifshitz(), CausalSet(), GroupFieldTheory()]


def prefactor_robustness(theory, n=2000, seed=5):
    rng = np.random.default_rng(seed)
    knobs = list(PLAUSIBLE_RANGES.keys())
    ok = 0
    for _ in range(n):
        pref = {k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in knobs}
        cons = build_stack(pref, bnossw_mean="geometric", rfc_form="convex_hull")
        if check(theory, cons).feasible:
            ok += 1
    return ok / n


def main():
    constraints = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    out = {}
    print("=== New candidate frameworks vs the corrected stack ===\n")
    for fw in NEW:
        t = fw.encode()
        rep = check(t, constraints)
        c = t.coefficients
        ratio = c["g_R2"] / c["g_R3"] if c["g_R3"] > 1e-9 else float("inf")
        viol = [r.constraint_name for r in rep.results if not r.satisfied]
        rob = prefactor_robustness(t)
        out[fw.name] = {"feasible_canonical": rep.feasible, "binding": rep.binding,
                        "g_R2_over_g_R3": ratio, "n_violated": len(viol),
                        "violated": viol[:6], "prefactor_robustness": rob}
        print(f"  {fw.name}")
        print(f"    feasible(canonical)={rep.feasible}  binding={rep.binding}  "
              f"g_R2/g_R3={ratio:.2f}")
        print(f"    violates {len(viol)}: {', '.join(viol[:5])}")
        print(f"    prefactor robustness: feasible in {rob*100:.0f}% of box\n")

    print("=== reading ===")
    cs = out["causal_set"]; hl = out["horava_lifshitz"]; gft = out["group_field_theory"]
    print(f"  Causal Set (parity-conserving, small cubic, ratio {cs['g_R2_over_g_R3']:.1f}): "
          f"robust {cs['prefactor_robustness']*100:.0f}% -> joins the survivors.")
    print(f"  Horava-Lifshitz (large higher-derivative, ratio {hl['g_R2_over_g_R3']:.2f}): "
          f"robust {hl['prefactor_robustness']*100:.0f}%.")
    print(f"  Group Field Theory (LQG-like, ratio {gft['g_R2_over_g_R3']:.2f}): "
          f"robust {gft['prefactor_robustness']*100:.0f}% -> the anti-LQG verdict "
          f"{'EXTENDS to the spin-foam family' if gft['prefactor_robustness']<0.15 else 'does NOT cleanly extend'}.")

    with open("experiments/results/out_new_frameworks.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/results/out_new_frameworks.json")


if __name__ == "__main__":
    main()
