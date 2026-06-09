"""v1.70 - Is the a-theorem sign bound (g_R2 >= 0) INDEPENDENT, or already
implied by the existing stack?

Rigorous empirical test. We do NOT assume the answer. Over a wide box that
deliberately includes NEGATIVE g_R2 (g_R2 in [-0.5, 0.5], g_R3 in [-0.2, 0.5]),
at a string-like matter point, we ask:

   Is there ANY point where the corrected stack (without the a-theorem) is
   fully satisfied, yet g_R2 < 0 ?

If such a point exists -> the a-theorem ADDS information (it would exclude it):
   the bound is INDEPENDENT.
If no such point exists -> the existing stack already forbids g_R2 < 0:
   the a-theorem is REDUNDANT in this basis.

We also check the 5 frameworks and report, for the witness search, which
existing constraint already kills each g_R2 < 0 point (the "shadow enforcer").
"""
import json
import sys

import numpy as np

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from stack import build_stack, frameworks
from itb.constraints.a_theorem import ATheoremMonotonicity
from itb.theory import Theory

BASE = {"g_4": 0.5, "g_6": 0.4, "g_8": 0.4,
        "g_R2_parity": 0.0, "g_R3_parity": 0.0}

N = 81


def stack_feasible(stack, th):
    """(all_pass, list_of_failed_names)."""
    failed = [c.name for c in stack if not c.evaluate(th).satisfied]
    return (len(failed) == 0), failed


def main():
    stack = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    a_thm = ATheoremMonotonicity()

    xs = np.linspace(-0.5, 0.5, N)    # g_R2 includes NEGATIVE values
    ys = np.linspace(-0.2, 0.5, N)    # g_R3

    # Search for a witness: feasible under the existing stack but g_R2 < 0.
    witnesses = 0
    # also: among ALL g_R2<0 cells, which existing constraint is the shadow
    # enforcer (first/most-common failing constraint)?
    shadow_counts = {}
    neg_cells = 0
    # And: does a-theorem ever flip a cell that the stack called feasible?
    flips = 0

    for gR2 in xs:
        for gR3 in ys:
            coeffs = dict(BASE); coeffs["g_R2"] = float(gR2); coeffs["g_R3"] = float(gR3)
            th = Theory(coefficients=coeffs)
            ok, failed = stack_feasible(stack, th)
            a_ok = a_thm.evaluate(th).satisfied
            if gR2 < 0:
                neg_cells += 1
                # shadow enforcer: which existing constraint kills this g_R2<0 cell?
                for nm in failed:
                    shadow_counts[nm] = shadow_counts.get(nm, 0) + 1
                if ok:               # feasible under existing stack AND g_R2<0
                    witnesses += 1
                if ok and not a_ok:  # a-theorem would newly exclude it
                    flips += 1

    # frameworks: does a-theorem change any framework verdict?
    fw_rows = []
    for fw in frameworks():
        th = fw.encode()
        ok, failed = stack_feasible(stack, th)
        a_ok = a_thm.evaluate(th).satisfied
        fw_rows.append({"framework": fw.name, "g_R2": th.coefficients.get("g_R2"),
                        "stack_feasible": ok, "a_theorem_ok": a_ok,
                        "would_flip": ok and not a_ok})

    shadow = dict(sorted(shadow_counts.items(), key=lambda kv: -kv[1])[:5])
    summary = {
        "box": {"g_R2": [-0.5, 0.5], "g_R3": [-0.2, 0.5], "grid": f"{N}x{N}"},
        "negative_gR2_cells": neg_cells,
        "witnesses_feasible_with_negative_gR2": witnesses,
        "cells_a_theorem_would_newly_exclude": flips,
        "verdict": ("INDEPENDENT (a-theorem adds information)" if flips > 0
                    else "REDUNDANT in this basis (existing stack already implies g_R2>=0)"),
        "shadow_enforcers_on_negative_gR2": shadow,
        "frameworks": fw_rows,
        "framework_flips": sum(1 for r in fw_rows if r["would_flip"]),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
