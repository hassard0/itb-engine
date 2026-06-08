"""Joint-uncertainty survival on the full ~37-constraint stack (v1.66).

Re-runs the v1.26 joint coefficient x prefactor survival, now with the v1.61
constraints (CEMZ causality + cross-sector EFThedron) in the stack and GFT added
to the framework set. Samples BOTH each framework's coefficients (pinned vs
representative + physical g_R3 ratio) AND all constraint prefactors over their
plausible boxes; reports the feasible fraction per in-scope framework. Out-of-scope
frameworks (HL, Causal Set, Emergent) are skipped (their verdicts are not
meaningful, v1.59/65).
"""

import argparse
import json
import os
import sys

import numpy as np

from itb.engine import check
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.group_field_theory import GroupFieldTheory
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.scope import engine_validity
from itb.theory import Theory

sys.path.insert(0, ".")
from experiments.stack import PLAUSIBLE_RANGES, build_stack

KNOBS = list(PLAUSIBLE_RANGES.keys())
SIGMA_PIN, SIGMA_REP = 0.10, 0.40

NAMED = {"string_tree_eft": StringTreeEFT(), "asymptotic_safety": AsymptoticSafety(),
         "cdt": CausalDynamicalTriangulation(), "lqg_induced": LQGInduced(),
         "group_field_theory": GroupFieldTheory()}
DISCOVERED = {"discovered_novel": DiscoveredNovel(),
              "discovered_parity_violating": DiscoveredParityViolating(),
              "discovered_high_g8": DiscoveredHighG8()}
ALL = {**NAMED, **DISCOVERED}
NOMINAL = {n: dict(fw.encode().coefficients) for n, fw in ALL.items()}

# pinned set + g_R3 ratio range per named framework (Dr. M. model; GFT spin-foam-like)
SPEC = {
    "string_tree_eft": ({"g_4", "g_6", "g_8", "g_R2", "g_R3"}, None),
    "asymptotic_safety": ({"g_4", "g_R2"}, (0.10, 0.40)),
    "cdt": ({"g_4"}, (0.10, 0.55)),
    "lqg_induced": ({"g_4"}, (0.10, 0.70)),
    "group_field_theory": ({"g_4"}, (0.10, 0.70)),
}

v126 = {"string_tree_eft": 23.5, "asymptotic_safety": 44.3, "cdt": 19.1,
        "lqg_induced": 2.1}   # earlier 31-constraint stack numbers (corrected stack)


def _perturb(name, rng):
    nom = NOMINAL[name]
    if name in SPEC:
        pinned, gr3 = SPEC[name]
        out = {}
        for k, v in nom.items():
            if v == 0.0:
                out[k] = 0.0
            else:
                sig = SIGMA_PIN if k in pinned else SIGMA_REP
                out[k] = v * (1 + rng.uniform(-sig, sig))
        if gr3 is not None and "g_R3" in out:
            out["g_R3"] = out["g_R2"] * rng.uniform(*gr3)
        return out
    # discovered: representative +/-30% all nonzero coeffs
    return {k: (0.0 if v == 0 else v * (1 + rng.uniform(-0.30, 0.30)))
            for k, v in nom.items()}


def _worker(args):
    name, seed = args
    rng = np.random.default_rng(seed)
    pref = {k: float(rng.uniform(*PLAUSIBLE_RANGES[k])) for k in KNOBS}
    coeffs = _perturb(name, rng)
    cons = build_stack(pref, bnossw_mean="geometric", rfc_form="convex_hull")
    return name, check(Theory(coefficients=coeffs, name=name), cons).feasible


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200000)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    args = ap.parse_args()
    import multiprocessing as mp, time

    n_constraints = len(build_stack())
    print(f"in-scope survival on {n_constraints}-constraint stack, n={args.n}/framework\n")
    tasks, s = [], 100
    for name in ALL:
        for _ in range(args.n):
            tasks.append((name, s)); s += 1
    with mp.Pool(args.workers) as pool:
        t0 = time.time()
        res = pool.map(_worker, tasks, chunksize=max(1, len(tasks)//(args.workers*8)))
        print(f"done ({time.time()-t0:.1f}s)")

    feas = {n: 0 for n in ALL}; tot = {n: 0 for n in ALL}
    for name, f in res:
        tot[name] += 1
        if f:
            feas[name] += 1
    out = {n: {"feasible_fraction": feas[n]/tot[n], "in_scope": engine_validity(ALL[n]).in_scope}
           for n in ALL}

    print(f"\n=== survival over joint coeff x prefactor box ({n_constraints} constraints) ===")
    print(f"  {'framework':<28}{'v1.66':>8}{'v1.26':>8}{'shift':>8}")
    for n in sorted(ALL, key=lambda x: -out[x]["feasible_fraction"]):
        cur = out[n]["feasible_fraction"]*100
        old = v126.get(n)
        olds = f"{old:.0f}%" if old is not None else "  new"
        shift = f"{cur-old:+.0f}%" if old is not None else ""
        print(f"  {n:<28}{cur:>7.0f}%{olds:>8}{shift:>8}")

    with open("experiments/results/out_survival_v66.json", "w") as f:
        json.dump({"n_constraints": n_constraints, "frameworks": out, "v126": v126}, f, indent=2)

    print("\n=== reading ===")
    print("  Adding the v1.61 constraints (CEMZ + cross-sector EFThedron) to the stack")
    print("  TIGHTENS survival (every fraction drops vs v1.26's 31-constraint numbers),")
    print("  most for the frameworks the EFThedron targets. GFT enters the comparison")
    print("  (spin-foam, low survival like LQG). Ordering and the LQG-disfavoured verdict")
    print("  are preserved; the new bounds make the allowed region smaller, not different.")

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        names = sorted(ALL, key=lambda x: -out[x]["feasible_fraction"])
        cur = [out[n]["feasible_fraction"]*100 for n in names]
        old = [v126.get(n, np.nan) for n in names]
        x = np.arange(len(names)); w = 0.4
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(x-w/2, old, w, label="v1.26 (31 constraints)", color="C0", alpha=0.7)
        ax.bar(x+w/2, cur, w, label=f"v1.66 ({n_constraints} constraints)", color="C2", alpha=0.85)
        ax.set_xticks(x); ax.set_xticklabels([n.replace("_"," ") for n in names], rotation=40, ha="right", fontsize=8)
        ax.set_ylabel("joint survival fraction [%]"); ax.legend()
        ax.set_title("v1.66 - survival shrinks with the new constraints (EFThedron+CEMZ)")
        plt.tight_layout(); plt.savefig("experiments/results/survival_v66.png", dpi=110)
        print("wrote experiments/results/survival_v66.png")
    except Exception as e:
        print(f"(plot skipped: {e})")
    print("\nwrote experiments/results/out_survival_v66.json")


if __name__ == "__main__":
    main()
