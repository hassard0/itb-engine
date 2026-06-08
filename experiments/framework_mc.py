"""Framework-coefficient uncertainty MC (v1.25).

The v1.23-24 audits perturbed the CONSTRAINT prefactors. But the engine's
FRAMEWORK coefficients are equally toy ("representative, not derived" —
2026-05-08 honest synthesis). This harness audits that other half: it perturbs
each framework's Wilson coefficients over relative-uncertainty ranges and asks
whether the v1.24 verdicts survive — in particular:

  * Does LQG stay excluded, and by what?
  * Does asymptotic safety stay the robust survivor?
  * The decisive variable: LQG's cubic coupling g_R3. The forward-positivity
    exclusion of LQG hinges on g_R3 ~ g_R2 (ratio ~1). If spin-foam dynamics
    actually give g_R3 parametrically smaller (ratio >1.2), LQG PASSES. So we
    scan LQG's g_R3 explicitly and report P(excluded) vs the assumed ratio.

Evaluated against the corrected v1.24 stack (convex-hull RFC + forward
positivity + matter s^3), canonical prefactors.

Usage:
    python -m experiments.framework_mc --n 200000 --workers 16 --rel 0.30
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
from experiments.stack import build_stack, frameworks

# nominal framework coefficients (from the encoders)
NOMINAL = {fw.name: dict(fw.encode().coefficients) for fw in frameworks()}
# corrected v1.24 stack; rebuilt in main() if --bnossw-mean given (fork-inherited)
CONSTRAINTS = build_stack(rfc_form="convex_hull")
CONSTRAINT_NAMES = [c.name for c in CONSTRAINTS]

# Per-framework uncertainty model, from Dr. M.'s pinned-vs-representative
# assessment (Pluto consult, 2026-06-08):
#   - PINNED coefficients are tightly determined -> small relative spread.
#   - REPRESENTATIVE coefficients are truncation/scheme dependent -> wide.
#   - g_R3 is modelled physically as ratio * g_R2 with ratio in the literature
#     range Dr. M. gave (spin-foam 1/j suppression => g_R3 << g_R2).
SIGMA_PINNED = 0.10
SIGMA_REPR = 0.40
SPEC = {
    "string_tree_eft": {"pinned": {"g_4", "g_6", "g_8", "g_R2", "g_R3"},
                        "gr3_ratio": None},
    "asymptotic_safety": {"pinned": {"g_4", "g_R2"},
                          "gr3_ratio": (0.10, 0.40)},
    "lqg_induced": {"pinned": {"g_4"},
                    "gr3_ratio": (0.10, 0.70)},
    "cdt": {"pinned": {"g_4"},
            "gr3_ratio": (0.10, 0.55)},
}
_REL = None  # if set (CLI), overrides SPEC with a flat ±_REL on every coeff


def _perturb(name, rng, rel=None):
    nom = NOMINAL[name]
    spec = SPEC[name]
    out = {}
    for k, v in nom.items():
        if v == 0.0:
            out[k] = 0.0  # preserve exact zeros (parity structure)
            continue
        if rel is not None:
            out[k] = v * (1.0 + rng.uniform(-rel, rel))
        else:
            sig = SIGMA_PINNED if k in spec["pinned"] else SIGMA_REPR
            out[k] = v * (1.0 + rng.uniform(-sig, sig))
    # physical g_R3 model: ratio * g_R2 over the literature range
    if rel is None and spec["gr3_ratio"] is not None and "g_R3" in out:
        lo, hi = spec["gr3_ratio"]
        out["g_R3"] = out["g_R2"] * rng.uniform(lo, hi)
    return out


def _worker(args):
    name, seed = args
    rng = np.random.default_rng(seed)
    coeffs = _perturb(name, rng, _REL)
    rep = check(Theory(coefficients=coeffs, name=name), CONSTRAINTS)
    violated = [r.constraint_name for r in rep.results if not r.satisfied]
    return name, rep.feasible, violated


def framework_uncertainty_mc(n, workers, rel, pool):
    names = [fw.name for fw in frameworks() if fw.name != "pure_gr"]
    args = []
    base = 1000
    for name in names:
        for i in range(n):
            args.append((name, base))
            base += 1
    results = pool.map(_worker, args, chunksize=max(1, len(args) // (workers * 8)))
    excl = {nm: 0 for nm in names}
    mat = {nm: Counter() for nm in names}
    tot = {nm: 0 for nm in names}
    for name, feasible, violated in results:
        tot[name] += 1
        if not feasible:
            excl[name] += 1
        for c in violated:
            mat[name][c] += 1
    summary = {}
    for nm in names:
        summary[nm] = {
            "exclusion_fraction": excl[nm] / tot[nm],
            "constraint_exclusion_prob": dict(sorted(
                ((c, mat[nm][c] / tot[nm]) for c in CONSTRAINT_NAMES if mat[nm][c] > 0),
                key=lambda kv: -kv[1])),
        }
    return {"n_per_framework": n, "rel": rel, "per_framework": summary}


def lqg_gr3_scan(steps=37):
    """Decisive scan: vary LQG's g_R3 (hence the g_R2/g_R3 ratio) and report
    full-stack feasibility + forward-positivity margin. Others at nominal."""
    from itb.constraints.graviton_forward_positivity import GravitonForwardPositivity
    nom = dict(NOMINAL["lqg_induced"])
    gR2 = nom["g_R2"]
    gr3_values = np.linspace(0.03, 0.33, steps)
    rows = []
    fwd = GravitonForwardPositivity(c=1.2)
    for gr3 in gr3_values:
        coeffs = dict(nom)
        coeffs["g_R3"] = float(gr3)
        t = Theory(coefficients=coeffs, name="lqg_induced")
        feasible = check(t, CONSTRAINTS).feasible
        rows.append({
            "g_R3": float(gr3),
            "ratio_gR2_over_gR3": float(gR2 / gr3),
            "fwd_margin": float(fwd.evaluate(t).margin),
            "fwd_satisfied": bool(fwd.evaluate(t).satisfied),
            "fullstack_feasible": bool(feasible),
        })
    return {"g_R2": gR2, "scan": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--rel", type=float, default=None,
                    help="flat ±rel on every coeff (overrides Dr. M.'s pinned/repr model)")
    ap.add_argument("--bnossw-mean", default="harmonic", choices=["harmonic", "geometric"])
    ap.add_argument("--out", default="experiments/out_framework_mc.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    global _REL, CONSTRAINTS, CONSTRAINT_NAMES
    _REL = args.rel
    if args.bnossw_mean != "harmonic":
        CONSTRAINTS = build_stack(rfc_form="convex_hull", bnossw_mean=args.bnossw_mean)
        CONSTRAINT_NAMES = [c.name for c in CONSTRAINTS]
    model = f"flat ±{args.rel*100:.0f}%" if args.rel is not None else "Dr.M pinned/representative + physical g_R3 ratio"
    print(f"workers={args.workers}  n_per_framework={args.n}  model=[{model}]  "
          f"stack={len(CONSTRAINTS)} constraints (corrected v1.24)")

    scan = lqg_gr3_scan()
    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        mc = framework_uncertainty_mc(args.n, args.workers, args.rel, pool)
        print(f"framework MC done ({time.time()-t0:.1f}s)")

    result = {"framework_mc": mc, "lqg_gr3_scan": scan}
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n=== Framework-coefficient uncertainty [{model}] ===")
    for nm, d in mc["per_framework"].items():
        top = list(d["constraint_exclusion_prob"].items())[:3]
        tops = ", ".join(f"{c}={p*100:.0f}%" for c, p in top)
        print(f"  {nm:<22} excluded {d['exclusion_fraction']*100:5.1f}%   top: {tops}")

    print("\n=== LQG g_R3 scan (decisive): when does LQG escape forward positivity? ===")
    print(f"  (LQG g_R2 = {scan['g_R2']}; canonical g_R3 = {NOMINAL['lqg_induced']['g_R3']})")
    print(f"  {'g_R3':>6} {'g_R2/g_R3':>10} {'fwd_margin':>11} {'fullstack_feasible':>18}")
    for r in scan["scan"]:
        if abs(r["g_R3"] - round(r["g_R3"], 2)) < 0.005 or r["g_R3"] in (0.10, 0.36):
            mark = "  <- escapes fwd-pos" if r["fwd_satisfied"] else ""
            print(f"  {r['g_R3']:>6.2f} {r['ratio_gR2_over_gR3']:>10.2f} "
                  f"{r['fwd_margin']:>11.3f} {str(r['fullstack_feasible']):>18}{mark}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
