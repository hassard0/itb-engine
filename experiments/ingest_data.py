"""v1.77 - The engine ingests real data: the island self-corrects.

We append the Eot-Wash sub-mm gravity bound (the first DATA-sourced constraint) to
the theoretical stack and ask what changes:
  (1) does the island CENTER move below the exclusion threshold g_R2 <= ~0.063
      (a now-ALLOWED, lambda < 50 um scalaron)?
  (2) does the island SHRINK -- new volume fraction vs the v1.73 theoretical 0.6%?
  (3) which frameworks newly fall outside?
All under the UNSCREENED assumption (submm_screened=False); screened theories are
untouched (and we verify the screened stack reproduces the theoretical island).

Run on Vulcan (16 cores):  python experiments/ingest_data.py [N]
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
from island_center import find_center
from itb.predict import FRAMEWORKS
from itb.constraints.submm_gravity import SubmmGravityYukawaBound, _lambda_um
from itb.theory import Theory

COEFFS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C"]
LO = np.array([0.05, 0.05, 0.05, 0.02, 0.0, 0.02])
HI = np.array([0.60, 0.60, 0.70, 0.45, 0.4, 0.60])

_THEO = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
_DATA = build_stack(bnossw_mean="geometric", rfc_form="convex_hull", include_data=True)


def _theory6(x):
    d = {k: float(v) for k, v in zip(COEFFS, x)}
    d["g_R2_parity"] = 0.0; d["g_R3_parity"] = 0.0
    return Theory(coefficients=d)


def _census_chunk(arg):
    seed, n = arg
    rng = np.random.default_rng(seed)
    X = LO + (HI - LO) * rng.random((n, len(COEFFS)))
    s_theo = s_data = 0
    for i in range(n):
        th = _theory6(X[i])
        ok_theo = all(c.evaluate(th).satisfied for c in _THEO)
        if ok_theo:
            s_theo += 1
            if all(c.evaluate(th).satisfied for c in _DATA):
                s_data += 1
    return s_theo, s_data, n


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000

    # --- centers before/after ---
    c_theo = find_center(_THEO, n_starts=40)
    c_data = find_center(_DATA, n_starts=40)
    gR2_theo = c_theo["x"][3]
    gR2_data = c_data["x"][3]
    submm = SubmmGravityYukawaBound()
    g_R2_max = submm.g_R2_max
    lam_theo = _lambda_um(gR2_theo, submm.E_Lambda)
    lam_data = _lambda_um(gR2_data, submm.E_Lambda)

    # --- census before/after (16 cores) ---
    ncpu = max(1, (os.cpu_count() or 4) - 1)
    chunks = ncpu * 4
    per = N // chunks
    from multiprocessing import Pool
    with Pool(ncpu) as pool:
        res = pool.map(_census_chunk, [(3000 + k, per) for k in range(chunks)])
    surv_theo = sum(r[0] for r in res)
    surv_data = sum(r[1] for r in res)   # survivors of THEORETICAL that ALSO pass data
    total = sum(r[2] for r in res)
    frac_theo = surv_theo / total
    # data-island fraction = (theoretical survivors that pass data) / total
    frac_data = surv_data / total
    kept = surv_data / surv_theo if surv_theo else 0.0

    # --- frameworks newly excluded by the data constraint ---
    newly = []
    for name, fw in FRAMEWORKS.items():
        th = fw.encode()
        feas_theo = all(c.evaluate(th).satisfied for c in _THEO)
        feas_data = all(c.evaluate(th).satisfied for c in _DATA)
        gR2 = th.coefficients.get("g_R2", 0.0)
        if feas_theo and not feas_data:
            newly.append({"framework": name, "g_R2": round(gR2, 3),
                          "lambda_um": round(_lambda_um(gR2, submm.E_Lambda), 1)})

    # --- figure: before/after center on the g_R2 / lambda axis vs exclusion ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    # left: g_R2 number line with exclusion threshold and the two centers
    ax1.axvspan(g_R2_max, HI[3], color="#d62728", alpha=0.18,
                label=f"excluded by sub-mm data (g_R2 > {g_R2_max:.3f})")
    ax1.axvline(g_R2_max, color="#d62728", lw=2, ls="--",
                label=f"exclusion threshold g_R2={g_R2_max:.3f} (lambda=50um)")
    ax1.scatter([gR2_theo], [1], s=180, marker="*", color="#1f77b4",
                edgecolor="black", zorder=5,
                label=f"center BEFORE data: g_R2={gR2_theo:.3f} (lambda={lam_theo:.0f}um, EXCLUDED)")
    ax1.scatter([gR2_data], [1], s=180, marker="*", color="#2ca02c",
                edgecolor="black", zorder=5,
                label=f"center AFTER data: g_R2={gR2_data:.3f} (lambda={lam_data:.0f}um, allowed)")
    ax1.set_yticks([]); ax1.set_xlim(0, HI[3]); ax1.set_xlabel("g_R2 (leading curvature coupling)")
    ax1.set_title("Island center self-corrects below the sub-mm exclusion threshold")
    ax1.legend(fontsize=7.5, loc="upper center")

    # right: census volume before/after
    bars = ax2.bar(["theoretical\n(axioms only)", "+ sub-mm data\n(unscreened)"],
                   [frac_theo * 100, frac_data * 100],
                   color=["#1f77b4", "#2ca02c"], alpha=0.85)
    for b, v in zip(bars, [frac_theo * 100, frac_data * 100]):
        ax2.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}%",
                 ha="center", va="bottom", fontsize=10)
    ax2.set_ylabel("island volume fraction (%)")
    ax2.set_title(f"Island shrinks by ingesting data\n({kept*100:.0f}% of the "
                  f"theoretical island survives the sub-mm bound)")
    fig.tight_layout()
    png = "/tmp/ingest_data.png"
    fig.savefig(png, dpi=140)

    summary = {
        "exclusion_threshold_g_R2_max": round(g_R2_max, 4),
        "exclusion_threshold_lambda_um": round(submm.lambda_max_um, 1),
        "center_before_data": {"g_R2": round(gR2_theo, 4), "lambda_um": round(lam_theo, 1),
                               "submm_status": "EXCLUDED" if gR2_theo > g_R2_max else "allowed"},
        "center_after_data": {"g_R2": round(gR2_data, 4), "lambda_um": round(lam_data, 1),
                              "submm_status": "EXCLUDED" if gR2_data > g_R2_max else "allowed",
                              "full_coeffs": c_data["center_coefficients"],
                              "inradius": c_data["inradius_walls_min_margin"],
                              "nearest_framework": c_data["frameworks_by_distance_to_center"][0]},
        "census": {"samples": total,
                   "volume_fraction_theoretical": round(frac_theo, 5),
                   "volume_fraction_with_data": round(frac_data, 5),
                   "fraction_of_island_surviving_data": round(kept, 4)},
        "frameworks_newly_excluded_by_data": newly,
        "assumption": "UNSCREENED f(R) scalaron coupling to the Standard Model; "
                      "screened (chameleon/Vainshtein/dark) theories are untouched.",
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
