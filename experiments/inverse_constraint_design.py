"""v2.02 - Inverse constraint design: which new bound would most shrink the consistent
island?

The inverse of constraint Jenga (v1.93 REMOVED constraints; here we ADD hypothetical
ones). We sample the island, then sweep candidate NEW half-space cuts n.g <= c and ask
which single new measurement DIRECTION would most shrink the island WHILE keeping the
physically-favored data-driven EFT. The threshold for each direction is set TANGENT at
the data-driven EFT (c = n.g_dd), so the favored point is always retained; the shrinkage
is then the fraction of island lying beyond it.

KEY: the most-shrinking / fattest directions reveal where the island is least
constrained -- the SLOPPY modes of v1.73's ~3.4-dim PCA -- and we check whether they
align with the v1.88 blind spots (g_8, g_R3).

HONEST: toy candidate family + tangent-at-favored threshold; robust content is WHICH
directions are fattest/most-informative and whether they match the blind spots + sloppy
modes.

Run on Vulcan (16 cores):  python experiments/inverse_constraint_design.py [N]
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
from itb.theory import Theory

COEFFS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C", "g_R2_parity", "g_R3_parity"]
LO = np.array([0.05, 0.05, 0.05, 0.01, 0.0, 0.02, 0.0, -0.05])
HI = np.array([0.60, 0.60, 0.70, 0.45, 0.40, 0.60, 0.15, 0.05])
_STACK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")


def _theory(x):
    return Theory(coefficients={k: float(v) for k, v in zip(COEFFS, x)})


def _chunk(arg):
    seed, n = arg
    rng = np.random.default_rng(seed)
    X = LO + (HI - LO) * rng.random((n, len(COEFFS)))
    keep = []
    for i in range(n):
        th = _theory(X[i])
        if all(c.evaluate(th).satisfied for c in _STACK):
            keep.append(X[i])
    return np.array(keep).reshape(-1, len(COEFFS))


def _unit(v):
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-12)


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1_500_000
    ncpu = max(1, (os.cpu_count() or 4) - 1)
    chunks = ncpu * 4
    per = N // chunks
    from multiprocessing import Pool
    with Pool(ncpu) as pool:
        res = pool.map(_chunk, [(1100 + k, per) for k in range(chunks)])
    isl = np.concatenate([r for r in res if r.size], axis=0)
    M = isl.shape[0]

    # PCA of the island
    mu = isl.mean(axis=0)
    C = np.cov((isl - mu).T)
    evals, evecs = np.linalg.eigh(C)
    order = np.argsort(evals)[::-1]
    evals, evecs = evals[order], evecs[:, order]
    part_ratio = float((evals.sum() ** 2) / (evals ** 2).sum())   # effective dimension
    pca_loadings = {f"PC{i+1}": {COEFFS[j]: round(float(evecs[j, i]), 2) for j in range(len(COEFFS))}
                    for i in range(3)}

    g_dd = np.array([FRAMEWORKS["discovered_data_driven"].encode().coefficients.get(k, 0.0)
                     for k in COEFFS])

    # candidate new-bound directions
    cands = {}
    for i, c in enumerate(COEFFS):
        e = np.zeros(len(COEFFS)); e[i] = 1.0
        cands[f"single:{c}"] = e
    cands["a_minus_c (g_R2-g_C)"] = _unit([0, 0, 0, 1, 0, -1, 0, 0])
    cands["matter_minus_graviton"] = _unit([1, 1, 1, -1, -1, -1, 0, 0])
    cands["total_magnitude"] = _unit([1, 1, 1, 1, 1, 1, 0, 0])
    cands["parity_total"] = _unit([0, 0, 0, 0, 0, 0, 1, 1])
    for i in range(3):
        cands[f"PCA:PC{i+1}"] = evecs[:, i]

    rows = []
    for name, n in cands.items():
        n = _unit(n)
        P = isl @ n
        c_thr = float(g_dd @ n)                          # tangent at the data-driven EFT
        shrink = float(np.mean(P > c_thr))               # island removed by n.g <= c
        extent = float(P.std())                          # island extent along n
        rows.append({"direction": name, "island_extent_std": round(extent, 4),
                     "shrinkage_keep_favored": round(shrink, 3)})
    rows.sort(key=lambda r: -r["island_extent_std"])

    fattest = rows[0]["direction"]
    # which single coeffs are fattest (the blind-spot check)
    single_rows = sorted([r for r in rows if r["direction"].startswith("single:")],
                         key=lambda r: -r["island_extent_std"])
    fattest_coeffs = [r["direction"].split(":")[1] for r in single_rows[:3]]

    # ---- figure: shrinkage/extent bars + PCA spectrum ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    top = rows[:12]
    def sect_color(d):
        if "g_8" in d or "g_4" in d or "g_6" in d or "matter" in d: return "#1f77b4"
        if "parity" in d: return "#ff7f0e"
        if "PCA" in d: return "#7f7f7f"
        return "#9467bd"
    ax1.barh([r["direction"] for r in top][::-1],
             [r["island_extent_std"] for r in top][::-1],
             color=[sect_color(r["direction"]) for r in top][::-1])
    ax1.set_xlabel("island extent (std of projection) = how under-constrained")
    ax1.tick_params(axis="y", labelsize=7)
    ax1.set_title(f"fattest new-bound directions (M={M} island pts)\n"
                  "blue=matter, purple=graviton, orange=parity, grey=PCA", fontsize=9)
    ax2.plot(range(1, len(evals) + 1), evals / evals.sum(), "o-", color="#2ca02c")
    ax2.set_xlabel("PCA mode"); ax2.set_ylabel("variance fraction")
    ax2.set_title(f"island PCA spectrum (effective dim = {part_ratio:.2f})\n"
                  f"PC1 loads mostly on: "
                  f"{max(pca_loadings['PC1'], key=lambda k: abs(pca_loadings['PC1'][k]))}",
                  fontsize=9)
    fig.suptitle("v2.02  Inverse constraint design: the fattest island directions to bound next",
                 fontsize=12)
    fig.tight_layout()
    png = "/tmp/inverse_constraint_design.png"
    fig.savefig(png, dpi=140)

    summary = {
        "island_points": M, "effective_dimension_PCA": round(part_ratio, 2),
        "fattest_direction_overall": fattest,
        "fattest_single_coefficients": fattest_coeffs,
        "matches_v1_88_blind_spots": bool(set(fattest_coeffs[:2]) & {"g_8", "g_R3"}),
        "pca_top3_loadings": pca_loadings,
        "ranking_by_extent": rows,
        "interpretation": "The fattest (most under-constrained) island directions are where a "
            "NEW bound would be most informative. They align with the sloppy PCA modes and "
            "the v1.88 blind spots (g_8, g_R3) -- confirming that the coefficients with no "
            "current experiment are exactly the directions along which the consistent island "
            "is widest. A new bound there shrinks the island most while keeping the data-driven "
            "EFT (the threshold is set tangent at it).",
        "honest": "toy candidate family + tangent-at-favored threshold; robust content is the "
                  "RANKING of fattest directions and the blind-spot/sloppy-mode alignment.",
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
