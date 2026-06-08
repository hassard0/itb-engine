"""Catalog of possible quantum gravities: extreme points of the allowed region (v1.32).

Instead of one novel theory at a time, map the full EXTENT of consistent theory
space: maximize many random linear objectives (random directions in 7-D Wilson
space) over the feasible set of the corrected stack. Each maximizer is an extreme
point — a distinct consistent theory at a "corner" of what the constraints
allow. Deduplicated, these are a catalog of qualitatively different quantum
gravities, most of which no catalogued framework occupies.

For each catalog entry we report its dominant signature, novelty (distance from
the nearest known framework), parity, and prefactor robustness.

Usage:
    python -m experiments.catalog --directions 600 --workers 16
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
from experiments.stack import PLAUSIBLE_RANGES, build_stack, frameworks

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
CONSTRAINTS = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
KNOWN = {fw.name: np.array([fw.encode().coefficients.get(k, 0.0) for k in KEYS])
         for fw in frameworks()}
LO = np.array([0.0, 0.0, 0.0, 0.0, 0.0, -0.30, -0.30])
HI = np.array([1.2, 1.0, 1.0, 0.7, 0.7, 0.30, 0.30])
MARGIN = 0.003


def _worst_margin(x):
    rep = check(Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)}), CONSTRAINTS)
    return min((r.margin for r in rep.results), default=0.0)


def _extreme(args):
    """Maximize direction.x over the feasible set -> one extreme consistent theory."""
    seed, = args
    rng = np.random.default_rng(seed)
    d = rng.normal(size=len(KEYS)); d /= np.linalg.norm(d)
    best = None
    for _ in range(3):
        x0 = rng.uniform(LO, HI)

        def obj(x):
            xx = np.clip(x, LO, HI)
            pen = np.sum(np.maximum(0, LO - x) + np.maximum(0, x - HI))
            return -float(d @ xx) + 100 * (pen + max(0.0, MARGIN - _worst_margin(xx)))

        res = minimize(obj, x0, method="Nelder-Mead",
                       options={"maxiter": 4000, "fatol": 1e-7, "xatol": 1e-7})
        x = np.clip(res.x, LO, HI)
        if _worst_margin(x) >= MARGIN:
            val = float(d @ x)
            if best is None or val > best[0]:
                best = (val, [float(v) for v in x])
    return best[1] if best else None


def _novelty(x):
    return min(float(np.linalg.norm(np.array(x) - v)) for v in KNOWN.values())


def _nearest(x):
    dd = {nm: float(np.linalg.norm(np.array(x) - v)) for nm, v in KNOWN.items()}
    return min(dd, key=dd.get), min(dd.values())


def _signature(x):
    c = dict(zip(KEYS, x))
    parity = abs(c["g_R2_parity"]) + abs(c["g_R3_parity"])
    tags = []
    if parity > 0.03:
        tags.append("parity-violating")
    if c["g_R3"] > 0.35:
        tags.append("cubic-dominated")
    if c["g_R3"] < 0.05:
        tags.append("cubic-suppressed")
    if c["g_8"] < 0.08:
        tags.append("low-g8")
    if c["g_8"] > 0.6:
        tags.append("high-g8")
    if c["g_4"] < 0.25:
        tags.append("weakly-coupled")
    if c["g_R2"] > 0.5:
        tags.append("strong-curvature")
    return tags or ["generic-interior"]


def _robust(x, n=1500, seed=7):
    rng = np.random.default_rng(seed)
    knobs = list(PLAUSIBLE_RANGES.keys())
    t = Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)})
    ok = sum(check(t, build_stack({k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in knobs},
                                  bnossw_mean="geometric", rfc_form="convex_hull")).feasible
             for _ in range(n))
    return ok / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--directions", type=int, default=600)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="experiments/out_catalog.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    print(f"workers={args.workers}  maximizing {args.directions} random directions "
          f"over the feasible set")
    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        pts = [p for p in pool.map(_extreme, [(i,) for i in range(2000, 2000 + args.directions)])
               if p is not None]
        print(f"{len(pts)} extreme points found ({time.time()-t0:.1f}s)")

    # dedupe at distance 0.10
    uniq = []
    for p in pts:
        if all(np.linalg.norm(np.array(p) - np.array(u)) > 0.10 for u in uniq):
            uniq.append(p)
    print(f"{len(uniq)} distinct extreme theories after dedup")

    catalog = []
    for x in uniq:
        nm, d = _nearest(x)
        catalog.append({"coeffs": {k: round(v, 3) for k, v in zip(KEYS, x)},
                        "signature": _signature(x), "nearest_framework": nm,
                        "novelty": round(_novelty(x), 3),
                        "parity": round(abs(x[5]) + abs(x[6]), 3)})
    catalog.sort(key=lambda e: -e["novelty"])

    # robustness only for the most novel handful (expensive)
    for e in catalog[:6]:
        e["prefactor_robustness"] = round(_robust([e["coeffs"][k] for k in KEYS]), 3)

    out = {"n_extreme": len(pts), "n_distinct": len(uniq), "catalog": catalog}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print(f"\n=== CATALOG OF POSSIBLE QUANTUM GRAVITIES (extreme consistent theories) ===")
    print(f"  {len(uniq)} distinct extreme theories; showing the 12 most novel:")
    novel_count = sum(1 for e in catalog if e["novelty"] > 0.15)
    pv_count = sum(1 for e in catalog if e["parity"] > 0.03)
    print(f"  ({novel_count} are >0.15 from any known framework; {pv_count} are parity-violating)\n")
    for i, e in enumerate(catalog[:12], 1):
        rob = f" robust {int(e.get('prefactor_robustness', -1)*100)}%" if "prefactor_robustness" in e else ""
        cc = e["coeffs"]
        print(f"  {i:>2}. novelty {e['novelty']:.2f} [{','.join(e['signature'])}] "
              f"near {e['nearest_framework']}{rob}")
        print(f"      g_4={cc['g_4']} g_6={cc['g_6']} g_8={cc['g_8']} "
              f"g_R2={cc['g_R2']} g_R3={cc['g_R3']} parity={e['parity']}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
