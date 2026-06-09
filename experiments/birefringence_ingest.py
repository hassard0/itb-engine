"""v1.78 - The second experiment: cosmic birefringence, and the engine's first
DATA preference for a nonzero (parity-violating) coefficient.

We ingest the Minami-Komatsu / Eskilt isotropic cosmic-birefringence measurement
beta = 0.34 +/- 0.09 deg as a constraint on the parity sector, and show:
  (1) the allowed g_R2_parity band EXCLUDES ZERO -- the engine now prefers a
      nonzero, definite-handedness parity coupling;
  (2) which frameworks are favored (in the band) vs disfavored (parity-even, or
      the WRONG handedness);
  (3) the 2-experiment 'empirical swampland': theory + sub-mm + birefringence.

Run on Vulcan:  python experiments/birefringence_ingest.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from stack import build_stack
from itb.predict import FRAMEWORKS
from itb.constraints.cosmic_birefringence import (
    CosmicBirefringenceData, BETA_MEAS_DEG, BETA_SIGMA_DEG, KAPPA_BETA)


def main():
    bire = CosmicBirefringenceData(mode="hint", n_sigma=2.0)
    band = bire.preferred_band
    zero_sigma = bire.excludes_zero_at_sigma

    theo = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    both = build_stack(bnossw_mean="geometric", rfc_form="convex_hull",
                       include_data=True, include_birefringence=True)

    # framework verdicts
    rows = []
    for name, fw in FRAMEWORKS.items():
        th = fw.encode()
        gp = th.coefficients.get("g_R2_parity", 0.0)
        bpred = KAPPA_BETA * gp
        bire_ok = bire.evaluate(th).satisfied
        feas_theo = all(c.evaluate(th).satisfied for c in theo)
        feas_both = all(c.evaluate(th).satisfied for c in both)
        rows.append({"framework": name, "g_R2_parity": round(gp, 3),
                     "beta_pred_deg": round(bpred, 3),
                     "birefringence_ok": bool(bire_ok),
                     "feasible_theory_only": bool(feas_theo),
                     "feasible_theory+both_data": bool(feas_both)})
    rows.sort(key=lambda r: -r["g_R2_parity"])

    favored = [r["framework"] for r in rows if r["birefringence_ok"]]
    parity_even_excluded = [r["framework"] for r in rows
                            if r["g_R2_parity"] == 0.0 and not r["birefringence_ok"]]
    wrong_handed = [r["framework"] for r in rows
                    if r["g_R2_parity"] < 0 and not r["birefringence_ok"]]
    survive_both = [r["framework"] for r in rows if r["feasible_theory+both_data"]]

    # ---- figure ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    # left: beta line with MK measurement, band, zero, frameworks
    gp_grid = np.linspace(-0.15, 0.20, 300)
    ax1.axvspan(band[0], band[1], color="#9467bd", alpha=0.2,
                label=f"preferred g_R2_parity band (2 sigma)")
    ax1.axvline(0.0, color="#d62728", lw=2, ls="--",
                label=f"parity-even (beta=0) EXCLUDED at {zero_sigma:.1f} sigma")
    ax1.axvline(BETA_MEAS_DEG / KAPPA_BETA, color="black", lw=1.5,
                label=f"Minami-Komatsu beta={BETA_MEAS_DEG} deg")
    for r in rows:
        gp = r["g_R2_parity"]
        col = "#2ca02c" if r["birefringence_ok"] else "#999999"
        ax1.scatter([gp], [0], s=60, color=col, edgecolor="black", zorder=5)
        if abs(gp) > 1e-6:
            ax1.annotate(r["framework"][:12], (gp, 0), rotation=40, fontsize=6.5,
                         textcoords="offset points", xytext=(2, 6))
    ax1.set_yticks([]); ax1.set_xlabel("g_R2_parity (leading Chern-Simons/Pontryagin coupling)")
    ax1.set_title("Cosmic birefringence PREFERS nonzero, positive-handed parity\n"
                  "green = in band; grey = disfavored (zero or wrong sign)", fontsize=9)
    ax1.legend(fontsize=7.5, loc="upper left")

    # right: beta predicted per framework vs measurement
    fw_n = [r["framework"] for r in rows]
    betas = [r["beta_pred_deg"] for r in rows]
    cols = ["#2ca02c" if r["birefringence_ok"] else "#999999" for r in rows]
    ax2.barh(fw_n[::-1], betas[::-1], color=cols[::-1])
    ax2.axvspan(BETA_MEAS_DEG - 2*BETA_SIGMA_DEG, BETA_MEAS_DEG + 2*BETA_SIGMA_DEG,
                color="#9467bd", alpha=0.2, label="MK 2 sigma")
    ax2.axvline(BETA_MEAS_DEG, color="black", lw=1.5, label="beta=0.34 deg")
    ax2.axvline(0.0, color="#d62728", lw=1, ls="--")
    ax2.set_xlabel("predicted birefringence beta (deg)")
    ax2.set_title("Per-framework predicted beta vs the measurement", fontsize=9)
    ax2.tick_params(axis="y", labelsize=7); ax2.legend(fontsize=7.5)
    fig.suptitle("v1.78  The second experiment: cosmic birefringence selects a "
                 "parity-violating handedness", fontsize=11)
    fig.tight_layout()
    png = "/tmp/birefringence_ingest.png"
    fig.savefig(png, dpi=140)

    summary = {
        "measurement": {"beta_deg": BETA_MEAS_DEG, "sigma_deg": BETA_SIGMA_DEG,
                        "excludes_zero_at_sigma": round(zero_sigma, 2),
                        "citation": "Minami-Komatsu 2020 / Eskilt-Komatsu 2022"},
        "mapping": f"beta = {KAPPA_BETA} * g_R2_parity (order-of-magnitude)",
        "preferred_g_R2_parity_band_2sigma": [round(b, 4) for b in band],
        "zero_excluded": bool(0.0 < band[0] or 0.0 > band[1]),
        "favored_by_birefringence": favored,
        "disfavored_parity_even": parity_even_excluded,
        "disfavored_wrong_handedness": wrong_handed,
        "survive_theory_plus_both_data": survive_both,
        "frameworks": rows,
        "honesty": "beta is a ~3.6 sigma HINT, not a discovery; the main systematic "
                   "is detector polarization-angle miscalibration.",
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
