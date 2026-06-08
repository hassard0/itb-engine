"""Pin the parity ceiling precisely (v1.37).

v1.31 mapped max consistent parity vs cubic coupling g_R3 noisily (6 restarts/
point). Parity violation is now the headline testable signal (v1.35/36), so this
nails the ceiling: for each g_R3 on a fine grid, maximize |g_R2_parity| +
|g_R3_parity| over the corrected stack with MANY restarts (parallelized over
grid x restarts on Vulcan), and identify the binding constraint at the optimum.

Questions: is the ceiling monotone increasing as g_R3 -> 0? What is the absolute
maximum consistent parity, and which constraint sets it?
"""

import argparse
import json
import os
import sys
from collections import Counter

import numpy as np
from scipy.optimize import minimize

from itb.engine import check
from itb.theory import Theory

sys.path.insert(0, ".")
from experiments.stack import build_stack

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
CONSTRAINTS = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
LO = np.array([0.0, 0.0, 0.0, 0.0, 0.0, -0.30, -0.30])
HI = np.array([1.2, 1.0, 1.0, 0.7, 0.7, 0.30, 0.30])
MARGIN = 0.003


def _report(x):
    return check(Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)}), CONSTRAINTS)


def _worst(x):
    return min((r.margin for r in _report(x).results), default=0.0)


def _parity(x):
    return abs(x[5]) + abs(x[6])


def _one(args):
    """One restart: maximize parity at fixed g_R3. Returns (parity, x, binding)."""
    gr3, seed = args
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(LO, HI); x0[4] = gr3

    def obj(x):
        xx = np.clip(x, LO, HI); xx[4] = gr3
        pen = np.sum(np.maximum(0, LO - x) + np.maximum(0, x - HI))
        return -_parity(xx) + 50 * (pen + max(0.0, MARGIN - _worst(xx)))

    res = minimize(obj, x0, method="Nelder-Mead",
                   options={"maxiter": 5000, "fatol": 1e-8, "xatol": 1e-8})
    x = np.clip(res.x, LO, HI); x[4] = gr3
    if _worst(x) < MARGIN:
        return gr3, 0.0, None, None
    rep = _report(x)
    # binding constraint = smallest-margin one (closest to active)
    binding = min(rep.results, key=lambda r: r.margin)
    return gr3, _parity(x), [float(v) for v in x], binding.constraint_name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=30)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="experiments/out_parity_ceiling.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    gr3_grid = np.round(np.linspace(0.0, 0.30, 16), 3)
    tasks = [(float(g), 5000 + int(g * 1000) * 100 + r)
             for g in gr3_grid for r in range(args.restarts)]
    print(f"workers={args.workers}  {len(gr3_grid)} g_R3 points x {args.restarts} restarts "
          f"= {len(tasks)} optimizations")
    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        results = pool.map(_one, tasks, chunksize=4)
        print(f"done ({time.time()-t0:.1f}s)")

    # aggregate: best parity per g_R3
    best = {float(g): (0.0, None, None) for g in gr3_grid}
    binders = Counter()
    for gr3, p, x, b in results:
        if x is not None and p > best[gr3][0]:
            best[gr3] = (p, x, b)
        if b is not None:
            binders[b] += 1

    curve = []
    for g in gr3_grid:
        p, x, b = best[float(g)]
        ratio = (x[3] / g) if (x and g > 1e-6) else None
        curve.append({"g_R3": float(g), "max_parity": p,
                      "binding": b, "g_R2_over_g_R3": ratio})
    overall = max(curve, key=lambda c: c["max_parity"])

    out = {"curve": curve, "ceiling": overall["max_parity"],
           "ceiling_g_R3": overall["g_R3"], "ceiling_binding": overall["binding"],
           "binding_histogram": dict(binders.most_common())}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print("\n=== PARITY CEILING vs cubic coupling g_R3 ===")
    print(f"  {'g_R3':>6} {'max|parity|':>12} {'g_R2/g_R3':>10}  binding")
    for c in curve:
        r = f"{c['g_R2_over_g_R3']:6.2f}" if c["g_R2_over_g_R3"] else "   inf"
        print(f"  {c['g_R3']:>6.3f} {c['max_parity']:>12.4f} {r:>10}  {c['binding'] or '-'}")
    # monotonicity check
    ps = [c["max_parity"] for c in curve if c["max_parity"] > 0]
    mono = all(curve[i]["max_parity"] >= curve[i+1]["max_parity"] - 0.005
               for i in range(len(curve)-1) if curve[i+1]["max_parity"] > 0)
    print(f"\n  absolute ceiling: |parity| = {overall['max_parity']:.4f} at "
          f"g_R3 = {overall['ceiling_g_R3'] if 'ceiling_g_R3' in overall else overall['g_R3']:.3f}, "
          f"set by {overall['binding']}")
    print(f"  monotone-increasing as g_R3 -> 0 (within 0.005)? {mono}")
    print(f"  binding-constraint histogram (at the ceilings): {dict(binders.most_common(4))}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
