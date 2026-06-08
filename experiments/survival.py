"""Comparative survival over joint coefficient x prefactor space (v1.26 capstone).

For every framework, sample BOTH its Wilson coefficients (Dr. M.'s
pinned/representative model + physical g_R3 ratio, reused from framework_mc) AND
all constraint prefactors over their plausible ranges, then measure the fraction
of the joint space in which the framework is full-stack feasible. Uses the
robust geometric-BNOSSW form and the corrected convex-hull RFC.

This is the single most honest robustness number the engine can produce: it
admits uncertainty in BOTH halves of the toy-ness at once.

Usage:
    python -m experiments.survival --n 400000 --workers 16
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
from experiments.framework_mc import NOMINAL, SPEC

KNOBS = list(CANONICAL.keys())
CONSTRAINT_NAMES = [c.name for c in build_stack()]
_FW_NAMES = [fw.name for fw in frameworks() if fw.name != "pure_gr"]
SIGMA_PINNED, SIGMA_REPR = 0.10, 0.40


def _perturb(name, rng):
    nom, spec = NOMINAL[name], SPEC[name]
    out = {}
    for k, v in nom.items():
        if v == 0.0:
            out[k] = 0.0
        else:
            sig = SIGMA_PINNED if k in spec["pinned"] else SIGMA_REPR
            out[k] = v * (1.0 + rng.uniform(-sig, sig))
    if spec["gr3_ratio"] is not None and "g_R3" in out:
        lo, hi = spec["gr3_ratio"]
        out["g_R3"] = out["g_R2"] * rng.uniform(lo, hi)
    return out


def _worker(args):
    name, seed = args
    rng = np.random.default_rng(seed)
    pref = {k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in KNOBS}
    coeffs = _perturb(name, rng)
    constraints = build_stack(pref, bnossw_mean="geometric", rfc_form="convex_hull")
    rep = check(Theory(coefficients=coeffs, name=name), constraints)
    violated = tuple(r.constraint_name for r in rep.results if not r.satisfied)
    return name, rep.feasible, violated


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400000)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="experiments/out_survival.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    print(f"workers={args.workers}  n={args.n}/framework  "
          f"joint coeff x prefactor, geometric BNOSSW + convex-hull RFC")

    tasks = []
    s = 90000
    for name in _FW_NAMES:
        for _ in range(args.n):
            tasks.append((name, s)); s += 1

    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        results = pool.map(_worker, tasks, chunksize=max(1, len(tasks) // (args.workers * 8)))
        print(f"done ({time.time()-t0:.1f}s)")

    feas = {nm: 0 for nm in _FW_NAMES}
    tot = {nm: 0 for nm in _FW_NAMES}
    viol = {nm: Counter() for nm in _FW_NAMES}
    for name, f, v in results:
        tot[name] += 1
        if f:
            feas[name] += 1
        else:
            for c in v:
                viol[name][c] += 1

    summary = {}
    for nm in _FW_NAMES:
        summary[nm] = {
            "feasible_fraction": feas[nm] / tot[nm],
            "top_excluders": [(c, viol[nm][c] / tot[nm]) for c in
                              [c for c, _ in viol[nm].most_common(5)]],
        }
    with open(args.out, "w") as f:
        json.dump({"n": args.n, "per_framework": summary}, f, indent=2)

    print(f"\n=== SURVIVAL over joint coeff x prefactor space ({args.n}/framework) ===")
    for nm in sorted(_FW_NAMES, key=lambda x: -summary[x]["feasible_fraction"]):
        d = summary[nm]
        tops = ", ".join(f"{c}={p*100:.0f}%" for c, p in d["top_excluders"][:3])
        print(f"  {nm:<22} FEASIBLE {d['feasible_fraction']*100:6.2f}%   top excluders: {tops}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
