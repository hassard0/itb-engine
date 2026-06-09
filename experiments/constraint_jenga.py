"""v1.93 - Constraint Jenga: which consistency conditions are load-bearing, and
which are redundant?

We pull out each of the 37 theoretical constraints one at a time and measure how much
the consistent island GROWS -- the growth is the constraint's *irreplaceability*. A
constraint whose removal grows the island a lot is load-bearing; one whose removal
changes nothing is redundant (implied by the others). We also track which FRAMEWORKS
flip survival when each constraint is removed -- i.e. which single constraint, if it
turned out WRONG, would most change the verdict on which quantum gravity survives.

Efficiency: sample once, cache each point's per-constraint satisfied-bitmask (uint64);
then 'island volume without constraint c' = count of samples whose bitmask has all bits
set except possibly c = ((bits | (1<<c)) == full_mask).any-count -- an instant bitwise op.

HONEST: redundancy is basis/encoding-dependent -- a constraint redundant in this toy
basis may bite in a fuller one (cf the a-theorem, v1.70). The robust content is the
RANKING of load-bearing vs redundant.

Run on Vulcan (16 cores):  python experiments/constraint_jenga.py [N]
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from stack import build_stack
from itb.predict import FRAMEWORKS
from itb.constraints.base import ConstraintClass
from itb.theory import Theory

COEFFS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C", "g_R2_parity", "g_R3_parity"]
LO = np.array([0.05, 0.05, 0.05, 0.01, 0.0, 0.02, 0.0, -0.05])
HI = np.array([0.60, 0.60, 0.70, 0.45, 0.40, 0.60, 0.15, 0.05])

_STACK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
_NAMES = [c.name for c in _STACK]
_NC = len(_STACK)
_FULL = (np.uint64(1) << np.uint64(_NC)) - np.uint64(1)
_CLASS = {ConstraintClass.A_AMPLITUDE: "A", ConstraintClass.B_INFORMATION: "B",
          ConstraintClass.C_UNIVERSALITY: "C"}


def _theory(x):
    return Theory(coefficients={k: float(v) for k, v in zip(COEFFS, x)})


def _bits_of(th):
    b = np.uint64(0)
    for j, c in enumerate(_STACK):
        if c.evaluate(th).satisfied:
            b |= np.uint64(1) << np.uint64(j)
    return b


def _chunk(arg):
    seed, n = arg
    rng = np.random.default_rng(seed)
    X = LO + (HI - LO) * rng.random((n, len(COEFFS)))
    out = np.zeros(n, dtype=np.uint64)
    for i in range(n):
        out[i] = _bits_of(_theory(X[i]))
    return out


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1_500_000
    ncpu = max(1, (os.cpu_count() or 4) - 1)
    chunks = ncpu * 4
    per = N // chunks
    from multiprocessing import Pool
    with Pool(ncpu) as pool:
        res = pool.map(_chunk, [(400 + k, per) for k in range(chunks)])
    bits = np.concatenate(res)
    total = bits.shape[0]

    V0 = int((bits == _FULL).sum())            # full island count
    # volume without each constraint c
    rows = []
    for j in range(_NC):
        maskj = np.uint64(1) << np.uint64(j)
        Vj = int(((bits | maskj) == _FULL).sum())
        growth = (Vj / V0 - 1.0) if V0 else float("inf")
        rows.append({"constraint": _NAMES[j], "class": _CLASS[_STACK[j].constraint_class],
                     "island_growth_pct": round(100 * growth, 1),
                     "redundant": growth < 0.01})
    rows.sort(key=lambda r: -r["island_growth_pct"])

    load_bearing = [r["constraint"] for r in rows[:6]]
    redundant = [r["constraint"] for r in rows if r["redundant"]]

    # framework survival flips: for each constraint, which frameworks PASS without it
    # but FAIL with it (constraint is a binding reason for that framework's failure)
    fw_bits = {}
    for name, fw in FRAMEWORKS.items():
        fw_bits[name] = _bits_of(fw.encode())
    flips = {}   # constraint -> [frameworks it flips]
    for j in range(_NC):
        maskj = np.uint64(1) << np.uint64(j)
        flipped = []
        for name, fb in fw_bits.items():
            survives_full = (fb == _FULL)
            survives_without = ((fb | maskj) == _FULL)
            if survives_without and not survives_full:
                flipped.append(name)
        if flipped:
            flips[_NAMES[j]] = flipped
    # which single constraint flips the most frameworks
    most_decisive = sorted(flips.items(), key=lambda kv: -len(kv[1]))[:5]

    # ---- figure: irreplaceability bars + flip matrix ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 8),
                                   gridspec_kw={"width_ratios": [1.3, 1]})
    cls_color = {"A": "#1f77b4", "B": "#ff7f0e", "C": "#9467bd"}
    top = rows[:24]
    ax1.barh([r["constraint"] for r in top][::-1],
             [max(r["island_growth_pct"], 0.01) for r in top][::-1],
             color=[cls_color[r["class"]] for r in top][::-1])
    ax1.set_xscale("symlog", linthresh=1)
    ax1.set_xlabel("island growth when removed (%) = irreplaceability")
    ax1.tick_params(axis="y", labelsize=6.5)
    ax1.set_title(f"Constraint irreplaceability (V0={V0}/{total}={100*V0/total:.3f}%)\n"
                  "blue=A amplitude, orange=B info, purple=C universality", fontsize=9)
    # flip matrix
    fw_names = list(FRAMEWORKS)
    flip_con = [c for c in _NAMES if c in flips]
    M = np.zeros((len(flip_con), len(fw_names)))
    for ci, c in enumerate(flip_con):
        for fi, f in enumerate(fw_names):
            if f in flips.get(c, []):
                M[ci, fi] = 1
    if flip_con:
        ax2.imshow(M, aspect="auto", cmap="Reds")
        ax2.set_xticks(range(len(fw_names)))
        ax2.set_xticklabels(fw_names, rotation=90, fontsize=6)
        ax2.set_yticks(range(len(flip_con)))
        ax2.set_yticklabels(flip_con, fontsize=6)
    ax2.set_title("framework survival FLIPS\n(red: framework fails ONLY because of this constraint)",
                  fontsize=9)
    fig.suptitle("v1.93  Constraint Jenga: load-bearing vs redundant consistency conditions",
                 fontsize=12)
    fig.tight_layout()
    png = "/tmp/constraint_jenga.png"
    fig.savefig(png, dpi=140)

    summary = {
        "samples": total, "island_V0": V0, "island_fraction": round(V0 / total, 5),
        "most_load_bearing": [(r["constraint"], r["island_growth_pct"]) for r in rows[:8]],
        "redundant_in_this_basis": redundant,
        "n_redundant": len(redundant),
        "most_decisive_for_frameworks": [{"constraint": k, "flips_frameworks": v}
                                         for k, v in most_decisive],
        "interpretation": "The load-bearing constraints (largest island growth on removal) "
            "do the real exclusion work; the redundant ones are implied by the others in "
            "this toy basis. The single constraint that flips the most framework verdicts is "
            "the one whose correctness most matters for 'which quantum gravity survives'.",
        "honest": "redundancy is basis/encoding-dependent (a redundant constraint here may "
                  "bite in a fuller basis, cf the a-theorem v1.70); robust content is the ranking.",
        "all_constraints": rows,
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
