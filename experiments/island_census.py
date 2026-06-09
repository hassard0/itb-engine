"""v1.73 - Global survival census: how unique is the consistent-QG island?

Monte-Carlo the full 8-coefficient EFT space against the full corrected stack and
ask three things about the surviving set:
  (1) VOLUME FRACTION  - how rare is a consistent EFT (in the stated box)?
  (2) DIMENSIONALITY    - PCA of survivors: how many principal directions carry
                          the variance? Is the island low-dimensional / sloppy?
  (3) WALLS             - which constraints bind at the survival boundary?
  (4) FRAMEWORKS        - do the 12 QG frameworks sit near the island centre or
                          its edge?

PARITY-EVEN census (STATED ASSUMPTION). We census the parity-even slice
(g_R2_parity = g_R3_parity = 0), where 11 of the 12 frameworks live, for two
reasons: (i) it is the physically dominant region, and (ii) it removes a sampling
artifact - the Distance Conjecture forbids coefficient hierarchies > 20x, and a
uniformly-sampled near-zero parity coefficient against an O(0.5) matter
coefficient trivially violates it, so a full-8D uniform box yields ~0 survivors
for an artifactual reason. Magnitudes are sampled COMPARABLE (no built-in
hierarchy) so the Distance and Complexity walls are satisfiable:
  g_4, g_6      in [0.05, 0.6]      (matter forward-positivity moments)
  g_8           in [0.05, 0.7]
  g_R2          in [0.02, 0.45]     (graviton curvature)
  g_R3          in [0.0, 0.4]
  g_C           in [0.02, 0.6]      (Weyl^2 / c-anomaly; HM wedge acts)
  g_R2_parity = g_R3_parity = 0     (parity-even slice)
The volume fraction is meaningful only relative to this box.

Run on Vulcan (16 cores):  python experiments/island_census.py [N]
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
from itb.holographic_ac import gC_from_gR2
from itb.theory import Theory

COEFFS = ["g_4", "g_6", "g_8", "g_R2", "g_R3",
          "g_R2_parity", "g_R3_parity", "g_C"]
LO = np.array([0.05, 0.05, 0.05, 0.02, 0.0, 0.0, 0.0, 0.02])
HI = np.array([0.60, 0.60, 0.70, 0.45, 0.4, 0.0, 0.0, 0.60])
VARY = HI > LO          # columns with nonzero range (parity cols are constant 0)

# module-global stack (inherited by fork workers on Linux)
_STACK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
_NAMES = [c.name for c in _STACK]


def _eval_chunk(arg):
    """Evaluate a chunk of samples. Returns (survived_mask, binding_idx,
    fail_primary_idx) as lists. binding_idx: for survivors, index of min-margin
    constraint (the nearest wall). fail_primary_idx: for failures, index of the
    most-violated constraint."""
    seed, n = arg
    rng = np.random.default_rng(seed)
    X = LO + (HI - LO) * rng.random((n, len(COEFFS)))
    survived = np.zeros(n, dtype=bool)
    binding = np.full(n, -1, dtype=np.int16)
    fail_primary = np.full(n, -1, dtype=np.int16)
    keep = []
    for i in range(n):
        coeffs = {k: float(v) for k, v in zip(COEFFS, X[i])}
        th = Theory(coefficients=coeffs)
        worst_fail_m, worst_fail_j = np.inf, -1
        min_margin_m, min_margin_j = np.inf, -1
        ok = True
        for j, c in enumerate(_STACK):
            r = c.evaluate(th)
            if r.margin < min_margin_m:
                min_margin_m, min_margin_j = r.margin, j
            if not r.satisfied:
                ok = False
                if r.margin < worst_fail_m:
                    worst_fail_m, worst_fail_j = r.margin, j
        if ok:
            survived[i] = True
            binding[i] = min_margin_j      # nearest wall (smallest positive margin)
            keep.append(X[i])
        else:
            fail_primary[i] = worst_fail_j
    surv_X = np.array(keep) if keep else np.zeros((0, len(COEFFS)))
    return (int(survived.sum()), n,
            np.bincount(binding[binding >= 0], minlength=len(_STACK)),
            np.bincount(fail_primary[fail_primary >= 0], minlength=len(_STACK)),
            surv_X)


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    ncpu = max(1, (os.cpu_count() or 4) - 1)
    chunks = ncpu * 4
    per = N // chunks
    args = [(1000 + k, per) for k in range(chunks)]

    from multiprocessing import Pool
    with Pool(ncpu) as pool:
        results = pool.map(_eval_chunk, args)

    total_surv = sum(r[0] for r in results)
    total_n = sum(r[1] for r in results)
    binding_counts = np.sum([r[2] for r in results], axis=0)
    fail_counts = np.sum([r[3] for r in results], axis=0)
    surv_X = np.vstack([r[4] for r in results if r[4].shape[0] > 0]) \
        if any(r[4].shape[0] for r in results) else np.zeros((0, len(COEFFS)))

    frac = total_surv / total_n
    frac_err = (frac * (1 - frac) / total_n) ** 0.5    # binomial s.e.

    # --- PCA on survivors (standardized), over VARYING coordinates only ---
    vary_names = [COEFFS[i] for i in range(len(COEFFS)) if VARY[i]]
    pca = {}
    if surv_X.shape[0] > 10:
        Xv = surv_X[:, VARY]
        mu = Xv.mean(axis=0)
        sd = Xv.std(axis=0)
        sd_safe = np.where(sd > 0, sd, 1.0)
        Z = (Xv - mu) / sd_safe
        cov = np.cov(Z, rowvar=False)
        evals, evecs = np.linalg.eigh(cov)
        order = np.argsort(evals)[::-1]
        evals = evals[order]; evecs = evecs[:, order]
        evals = np.clip(evals, 0, None)
        cumvar = np.cumsum(evals) / evals.sum()
        d90 = int(np.searchsorted(cumvar, 0.90) + 1)
        d99 = int(np.searchsorted(cumvar, 0.99) + 1)
        pca = {"n_varying_dims": int(VARY.sum()),
               "varying_coords": vary_names,
               "eigenvalues": [round(float(e), 4) for e in evals],
               "cumulative_variance": [round(float(c), 4) for c in cumvar],
               "dims_for_90pct": d90, "dims_for_99pct": d99,
               "participation_ratio": round(float(evals.sum()**2 /
                                                  (evals**2).sum()), 3),
               "top_PC1_loadings": {vary_names[i]: round(float(evecs[i, 0]), 3)
                                    for i in range(len(vary_names))},
               "mean": {k: round(float(m), 4) for k, m in zip(vary_names, mu)},
               "std": {k: round(float(s), 4) for k, s in zip(vary_names, sd)}}

    # --- frameworks: position relative to the island (varying coords) ---
    fw_rows = []
    if surv_X.shape[0] > 10:
        Xv = surv_X[:, VARY]
        mu = Xv.mean(axis=0); sd = Xv.std(axis=0)
        sd_safe = np.where(sd > 0, sd, 1.0)
        for name, fw in FRAMEWORKS.items():
            c = fw.encode().coefficients
            gR2 = c.get("g_R2", 0.0)
            vec = np.array([c.get("g_4", 0.0), c.get("g_6", 0.0), c.get("g_8", 0.0),
                            gR2, c.get("g_R3", 0.0),
                            c.get("g_R2_parity", 0.0), c.get("g_R3_parity", 0.0),
                            gC_from_gR2(gR2)])
            z = (vec[VARY] - mu) / sd_safe
            th = Theory(coefficients={k: float(v) for k, v in zip(COEFFS, vec)})
            feas = all(cc.evaluate(th).satisfied for cc in _STACK)
            fw_rows.append({"framework": name,
                            "z_dist_to_centroid": round(float(np.linalg.norm(z)), 2),
                            "feasible": bool(feas)})
        fw_rows.sort(key=lambda r: r["z_dist_to_centroid"])

    # --- figures: PCA scatter + scree ---
    png = "/tmp/island_census.png"
    if surv_X.shape[0] > 10:
        Xv = surv_X[:, VARY]
        mu = Xv.mean(axis=0); sd = Xv.std(axis=0)
        sd_safe = np.where(sd > 0, sd, 1.0)
        Z = (Xv - mu) / sd_safe
        cov = np.cov(Z, rowvar=False)
        evals, evecs = np.linalg.eigh(cov)
        order = np.argsort(evals)[::-1]
        evecs = evecs[:, order]; evals = np.clip(evals[order], 0, None)
        P = Z @ evecs[:, :2]      # project survivors onto PC1, PC2

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        h = ax1.hist2d(P[:, 0], P[:, 1], bins=80, cmap="viridis")
        fig.colorbar(h[3], ax=ax1, label="survivor density")
        # overlay frameworks
        for name, fw in FRAMEWORKS.items():
            c = fw.encode().coefficients; gR2 = c.get("g_R2", 0.0)
            vec = np.array([c.get("g_4", 0.0), c.get("g_6", 0.0), c.get("g_8", 0.0),
                            gR2, c.get("g_R3", 0.0), c.get("g_R2_parity", 0.0),
                            c.get("g_R3_parity", 0.0), gC_from_gR2(gR2)])
            p = ((vec[VARY] - mu) / sd_safe) @ evecs[:, :2]
            ax1.scatter([p[0]], [p[1]], s=45, c="red", edgecolor="white", zorder=5)
            ax1.annotate(name, (p[0], p[1]), fontsize=6, color="white",
                         textcoords="offset points", xytext=(4, 2))
        ax1.set_xlabel("PC1"); ax1.set_ylabel("PC2")
        ax1.set_title(f"Consistent-QG island in PCA space\n"
                      f"{total_surv:,} survivors / {total_n:,} "
                      f"({frac*100:.2f}%); frameworks in red")
        cumvar = np.cumsum(evals) / evals.sum()
        ax2.bar(range(1, len(evals) + 1), evals / evals.sum(),
                color="#1f77b4", alpha=0.8, label="variance fraction")
        ax2.plot(range(1, len(evals) + 1), cumvar, "ko-", label="cumulative")
        ax2.axhline(0.9, color="green", ls="--", lw=1, label="90%")
        ax2.axhline(0.99, color="orange", ls="--", lw=1, label="99%")
        ax2.set_xlabel("principal component"); ax2.set_ylabel("variance fraction")
        ax2.set_title("PCA scree - dimensionality of the island")
        ax2.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(png, dpi=140)

    walls = sorted([(_NAMES[j], int(binding_counts[j]))
                    for j in range(len(_NAMES)) if binding_counts[j] > 0],
                   key=lambda kv: -kv[1])[:8]
    fails = sorted([(_NAMES[j], int(fail_counts[j]))
                    for j in range(len(_NAMES)) if fail_counts[j] > 0],
                   key=lambda kv: -kv[1])[:8]

    summary = {
        "samples": total_n, "survivors": total_surv,
        "volume_fraction": round(frac, 5),
        "volume_fraction_stderr": round(frac_err, 6),
        "box": {k: [float(LO[i]), float(HI[i])] for i, k in enumerate(COEFFS)},
        "pca": pca,
        "island_walls_nearest_margin_count": walls,
        "primary_excluders_of_failures": fails,
        "frameworks_by_distance_to_centroid": fw_rows,
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
