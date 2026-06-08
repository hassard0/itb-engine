"""Joint prefactor-realism robustness harness (parallel).

The engine's verdicts ("LQG fails", "intersection non-empty") are computed at
ONE choice of six O(1) placeholder prefactors. We only know those "house
numbers" to within ~a factor of two. This harness asks the honest question:

  Over the whole plausible 6-D prefactor box, what FRACTION of parameter
  space yields each verdict?

Two analyses:

  1. marginal_sweeps  -- vary one prefactor across its range with the other
     five held canonical, against the FULL stack. (The existing
     prefactor_sensitivity tool only tests against ~4 constraints; this tests
     against all 31.) Answers: which verdicts are knife-edge?

  2. joint_mc         -- Monte-Carlo over the full 6-D box. Per framework:
     exclusion fraction + which constraint binds. Plus an intersection-
     emptiness sub-sample. This is the embarrassingly-parallel part that uses
     all of Vulcan's cores.

Usage:
    python -m experiments.realism_mc --n 200000 --n-intersection 2000 --workers 16
"""

import argparse
import json
import os
import sys
from collections import Counter

import numpy as np

from itb.engine import check
from itb.intersection_search import search_intersection

sys.path.insert(0, ".")
from experiments.stack import (
    CANONICAL,
    INTERSECTION_INITIAL,
    PLAUSIBLE_RANGES,
    build_stack,
    frameworks,
)

KNOBS = list(CANONICAL.keys())
_FW_NAMES = [fw.name for fw in frameworks()]
CONSTRAINT_NAMES = [c.name for c in build_stack()]
_DROP: set = set()  # constraint names to remove (leave-one-out); fork-inherited
_RFC_FORM: str = "matter_product"  # fork-inherited


def _stack(pref, mean):
    return [c for c in build_stack(pref, bnossw_mean=mean, rfc_form=_RFC_FORM)
            if c.name not in _DROP]


def _sample(rng, n, prior):
    """Draw n points in the 6-D prefactor box under uniform or log-uniform prior."""
    keys = KNOBS
    lo = np.array([PLAUSIBLE_RANGES[k][0] for k in keys])
    hi = np.array([PLAUSIBLE_RANGES[k][1] for k in keys])
    if prior == "loguniform":
        return np.exp(rng.uniform(np.log(lo), np.log(hi), size=(n, len(keys))))
    return rng.uniform(lo, hi, size=(n, len(keys)))


# --- worker functions (top-level for multiprocessing picklability) ---------
def _verdicts(args):
    """(prefactor_vector, mean) -> per-framework (feasible, [violated names]).

    We record EVERY violated constraint, not just the single hardest-binding
    one, so the dominant universal excluder (RFC) doesn't mask framework-
    specific exclusions underneath it."""
    vec, mean = args
    pref = dict(zip(KNOBS, vec))
    constraints = _stack(pref, mean)
    out = {}
    for fw in frameworks():
        rep = check(fw.encode(), constraints)
        violated = [r.constraint_name for r in rep.results if not r.satisfied]
        out[fw.name] = (rep.feasible, violated)
    return out


def _intersection(args):
    """(prefactor_vector, mean) -> worst_case_margin of the all-constraint search."""
    vec, mean = args
    pref = dict(zip(KNOBS, vec))
    constraints = _stack(pref, mean)
    res = search_intersection(constraints, INTERSECTION_INITIAL, max_iters=800)
    return res.worst_case_margin


def marginal_sweeps(steps=41, mean="harmonic"):
    """1-D sweep of each knob across its range, others canonical, full stack."""
    results = {}
    for knob in KNOBS:
        lo, hi = PLAUSIBLE_RANGES[knob]
        values = np.linspace(lo, hi, steps)
        per_fw = {name: [] for name in _FW_NAMES}
        for v in values:
            pref = dict(CANONICAL)
            pref[knob] = float(v)
            constraints = _stack(pref, mean)
            for fw in frameworks():
                rep = check(fw.encode(), constraints)
                per_fw[fw.name].append(bool(rep.feasible))
        # locate feasible window per framework
        summary = {}
        for name, feas in per_fw.items():
            feas = np.array(feas)
            transitions = [float(values[i]) for i in range(1, len(feas))
                           if feas[i] != feas[i - 1]]
            summary[name] = {
                "canonical_value": CANONICAL[knob],
                "feasible_fraction": float(feas.mean()),
                "transitions": transitions,
                "feasible_at_canonical": bool(
                    feas[int(np.argmin(np.abs(values - CANONICAL[knob])))]
                ),
            }
        results[knob] = {"range": [lo, hi], "frameworks": summary}
    return results


def joint_mc(n, workers, seed=20260608, mean="harmonic", pool=None, prior="uniform"):
    rng = np.random.default_rng(seed)
    samples = _sample(rng, n, prior)
    args = [(samples[i], mean) for i in range(n)]

    verdicts = pool.map(_verdicts, args, chunksize=max(1, n // (workers * 8)))

    excl_count = {name: 0 for name in _FW_NAMES}
    # per (framework, constraint): how many draws had that constraint violating
    viol_matrix = {name: Counter() for name in _FW_NAMES}
    all_excluded = 0
    for v in verdicts:
        n_excluded = 0
        for name in _FW_NAMES:
            feasible, violated = v[name]
            for cname in violated:
                viol_matrix[name][cname] += 1
            if not feasible:
                excl_count[name] += 1
                n_excluded += 1
        if n_excluded >= len(_FW_NAMES) - 1:  # pure_gr is always feasible
            all_excluded += 1

    summary = {}
    for name in _FW_NAMES:
        # exclusion probability per constraint, AND probability that this
        # constraint is the SOLE excluder (would flip the verdict if removed)
        per_constraint = {c: viol_matrix[name][c] / n for c in CONSTRAINT_NAMES
                          if viol_matrix[name][c] > 0}
        summary[name] = {
            "exclusion_fraction": excl_count[name] / n,
            "constraint_exclusion_prob": dict(
                sorted(per_constraint.items(), key=lambda kv: -kv[1])
            ),
        }
    return {
        "n": n,
        "mean_form": mean,
        "per_framework": summary,
        "fraction_all_nontrivial_excluded": all_excluded / n,
    }


def intersection_mc(n, workers, seed=20260608, mean="harmonic", pool=None, prior="uniform"):
    rng = np.random.default_rng(seed + 1)
    samples = _sample(rng, n, prior)
    args = [(samples[i], mean) for i in range(n)]
    margins = pool.map(_intersection, args, chunksize=max(1, n // (workers * 8)))
    margins = np.array(margins)
    return {
        "n": n,
        "mean_form": mean,
        "nonempty_fraction": float((margins >= 0).mean()),
        "margin_mean": float(margins.mean()),
        "margin_p05": float(np.percentile(margins, 5)),
        "margin_p50": float(np.percentile(margins, 50)),
        "margin_p95": float(np.percentile(margins, 95)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--n-intersection", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--mean", default="harmonic", choices=["harmonic", "geometric"])
    ap.add_argument("--prior", default="uniform", choices=["uniform", "loguniform"])
    ap.add_argument("--rfc-form", default="matter_product",
                    choices=["matter_product", "convex_hull"])
    ap.add_argument("--drop", default="", help="comma-separated constraint names to remove (leave-one-out)")
    ap.add_argument("--out", default="experiments/out_realism_mc.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    global _DROP, _RFC_FORM
    _DROP = set(x for x in args.drop.split(",") if x)
    _RFC_FORM = args.rfc_form

    print(f"workers={args.workers}  n_joint={args.n}  "
          f"n_intersection={args.n_intersection}  mean={args.mean}  "
          f"prior={args.prior}  rfc_form={args.rfc_form}  "
          f"drop={sorted(_DROP) or '—'}")

    t0 = time.time()
    marg = marginal_sweeps(mean=args.mean)
    print(f"marginal sweeps done ({time.time()-t0:.1f}s)")

    with mp.Pool(args.workers) as pool:
        t1 = time.time()
        joint = joint_mc(args.n, args.workers, mean=args.mean, pool=pool,
                         prior=args.prior)
        print(f"joint MC done ({time.time()-t1:.1f}s)")
        t2 = time.time()
        inter = intersection_mc(args.n_intersection, args.workers,
                                mean=args.mean, pool=pool, prior=args.prior)
        print(f"intersection MC done ({time.time()-t2:.1f}s)")

    result = {"marginal": marg, "joint": joint, "intersection": inter,
              "canonical": CANONICAL, "ranges": PLAUSIBLE_RANGES,
              "dropped": sorted(_DROP), "prior": args.prior,
              "rfc_form": args.rfc_form}
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)

    # --- console summary ---
    print("\n=== JOINT MC: exclusion over plausible 6-D prefactor box ===")
    # Identify universal excluders (exclude ~every framework) vs specific ones.
    excluders_by_fw = {name: set(d["constraint_exclusion_prob"].keys())
                       for name, d in joint["per_framework"].items()
                       if name != "pure_gr"}
    universal = set.intersection(*excluders_by_fw.values()) if excluders_by_fw else set()
    print(f"  universal excluders (exclude ALL non-trivial frameworks): "
          f"{sorted(universal) or '—'}")
    for name, d in joint["per_framework"].items():
        if name == "pure_gr":
            continue
        print(f"\n  {name}  (excluded in {d['exclusion_fraction']*100:.1f}% of box)")
        for c, p in list(d["constraint_exclusion_prob"].items())[:6]:
            tag = "" if c in universal else "  <-- framework-specific"
            print(f"      {c:<32} {p*100:5.1f}%{tag}")
    print(f"\n  all non-trivial excluded together: "
          f"{joint['fraction_all_nontrivial_excluded']*100:.1f}%")
    print(f"\n=== INTERSECTION MC ===")
    print(f"  all-constraint intersection non-empty in "
          f"{inter['nonempty_fraction']*100:.1f}% of the box")
    print(f"  worst-case margin p05/p50/p95: "
          f"{inter['margin_p05']:.4f}/{inter['margin_p50']:.4f}/{inter['margin_p95']:.4f}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
