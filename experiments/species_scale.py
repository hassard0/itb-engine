"""v1.96 - The species scale: tying the EFT cutoff to a tower of states.

We added a SpeciesScaleBound (Dvali species scale: large curvature couplings -> light
tower -> low gravity cutoff -> a bound on the coefficients). Here we measure whether it
carries INDEPENDENT information: its irreplaceability (island growth if removed), which
frameworks it affects, and its overlap with the complexity cutoff and distance
conjecture (Dr. M.: same FORM as complexity, distinct content).

Run on Vulcan (16 cores):  python experiments/species_scale.py [N]
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
from itb.constraints.species_scale import SpeciesScaleBound
from itb.theory import Theory

COEFFS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C", "g_R2_parity", "g_R3_parity"]
LO = np.array([0.05, 0.05, 0.05, 0.01, 0.0, 0.02, 0.0, -0.05])
HI = np.array([0.60, 0.60, 0.70, 0.45, 0.40, 0.60, 0.15, 0.05])

_STACK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
_NAMES = [c.name for c in _STACK]
_SP = _NAMES.index("species_scale_bound")
_CX = _NAMES.index("complexity_cutoff")
_DC = _NAMES.index("swampland_distance_conjecture")


def _theory(x):
    return Theory(coefficients={k: float(v) for k, v in zip(COEFFS, x)})


def _chunk(arg):
    seed, n = arg
    rng = np.random.default_rng(seed)
    X = LO + (HI - LO) * rng.random((n, len(COEFFS)))
    # counts: full island, island-without-species, and overlap stats
    full = wo_species = sp_fail = sp_fail_also_cx = sp_fail_also_dc = 0
    for i in range(n):
        th = _theory(X[i])
        sat = [c.evaluate(th).satisfied for c in _STACK]
        all_but_sp = all(sat[j] for j in range(len(sat)) if j != _SP)
        if all(sat):
            full += 1
        if all_but_sp:
            wo_species += 1
        if not sat[_SP]:
            sp_fail += 1
            if not sat[_CX]:
                sp_fail_also_cx += 1
            if not sat[_DC]:
                sp_fail_also_dc += 1
    return full, wo_species, sp_fail, sp_fail_also_cx, sp_fail_also_dc, n


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    ncpu = max(1, (os.cpu_count() or 4) - 1)
    chunks = ncpu * 4
    per = N // chunks
    from multiprocessing import Pool
    with Pool(ncpu) as pool:
        res = pool.map(_chunk, [(600 + k, per) for k in range(chunks)])
    full = sum(r[0] for r in res); wo = sum(r[1] for r in res)
    spf = sum(r[2] for r in res); spf_cx = sum(r[3] for r in res); spf_dc = sum(r[4] for r in res)
    total = sum(r[5] for r in res)

    growth = (wo / full - 1.0) if full else float("inf")
    redundant = growth < 0.01
    # of species-failing points, what fraction ALSO fail complexity (overlap)
    overlap_cx = (spf_cx / spf) if spf else 0.0
    overlap_dc = (spf_dc / spf) if spf else 0.0

    # frameworks: species number and verdict
    sb = SpeciesScaleBound()
    fw_rows = []
    for name, fw in FRAMEWORKS.items():
        th = fw.encode()
        N_sp = sb._species(th)
        excl = not sb.evaluate(th).satisfied
        fw_rows.append({"framework": name, "N_species": round(N_sp, 3),
                        "species_excluded": bool(excl)})
    fw_rows.sort(key=lambda r: -r["N_species"])
    excluded_by_species = [r["framework"] for r in fw_rows if r["species_excluded"]]

    # ---- figure: species number per framework + the bound ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    names = [r["framework"] for r in fw_rows]
    Ns = [r["N_species"] for r in fw_rows]
    cols = ["#d62728" if r["species_excluded"] else "#1f77b4" for r in fw_rows]
    ax1.barh(names[::-1], Ns[::-1], color=cols[::-1])
    ax1.axvline(sb.N_max, color="black", ls="--", lw=1.5, label=f"N_max = {sb.N_max}")
    ax1.set_xlabel("species number N = 1 + 2(|g_R2|+|g_C|+|g_R3|)")
    ax1.set_title("species count per framework (red = excluded by species scale)", fontsize=9)
    ax1.legend(fontsize=8)
    # overlap pie-ish bar
    ax2.bar(["fail species\n& complexity", "fail species\n& distance", "fail species\nonly"],
            [overlap_cx * 100, overlap_dc * 100,
             max(0, 100 - overlap_cx * 100 - overlap_dc * 100)],
            color=["#9467bd", "#ff7f0e", "#2ca02c"])
    ax2.set_ylabel("% of species-failing points")
    ax2.set_title(f"species-scale irreplaceability: island growth {100*growth:.1f}% if removed\n"
                  f"{'REDUNDANT' if redundant else 'carries content'} "
                  f"({overlap_cx*100:.0f}% also fail complexity)", fontsize=9)
    fig.suptitle("v1.96  The species scale: a new swampland constraint", fontsize=12)
    fig.tight_layout()
    png = "/tmp/species_scale.png"
    fig.savefig(png, dpi=140)

    summary = {
        "samples": total, "island_with_species": full, "island_without_species": wo,
        "irreplaceability_island_growth_pct": round(100 * growth, 1),
        "redundant_in_this_basis": bool(redundant),
        "of_species_failures_also_fail_complexity_pct": round(100 * overlap_cx, 1),
        "of_species_failures_also_fail_distance_pct": round(100 * overlap_dc, 1),
        "frameworks_excluded_by_species_alone": excluded_by_species,
        "framework_species_numbers": fw_rows,
        "interpretation": ("The species-scale bound " +
            ("is REDUNDANT in this basis (its exclusions are already covered by the other "
             "constraints, esp. complexity) -- two distinct swampland principles collapse to "
             "the same coefficient bound here" if redundant else
             "carries INDEPENDENT content (it grows the island when removed) -- a genuinely "
             "new load-bearing swampland bound") + "."),
        "honest": "toy species-counting map (N=1+2*curvature-coupling-sum, N_max=3); robust "
            "content is the structure (large curvature couplings -> light tower -> low "
            "species cutoff) and whether it adds information beyond complexity.",
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
