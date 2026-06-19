"""Theory-space phase mapping via feasible-seed connectivity (v1.28/v2.13).

The feasible region is a thin sliver in 8-D (uniform hit rate ~1e-6), so
rejection sampling fails. Instead we: (1) multistart-optimize to deep-interior
feasible SEEDS spread across the region; (2) test straight-segment feasibility
between seed pairs; (3) compute connected components of the resulting seed graph.

If the straight segment between two seeds is feasible, they are the same phase.
No straight edge is not proof of disconnection, because a curved path may still
connect the points. This experiment is a conservative connectivity witness, not
a topology theorem.

Usage:
    python -m experiments.phases --seeds 240 --workers 16
"""

import argparse
import json
import os
import sys

import numpy as np
from scipy.optimize import minimize
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from itb.engine import check
from itb.theory import Theory

sys.path.insert(0, ".")
from experiments.stack import build_stack
from itb.predict import FRAMEWORKS

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C", "g_R2_parity", "g_R3_parity"]
CONSTRAINTS = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
KNOWN = {name: np.array([fw.encode().coefficients.get(k, 0.0) for k in KEYS])
         for name, fw in FRAMEWORKS.items()}
LO = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.02, -0.30, -0.30])
HI = np.array([1.2, 1.0, 1.0, 0.7, 0.7, 0.80, 0.30, 0.30])


def _worst_margin(x):
    rep = check(Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)}), CONSTRAINTS)
    return min((r.margin for r in rep.results), default=0.0)


def _feasible(x):
    if np.any(x < LO) or np.any(x > HI):
        return False
    return _worst_margin(x) >= 0.0


_KNOWN_ARR = list(KNOWN.values())


def _novelty(x):
    return min(float(np.linalg.norm(x - v)) for v in _KNOWN_ARR)


def _seed(args):
    """Find a DIVERSE feasible seed: maximize novelty (distance from known
    frameworks) subject to an interior margin, so seeds spread across the
    feasible region rather than collapsing to its Chebyshev centre."""
    seed, = args
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(LO, HI)
    res = minimize(lambda x: -_novelty(np.clip(x, LO, HI))
                   + 50 * (np.sum(np.maximum(0, LO - x) + np.maximum(0, x - HI))
                           + max(0.0, 0.003 - _worst_margin(np.clip(x, LO, HI)))),
                   x0, method="Nelder-Mead",
                   options={"maxiter": 4000, "fatol": 1e-7, "xatol": 1e-7})
    x = np.clip(res.x, LO, HI)
    if _worst_margin(x) >= 0.003:
        return [float(v) for v in x]
    return None


def _segment_feasible(a, b, m=24):
    """Is the straight segment a->b entirely feasible? (Underestimates
    connectivity for non-convex regions: 'yes' is a sure edge, 'no' is not a
    sure cut.)"""
    a, b = np.array(a), np.array(b)
    for t in np.linspace(0, 1, m):
        if not _feasible(a + t * (b - a)):
            return False
    return True


def _edges(args):
    """Connectivity edges for one seed vs all later seeds."""
    i, seeds = args
    out = []
    for j in range(i + 1, len(seeds)):
        if _segment_feasible(seeds[i], seeds[j]):
            out.append((i, j))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=400)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="experiments/out_phases.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        raw = [s for s in pool.map(_seed, [(i,) for i in range(3000, 3000 + args.seeds)])
               if s is not None]
        print(f"{len(raw)} diverse feasible seeds found ({time.time()-t0:.1f}s)")
        # dedupe near-identical seeds (within 0.02)
        seeds = []
        for s in raw:
            if all(np.linalg.norm(np.array(s) - np.array(t)) > 0.02 for t in seeds):
                seeds.append(s)
        print(f"{len(seeds)} distinct seeds after dedup")
        t1 = time.time()
        edge_lists = pool.map(_edges, [(i, seeds) for i in range(len(seeds))])
        print(f"segment-connectivity done ({time.time()-t1:.1f}s)")

    n = len(seeds)
    edges = [e for lst in edge_lists for e in lst]
    if edges:
        ij = np.array(edges)
        g = coo_matrix((np.ones(len(ij)), (ij[:, 0], ij[:, 1])), shape=(n, n))
        ncomp, labels = connected_components(g, directed=False)
    else:
        ncomp, labels = n, np.arange(n)
    sizes = np.bincount(labels)
    pts = np.array(seeds)

    phases = []
    for ci in np.argsort(-sizes):
        members = pts[labels == ci]
        centroid = members.mean(axis=0)
        dists = {nm: float(np.linalg.norm(centroid - v)) for nm, v in KNOWN.items()}
        nm = min(dists, key=dists.get)
        # span of the component (max pairwise distance) — is it a point or a region?
        span = 0.0
        if len(members) > 1:
            span = float(max(np.linalg.norm(a - b) for a in members for b in members))
        phases.append({
            "size": int(sizes[ci]),
            "span": span,
            "centroid": {k: float(v) for k, v in zip(KEYS, centroid)},
            "nearest_framework": nm, "nearest_distance": dists[nm],
            "contains_framework": dists[nm] < 0.10,
            "parity_violating": bool(abs(centroid[6]) + abs(centroid[7]) > 0.02),
        })

    out = {"n_seeds": n, "n_components_straightline": int(ncomp),
           "basis": KEYS,
           "box": {k: [float(LO[i]), float(HI[i])] for i, k in enumerate(KEYS)},
           "method": "8D straight-segment feasibility connectivity (lower bound on connectivity)",
           "phases": phases[:20]}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print("\n=== THEORY-SPACE STRUCTURE ===")
    print(f"  {n} diverse feasible seeds -> {ncomp} straight-line-connected component(s)")
    print("  (straight-line is a LOWER bound on connectivity; curved feasible "
          "paths can merge these further)")
    big = [p for p in phases if p["size"] >= 2]
    print(f"\n  components with >=2 seeds: {len(big)}")
    for i, ph in enumerate(phases[:8], 1):
        tag = (f"CONTAINS {ph['nearest_framework']}" if ph["contains_framework"]
               else f"novel (nearest {ph['nearest_framework']} @ {ph['nearest_distance']:.2f})")
        pv = " PARITY-VIOLATING" if ph["parity_violating"] else ""
        cen = ", ".join(
            f"{k}={ph['centroid'][k]:.2f}" for k in ("g_4", "g_R2", "g_C", "g_R3")
        )
        print(f"  comp {i}: {ph['size']:>3} seeds, span {ph['span']:.2f}  [{tag}]{pv}  {cen}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
