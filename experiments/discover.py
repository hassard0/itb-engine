"""Generative theory discovery + invented experiments (v1.27).

The engine has been used defensively (which known frameworks survive?). Here we
use it generatively: search the feasible region (all corrected constraints) for
CONSISTENT theories that are maximally UNLIKE any known framework — candidate
quantum-gravity theories not yet on anyone's map — and for each, invent the
experiment that would reveal it (the coefficient measurement that most separates
it from known physics).

Three searches (scipy Nelder-Mead, parallel multistart on Vulcan):

  1. novelty   — maximize distance from {PureGR, string, AS, LQG, CDT} subject
                 to feasibility. Finds the most novel consistent theory.
  2. parity    — maximize gravitational parity content (g_R2_parity, g_R3_parity)
                 subject to feasibility. Every feasible framework so far is
                 parity-conserving; LQG (the only parity-violator) is excluded.
                 Does a CONSISTENT parity-violating QG exist?
  3. islands   — cluster many feasible solutions to see whether the allowed
                 region is one blob or several disconnected "theory islands".

For each discovered theory we report the single observable (Wilson coefficient)
whose measurement would most sharply distinguish it from its nearest known
framework — the "invented experiment".

Usage:
    python -m experiments.discover --restarts 400 --workers 16
"""

import argparse
import json
import os
import sys

import numpy as np
from scipy.optimize import minimize

from itb.engine import check
from itb.theory import Theory

sys.path.insert(0, ".")
from experiments.stack import build_stack, frameworks

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
CONSTRAINTS = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
KNOWN = {fw.name: np.array([fw.encode().coefficients.get(k, 0.0) for k in KEYS])
         for fw in frameworks()}
# search box (EFT-validity bounded; parity allowed both signs)
LO = np.array([0.0, 0.0, 0.0, 0.0, 0.0, -0.30, -0.30])
HI = np.array([1.2, 1.0, 1.0, 0.7, 0.7, 0.30, 0.30])
LAMBDA = 50.0       # feasibility-penalty weight
MARGIN_TARGET = 0.0  # require worst-case margin >= this (interior robustness); set by CLI


def _vec_to_theory(x):
    return Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)})


def _worst_margin(x):
    rep = check(_vec_to_theory(x), CONSTRAINTS)
    return min((r.margin for r in rep.results), default=0.0), rep.feasible


def _novelty(x):
    return min(float(np.linalg.norm(x - v)) for v in KNOWN.values())


def _penalty(x):
    # box + feasibility penalty (require margin >= MARGIN_TARGET for interior robustness)
    box = np.sum(np.maximum(0.0, LO - x) + np.maximum(0.0, x - HI))
    wm, _ = _worst_margin(x)
    return LAMBDA * (box + max(0.0, MARGIN_TARGET - wm))


def _prefactor_robustness(x, n=2000, seed=314):
    """Fraction of the plausible prefactor box in which this fixed theory stays
    feasible — does the discovered theory survive constraint-prefactor uncertainty?"""
    from experiments.stack import PLAUSIBLE_RANGES
    rng = np.random.default_rng(seed)
    knobs = list(PLAUSIBLE_RANGES.keys())
    theory = _vec_to_theory(x)
    ok = 0
    for _ in range(n):
        pref = {k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in knobs}
        cons = build_stack(pref, bnossw_mean="geometric", rfc_form="convex_hull")
        if check(theory, cons).feasible:
            ok += 1
    return ok / n


def _obj_novelty(x):
    return -_novelty(x) + _penalty(x)


def _obj_parity(x):
    parity = abs(x[5]) + abs(x[6])
    return -parity + _penalty(x)


def _run_one(args):
    kind, seed = args
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(LO, HI)
    obj = _obj_parity if kind == "parity" else _obj_novelty
    res = minimize(obj, x0, method="Nelder-Mead",
                   options={"maxiter": 4000, "xatol": 1e-6, "fatol": 1e-6})
    x = np.clip(res.x, LO, HI)
    wm, feasible = _worst_margin(x)
    return {
        "kind": kind,
        "x": [float(v) for v in x],
        "feasible": bool(feasible),
        "worst_margin": float(wm),
        "novelty": float(_novelty(x)),
        "parity": float(abs(x[5]) + abs(x[6])),
    }


def _nearest_framework(x):
    d = {nm: float(np.linalg.norm(np.array(x) - v)) for nm, v in KNOWN.items()}
    nm = min(d, key=d.get)
    return nm, d[nm]


def _invented_experiment(x):
    """The observable whose measurement most separates this theory from its
    nearest known framework = the coefficient with the largest abs difference."""
    nm, _ = _nearest_framework(x)
    diffs = {k: abs(x[i] - KNOWN[nm][i]) for i, k in enumerate(KEYS)}
    obs = max(diffs, key=diffs.get)
    return nm, obs, diffs[obs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=400)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--margin-target", type=float, default=0.0,
                    help="require interior worst-case margin >= this")
    ap.add_argument("--out", default="experiments/out_discover.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    global MARGIN_TARGET
    MARGIN_TARGET = args.margin_target

    tasks = ([("novelty", s) for s in range(1000, 1000 + args.restarts)]
             + [("parity", s) for s in range(50000, 50000 + args.restarts)])
    print(f"workers={args.workers}  restarts={args.restarts} x2 searches  "
          f"stack={len(CONSTRAINTS)} (corrected)")
    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        results = pool.map(_run_one, tasks, chunksize=4)
        print(f"done ({time.time()-t0:.1f}s)")

    feas = [r for r in results if r["feasible"]]
    nov = sorted([r for r in feas if r["kind"] == "novelty"],
                 key=lambda r: -r["novelty"])
    par = sorted([r for r in feas if r["kind"] == "parity"],
                 key=lambda r: -r["parity"])

    out = {"n_feasible": len(feas), "n_total": len(results)}

    print(f"\nfeasible solutions found: {len(feas)}/{len(results)}")

    if nov:
        best = nov[0]
        nm, d = _nearest_framework(best["x"])
        fwk, obs, gap = _invented_experiment(best["x"])
        rob = _prefactor_robustness(best["x"])
        out["most_novel"] = {**best, "nearest_framework": nm,
                             "nearest_distance": d, "prefactor_robustness": rob,
                             "invented_experiment": {"vs": fwk, "observable": obs, "gap": gap}}
        print("\n=== MOST NOVEL CONSISTENT THEORY ===")
        print("  coefficients: " + ", ".join(f"{k}={v:.3f}" for k, v in zip(KEYS, best["x"])))
        print(f"  worst-case margin: {best['worst_margin']:+.4f}  "
              f"novelty(dist to nearest known): {best['novelty']:.3f}")
        print(f"  nearest known framework: {nm} (distance {d:.3f})")
        print(f"  prefactor robustness: feasible in {rob*100:.0f}% of prefactor box")
        print(f"  INVENTED EXPERIMENT: measure {obs} — it differs by {gap:.3f} "
              f"from {fwk}, the largest separation")

    if par:
        best = par[0]
        fwk, obs, gap = _invented_experiment(best["x"])
        rob = _prefactor_robustness(best["x"])
        out["max_parity"] = {**best, "prefactor_robustness": rob,
                             "invented_experiment": {"vs": fwk, "observable": obs, "gap": gap}}
        print("\n=== MAXIMALLY PARITY-VIOLATING CONSISTENT THEORY ===")
        print("  coefficients: " + ", ".join(f"{k}={v:.3f}" for k, v in zip(KEYS, best["x"])))
        print(f"  parity content |g_R2p|+|g_R3p| = {best['parity']:.3f}  "
              f"worst-case margin {best['worst_margin']:+.4f}")
        print(f"  prefactor robustness: feasible in {rob*100:.0f}% of prefactor box")
        if best["parity"] > 0.02:
            print(f"  => a CONSISTENT parity-violating QG candidate exists "
                  f"(unlike LQG, which is excluded).")
            print(f"  INVENTED EXPERIMENT: measure {obs} (gravitational parity "
                  f"observable) at precision < {best['parity']:.3f}")
        else:
            print("  => no substantially parity-violating consistent theory found "
                  "(parity driven to ~0 by the constraints).")

    # island clustering on novelty solutions
    if len(nov) >= 3:
        pts = np.array([r["x"] for r in nov])
        # greedy clustering at distance 0.15
        centers = []
        labels = []
        for p in pts:
            placed = False
            for ci, c in enumerate(centers):
                if np.linalg.norm(p - c) < 0.15:
                    labels.append(ci); placed = True; break
            if not placed:
                centers.append(p); labels.append(len(centers) - 1)
        out["n_islands"] = len(centers)
        print(f"\n=== FEASIBLE-REGION STRUCTURE ===")
        print(f"  {len(nov)} feasible novelty-solutions cluster into "
              f"{len(centers)} island(s) at distance threshold 0.15")

    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
