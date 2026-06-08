"""Combined LQG-survival search (v1.26).

The realism program has shown LQG's exclusion mechanism move from RFC (v1.23
artifact) to BNOSSW (v1.23 fragile) to forward positivity (v1.25 artifact) to
its parity-violation anomaly inflow + complexity. This is the decisive test:
sample JOINTLY over BOTH the constraint prefactors AND LQG's representative
coefficients (Dr. M.'s ranges) and ask —

    is there ANY corner of the joint plausible space where LQG is full-stack
    feasible? If not, LQG-exclusion is robust. If yes, how large is that corner,
    and what has to be true for LQG to survive?

We also tabulate, when LQG is infeasible, which constraints violate — to see
whether anomaly inflow (LQG's current top robust excluder) is itself a
knife-edge.

Usage:
    python -m experiments.lqg_survival --n 500000 --workers 16
"""

import argparse
import json
import os
import sys
from collections import Counter

import numpy as np

from itb.engine import check
from itb.theory import Theory

sys.path.insert(0, ".")
from experiments.stack import CANONICAL, PLAUSIBLE_RANGES, build_stack, frameworks

KNOBS = list(CANONICAL.keys())
LQG_NOM = dict(next(fw for fw in frameworks() if fw.name == "lqg_induced").encode().coefficients)
CONSTRAINT_NAMES = [c.name for c in build_stack()]
_BNOSSW_MEAN = "geometric"  # robust form (harmonic is fragile, v1.23 F4)

# LQG coefficient uncertainty (Dr. M.): g_4 pinned; g_R3 via spin-foam ratio;
# parity Immirzi-sensitive; g_6/g_8/g_R2 representative.
LQG_RANGES = {
    "g_4": ("rel", 0.10),
    "g_6": ("rel", 0.40),
    "g_8": ("rel", 0.40),
    "g_R2": ("rel", 0.40),
    "g_R3_ratio": (0.10, 0.70),         # g_R3 = ratio * g_R2
    "parity_scale": (0.30, 1.50),       # scales both parity coeffs together
}


def _sample_lqg(rng):
    c = {}
    for k in ("g_4", "g_6", "g_8", "g_R2"):
        _, r = LQG_RANGES[k]
        c[k] = LQG_NOM[k] * (1.0 + rng.uniform(-r, r))
    lo, hi = LQG_RANGES["g_R3_ratio"]
    c["g_R3"] = c["g_R2"] * rng.uniform(lo, hi)
    plo, phi = LQG_RANGES["parity_scale"]
    ps = rng.uniform(plo, phi)
    c["g_R2_parity"] = LQG_NOM["g_R2_parity"] * ps
    c["g_R3_parity"] = LQG_NOM["g_R3_parity"] * ps
    return c


def _sample_prefactors(rng):
    return {k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in KNOBS}


def _worker(seed):
    rng = np.random.default_rng(seed)
    pref = _sample_prefactors(rng)
    coeffs = _sample_lqg(rng)
    constraints = build_stack(pref, bnossw_mean=_BNOSSW_MEAN, rfc_form="convex_hull")
    rep = check(Theory(coefficients=coeffs, name="lqg_induced"), constraints)
    violated = tuple(r.constraint_name for r in rep.results if not r.satisfied)
    return rep.feasible, violated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500000)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="experiments/out_lqg_survival.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    print(f"workers={args.workers}  n={args.n}  "
          f"joint LQG(coeffs) x prefactors, geometric BNOSSW + convex-hull RFC")

    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        results = pool.map(_worker, range(7000, 7000 + args.n),
                           chunksize=max(1, args.n // (args.workers * 8)))
        print(f"done ({time.time()-t0:.1f}s)")

    feasible = sum(1 for f, _ in results if f)
    viol = Counter()
    sole = Counter()   # constraints that are the ONLY violator (would flip verdict)
    for f, v in results:
        if f:
            continue
        for c in v:
            viol[c] += 1
        if len(v) == 1:
            sole[v[0]] += 1

    n = args.n
    out = {
        "n": n,
        "lqg_feasible_fraction": feasible / n,
        "violating_constraint_prob": {c: viol[c] / n for c in CONSTRAINT_NAMES if viol[c]},
        "sole_violator_prob": {c: sole[c] / n for c in CONSTRAINT_NAMES if sole[c]},
    }
    out["violating_constraint_prob"] = dict(
        sorted(out["violating_constraint_prob"].items(), key=lambda kv: -kv[1]))
    out["sole_violator_prob"] = dict(
        sorted(out["sole_violator_prob"].items(), key=lambda kv: -kv[1]))
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print(f"\n=== LQG SURVIVAL over joint coeff x prefactor space (n={n}) ===")
    print(f"  LQG full-stack FEASIBLE in {out['lqg_feasible_fraction']*100:.2f}% of the box")
    print(f"\n  constraints excluding LQG (prob it violates):")
    for c, p in list(out["violating_constraint_prob"].items())[:8]:
        s = out["sole_violator_prob"].get(c, 0.0)
        print(f"      {c:<32} {p*100:5.1f}%   (sole excluder {s*100:4.1f}%)")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
