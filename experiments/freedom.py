"""Freedom map of consistent theory space (v1.33).

Where does consistent quantum gravity have room to vary, and where is it pinned?
Two measurements over the feasible set of the corrected stack:

  1. per-coefficient extent: maximize and minimize each Wilson coefficient over
     the feasible set -> [min, max] feasible range. A wide range = a loose
     direction (new-physics frontier); a narrow range = a tight direction (a
     robust prediction of the constraint stack).
  2. principal axes: PCA on a cloud of feasible extreme points -> the coefficient
     COMBINATIONS that vary most / least across consistent theories.

Usage:
    python -m experiments.freedom --workers 16
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
from experiments.stack import build_stack

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
CONSTRAINTS = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
LO = np.array([0.0, 0.0, 0.0, 0.0, 0.0, -0.30, -0.30])
HI = np.array([1.2, 1.0, 1.0, 0.7, 0.7, 0.30, 0.30])
MARGIN = 0.003


def _worst_margin(x):
    rep = check(Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)}), CONSTRAINTS)
    return min((r.margin for r in rep.results), default=0.0)


def _extremize(args):
    """Maximize (sign=+1) or minimize (sign=-1) coordinate idx over feasible set."""
    idx, sign, seed = args
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(5):
        x0 = rng.uniform(LO, HI)

        def obj(x):
            xx = np.clip(x, LO, HI)
            pen = np.sum(np.maximum(0, LO - x) + np.maximum(0, x - HI))
            return -sign * xx[idx] + 100 * (pen + max(0.0, MARGIN - _worst_margin(xx)))

        res = minimize(obj, x0, method="Nelder-Mead",
                       options={"maxiter": 4000, "fatol": 1e-7, "xatol": 1e-7})
        x = np.clip(res.x, LO, HI)
        if _worst_margin(x) >= MARGIN:
            val = sign * x[idx]
            if best is None or val > best:
                best = float(val)
    return idx, sign, (sign * best if best is not None else None)


def _extreme_cloud(args):
    seed, = args
    rng = np.random.default_rng(seed)
    d = rng.normal(size=len(KEYS)); d /= np.linalg.norm(d)
    x0 = rng.uniform(LO, HI)

    def obj(x):
        xx = np.clip(x, LO, HI)
        pen = np.sum(np.maximum(0, LO - x) + np.maximum(0, x - HI))
        return -float(d @ xx) + 100 * (pen + max(0.0, MARGIN - _worst_margin(xx)))

    res = minimize(obj, x0, method="Nelder-Mead", options={"maxiter": 3000, "fatol": 1e-7})
    x = np.clip(res.x, LO, HI)
    return [float(v) for v in x] if _worst_margin(x) >= MARGIN else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="experiments/out_freedom.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        cloud = [p for p in pool.map(_extreme_cloud, [(i,) for i in range(2000, 3000)])
                 if p is not None]
        print(f"{len(cloud)}-point extreme cloud done ({time.time()-t0:.1f}s)")

    # augment with the v1.32 catalog points if present (more boundary coverage)
    try:
        cat = json.load(open("experiments/results/out_catalog.json"))
        cloud += [[e["coeffs"][k] for k in KEYS] for e in cat["catalog"]]
        print(f"augmented with {len(cat['catalog'])} catalog points -> {len(cloud)} total")
    except Exception:
        pass

    C = np.array(cloud)
    # per-coefficient extent estimated empirically from the boundary cloud
    extent = {}
    for i, k in enumerate(KEYS):
        mn, mx = float(C[:, i].min()), float(C[:, i].max())
        extent[k] = {"min": mn, "max": mx, "range": mx - mn}

    # PCA on the cloud
    C = np.array(cloud)
    Cc = C - C.mean(axis=0)
    cov = (Cc.T @ Cc) / len(Cc)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(-evals)
    pcs = []
    for o in order[:3]:
        v = evecs[:, o]
        # dominant coefficient in this PC
        dom = KEYS[int(np.argmax(np.abs(v)))]
        pcs.append({"variance": float(evals[o]), "dominant": dom,
                    "loadings": {k: round(float(v[i]), 2) for i, k in enumerate(KEYS)}})

    out = {"extent": extent, "principal_components": pcs, "cloud_size": len(cloud)}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print("\n=== FREEDOM MAP: per-coefficient feasible extent ===")
    print("  (wide range = loose direction / new-physics frontier; narrow = robust prediction)")
    ranked = sorted(KEYS, key=lambda k: -(extent[k]["range"] or 0))
    for k in ranked:
        e = extent[k]
        bar = "#" * int((e["range"] or 0) / 0.05)
        print(f"  {k:<14} [{e['min']:+.3f}, {e['max']:+.3f}]  range={e['range']:.3f}  {bar}")
    print("\n=== PRINCIPAL AXES OF CONSISTENT THEORY SPACE ===")
    for i, pc in enumerate(pcs, 1):
        top = sorted(pc["loadings"].items(), key=lambda kv: -abs(kv[1]))[:3]
        print(f"  PC{i} (var {pc['variance']:.4f}, dominant {pc['dominant']}): "
              + ", ".join(f"{k}={v:+.2f}" for k, v in top))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
