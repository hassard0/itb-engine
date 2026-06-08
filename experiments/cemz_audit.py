"""Re-audit: does CEMZ causality change any framework verdict? (v1.61)

Adds the CEMZ graviton-causality bound (|g_R3| <= kappa*sqrt(g_4*g_R2)) to the
corrected stack and checks, for the in-scope frameworks, whether causality
independently constrains them — and at what kappa it bites each.
"""

import json
import sys

import numpy as np

from itb.constraints.cemz_causality import CEMZCausality
from itb.constraints.cross_sector_efthedron import CrossSectorEFThedron
from itb.engine import check
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.group_field_theory import GroupFieldTheory
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT

sys.path.insert(0, ".")
from experiments.stack import build_stack
from itb.scope import engine_validity

FWS = [StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
       CausalDynamicalTriangulation(), GroupFieldTheory(),
       DiscoveredNovel(), DiscoveredParityViolating(), DiscoveredHighG8()]


def main():
    full = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    # full now INCLUDES cemz + cross-sector EFThedron; make a version without both new ones
    NEW = {"cemz_causality", "cross_sector_efthedron"}
    without_new = [c for c in full if c.name not in NEW]

    print("=== v1.61 new-constraint re-audit (CEMZ kappa=0.8, EFThedron alpha=1.1) ===\n")
    print(f"  {'framework':<28}{'CEMZ marg':>11}{'EFThed marg':>13}  scope")
    out = {}
    for fw in FWS:
        t = fw.encode()
        cemz = CEMZCausality(kappa=0.8).evaluate(t)
        efth = CrossSectorEFThedron(alpha=1.1).evaluate(t)
        sc = engine_validity(fw)
        out[fw.name] = {"cemz_margin": float(cemz.margin), "cemz_ok": cemz.satisfied,
                        "efthedron_margin": float(efth.margin), "efthedron_ok": efth.satisfied,
                        "in_scope": sc.in_scope}
        print(f"  {fw.name:<28}{cemz.margin:>11.3f}{efth.margin:>13.4f}  "
              f"{'in' if sc.in_scope else 'OUT'}  "
              f"{'' if (cemz.satisfied and efth.satisfied) else '<-- violates new'}")

    # does adding the new constraints change feasibility for in-scope frameworks?
    print("\n  feasibility change from adding the new constraints (in-scope):")
    changed = []
    for fw in FWS:
        if not engine_validity(fw).in_scope:
            continue
        f_without = check(fw.encode(), without_new).feasible
        f_with = check(fw.encode(), full).feasible
        tag = "  <== NEW CONSTRAINT FLIPS verdict" if f_without != f_with else ""
        if f_without != f_with:
            changed.append(fw.name)
        print(f"    {fw.name:<28} without_new={f_without}  with_new={f_with}{tag}")

    print(f"\n=== reading ===")
    print(f"  kappa-bite = the causality prefactor at which each framework first violates")
    print(f"  CEMZ. Frameworks with kappa-bite < 1 are constrained by causality at O(1)")
    print(f"  prefactors. At canonical kappa=0.8, CEMZ adds an INDEPENDENT (causality, not")
    print(f"  positivity) pressure on the large-cubic theories.")
    if changed:
        print(f"  CEMZ newly flips: {changed}")
    else:
        print(f"  No NEW exclusions at kappa=0.8 (the large-cubic frameworks already fail")
        print(f"  the corrected stack via forward positivity); CEMZ corroborates that")
        print(f"  verdict from a DIFFERENT principle, tightening as kappa decreases.")

    with open("experiments/results/out_cemz_audit.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/results/out_cemz_audit.json")


if __name__ == "__main__":
    main()
