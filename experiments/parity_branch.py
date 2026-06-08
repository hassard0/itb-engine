"""Characterize the consistent parity-violating branch (v1.31).

v1.27 found that a parity-violating QG can be consistent IF it suppresses its
cubic curvature. This maps that new-physics branch quantitatively:

  1. trade-off curve: for each fixed cubic coupling g_R3, what is the MAXIMUM
     gravitational parity content P = |g_R2_parity| + |g_R3_parity| consistent
     with all constraints? (Other 5 coefficients optimized freely.)
  2. the maximally-parity-violating consistent theory overall, its robustness
     (feasible fraction over the prefactor box), and its observable signature
     (parity-amplitude S/N vs the parity-conserving frameworks).

The binding physics: anomaly inflow caps P^2 by rho*g_4*g_R2, while forward
positivity needs g_R2 >= c*g_R3 — so suppressing g_R3 frees up g_R2 headroom
and hence allowed parity. This experiment makes that trade-off concrete.

Usage:
    python -m experiments.parity_branch --restarts 60 --workers 16
"""

import argparse
import json
import os
import sys

import numpy as np
from scipy.optimize import minimize

from itb.engine import check
from itb.first_disagreement import first_disagreement
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.observables import Observable
from itb.theory import Theory

sys.path.insert(0, ".")
from experiments.stack import PLAUSIBLE_RANGES, build_stack

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
CONSTRAINTS = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
LO = np.array([0.0, 0.0, 0.0, 0.0, 0.0, -0.30, -0.30])
HI = np.array([1.2, 1.0, 1.0, 0.7, 0.7, 0.30, 0.30])
MARGIN = 0.003


def _worst_margin(x):
    rep = check(Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)}), CONSTRAINTS)
    return min((r.margin for r in rep.results), default=0.0)


def _parity(x):
    return abs(x[5]) + abs(x[6])


def _max_parity_at_gr3(args):
    """Maximize parity content with g_R3 fixed; return best feasible (P, x)."""
    gr3, seed = args
    rng = np.random.default_rng(seed)
    best = (0.0, None)
    for _ in range(6):
        x0 = rng.uniform(LO, HI); x0[4] = gr3

        def obj(x):
            xx = np.clip(x, LO, HI); xx[4] = gr3
            pen = np.sum(np.maximum(0, LO - x) + np.maximum(0, x - HI))
            return -_parity(xx) + 50 * (pen + max(0.0, MARGIN - _worst_margin(xx)))

        res = minimize(obj, x0, method="Nelder-Mead",
                       options={"maxiter": 4000, "fatol": 1e-7, "xatol": 1e-7})
        x = np.clip(res.x, LO, HI); x[4] = gr3
        if _worst_margin(x) >= MARGIN:
            p = _parity(x)
            if p > best[0]:
                best = (float(p), [float(v) for v in x])
    return gr3, best[0], best[1]


def _prefactor_robustness(x, n=2000, seed=11):
    rng = np.random.default_rng(seed)
    knobs = list(PLAUSIBLE_RANGES.keys())
    t = Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)})
    ok = sum(check(t, build_stack({k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in knobs},
                                  bnossw_mean="geometric", rfc_form="convex_hull")).feasible
             for _ in range(n))
    return ok / n


class _ParityAmp(Observable):
    def predict(self, theory):
        s = np.linspace(0.2, 1.0, 9)
        return (theory.coefficients.get("g_R2_parity", 0.0) * s ** 2
                + theory.coefficients.get("g_R3_parity", 0.0) * s ** 3)
    def jacobian(self, theory, params):
        return np.zeros((9, len(params)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=60)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="experiments/out_parity_branch.json")
    args = ap.parse_args()

    import multiprocessing as mp
    import time

    gr3_grid = np.round(np.linspace(0.0, 0.40, 17), 3)
    tasks = [(float(g), 4000 + i) for i, g in enumerate(gr3_grid)]
    print(f"workers={args.workers}  mapping max-parity vs g_R3 over {len(gr3_grid)} points")
    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        res = pool.map(_max_parity_at_gr3, tasks)
        print(f"trade-off map done ({time.time()-t0:.1f}s)")

    curve = [{"g_R3": g, "max_parity": p, "theory": x} for g, p, x in sorted(res)]
    # overall max-parity theory
    best = max((c for c in curve if c["theory"]), key=lambda c: c["max_parity"])
    rob = _prefactor_robustness(best["theory"])
    bt = Theory(coefficients={k: float(v) for k, v in zip(KEYS, best["theory"])}, name="parity_max")

    # observable signature: parity-amplitude S/N vs parity-conserving frameworks
    sig = first_disagreement(
        [_NamedTheory("parity_max", bt), _NamedTheory("string", StringTreeEFT().encode()),
         _NamedTheory("AS", AsymptoticSafety().encode()), _NamedTheory("CDT", CausalDynamicalTriangulation().encode())],
        {"parity_amplitude": _ParityAmp()}, sigma=0.005)

    out = {"tradeoff_curve": curve,
           "max_parity_theory": {"coeffs": {k: v for k, v in zip(KEYS, best["theory"])},
                                 "parity": best["max_parity"], "g_R3": best["g_R3"],
                                 "prefactor_robustness": rob},
           "parity_signature_best_pair": {
               "a": sig.best_pair.framework_a, "b": sig.best_pair.framework_b,
               "snr": sig.best_pair.max_signal_to_noise, "signal": sig.best_pair.signal}}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)

    print("\n=== MAX PARITY vs CUBIC COUPLING g_R3 ===")
    print(f"  {'g_R3':>6} {'max|parity|':>12}  {'g_R2/g_R3':>10}")
    for c in curve:
        if c["theory"]:
            r2 = c["theory"][3]
            ratio = r2 / c["g_R3"] if c["g_R3"] > 1e-6 else float('inf')
            print(f"  {c['g_R3']:>6.3f} {c['max_parity']:>12.3f}  "
                  f"{('inf' if ratio==float('inf') else f'{ratio:6.2f}'):>10}")
    print(f"\n  overall max-parity consistent theory: |parity|={best['max_parity']:.3f} "
          f"at g_R3={best['g_R3']:.3f}, robust in {rob*100:.0f}% of prefactor box")
    print(f"  observable signature: parity_amplitude separates parity_max best at "
          f"S/N={sig.best_pair.max_signal_to_noise:.0f}")
    print(f"\nwrote {args.out}")


class _NamedTheory:
    """Adapter so a fixed Theory looks like a Framework for first_disagreement."""
    def __init__(self, name, theory):
        self.name = name; self._t = theory
    def encode(self):
        return self._t


if __name__ == "__main__":
    main()
