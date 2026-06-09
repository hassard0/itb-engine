"""v1.83 - The ITB master predictions scorecard & falsifiable roadmap.

Consolidates the whole empirical-swampland program (v1.71-82) into one forward-
looking picture: every distinct falsifiable prediction the engine now makes, its
current experimental status, and the next experiment (+ rough timeline) that tests
it. Numbers are pulled live from `itb predict discovered_data_driven` and the
engine modules where possible. (The earlier experiments/scorecard.py is the v1.51
snapshot; this is the expanded successor.)

Status legend:
  DETECTED   - already measured at >=3 sigma (the engine is consistent with it)
  TENSION    - the engine + current data are in tension at face value
  EXCLUDED   - the naive (unscreened/face-value) prediction is excluded by data
  CONSISTENT - predicted, below current sensitivity, no contradiction (untested)
  STRUCTURAL - a theoretical-consistency statement (not yet a direct measurement)

Run on Vulcan:  python experiments/master_scorecard.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")

from itb.predict import predict

STATUS_COLORS = {
    "DETECTED": "#2ca02c",
    "TENSION": "#d62728",
    "EXCLUDED": "#7f2704",
    "CONSISTENT": "#1f77b4",
    "STRUCTURAL": "#9467bd",
}
STATUS_ORDER = ["DETECTED", "TENSION", "EXCLUDED", "CONSISTENT", "STRUCTURAL"]


def build_scorecard():
    p = predict("discovered_data_driven")
    o = p["observables"]
    beta = round(3.4 * p["coefficients"]["g_R2_parity"], 2)
    rows = [
        {"key": "submm", "prediction":
            "Dark-energy-scale f(R) scalaron fifth force (alpha=1/3) at lambda~80um",
         "version": "v1.76-77", "status": "EXCLUDED",
         "next": "Eot-Wash / next-gen sub-mm torsion balances", "when": "now-2030"},
        {"key": "cmb_beta", "prediction":
            f"Cosmic birefringence beta ~ {beta} deg (parity-violating universe)",
         "version": "v1.78", "status": "DETECTED",
         "next": "LiteBIRD / CMB-S4 (refine toward ~11 sigma)", "when": "2028-2032"},
        {"key": "tension", "prediction":
            "Birefringence vs unscreened dark-energy gravity -> PREFERS SCREENING",
         "version": "v1.79-80", "status": "TENSION",
         "next": "joint sub-mm + CMB; chameleon/screening tests", "when": "now-2032"},
        {"key": "gw_bire", "prediction":
            f"LIGO/Virgo GW birefringence (|g_R2_parity|={o['gw_birefringence_g_R2_parity']})",
         "version": "v1.81", "status": "CONSISTENT",
         "next": "Einstein Telescope / Cosmic Explorer (~1.2 sigma)", "when": "2035+"},
        {"key": "pta", "prediction":
            f"PTA chiral SGWB Pi_V ~ {o['chiral_HD_circular_polarization_pct'][0]}-"
            f"{o['chiral_HD_circular_polarization_pct'][1]}%",
         "version": "v1.81", "status": "CONSISTENT",
         "next": "SKA-PTA (~1.6 sigma)", "when": "2030-2035"},
        {"key": "eta_s", "prediction":
            f"Holographic eta/s ~ {o['holographic_eta_over_s_KSS_units']} (KSS-violating dual)",
         "version": "v1.67/72", "status": "STRUCTURAL",
         "next": "no direct probe (holographic-dual statement)", "when": "--"},
        {"key": "ac_wedge", "prediction":
            "a/c central-charge ratio inside Hofman-Maldacena wedge [1/3, 31/18]",
         "version": "v1.71", "status": "STRUCTURAL",
         "next": "theoretical (conformal-collider consistency)", "when": "--"},
        {"key": "bh_entropy", "prediction":
            f"Extremal BH entropy shift Delta S_ext = {o['bh_entropy_shift_delta_S_ext']} > 0 (WGC)",
         "version": "v1.82", "status": "STRUCTURAL",
         "next": "theoretical (WGC / black-hole thermodynamics)", "when": "--"},
        {"key": "island", "prediction":
            "Consistent-QG EFT island ~0.6% by volume, ~3.4 effective dimensions",
         "version": "v1.73", "status": "STRUCTURAL",
         "next": "tightens as each new constraint/experiment is added", "when": "--"},
        {"key": "data_eft", "prediction":
            "Data-driven EFT: screened scalaron + positive-handed parity",
         "version": "v1.79", "status": "TENSION",
         "next": "joint sub-mm + CMB + GW/PTA", "when": "2030+"},
        {"key": "inflation", "prediction":
            "R^2 (Starobinsky) inflation: n_s~0.964, r~0.004 (best-fit model)",
         "version": "v1.86", "status": "DETECTED",
         "next": "LiteBIRD / CMB-S4 / Simons (r down to ~0.001)", "when": "2028-2032"},
    ]
    return rows


def main():
    rows = build_scorecard()
    rows_sorted = sorted(rows, key=lambda r: STATUS_ORDER.index(r["status"]))
    fig, ax = plt.subplots(figsize=(15, 8))
    y = np.arange(len(rows_sorted))[::-1]
    for r, yy in zip(rows_sorted, y):
        col = STATUS_COLORS[r["status"]]
        ax.barh(yy, 1.0, height=0.74, color=col, alpha=0.9)
        ax.text(0.012, yy, f"{r['prediction']}  [{r['version']}]", va="center",
                ha="left", fontsize=8.6, color="white", fontweight="bold")
        ax.text(1.03, yy, r["status"], va="center", ha="left", fontsize=8.3,
                color=col, fontweight="bold")
        ax.text(1.18, yy, f"-> {r['next']}  ({r['when']})", va="center", ha="left",
                fontsize=7.4, color="black")
    ax.set_xlim(0, 2.25); ax.set_ylim(-0.6, len(rows_sorted) - 0.4)
    ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=STATUS_COLORS[s]) for s in STATUS_ORDER]
    ax.legend(handles, STATUS_ORDER, loc="lower center", fontsize=8, ncol=5,
              frameon=False, bbox_to_anchor=(0.5, -0.07))
    ax.set_title("v1.83  ITB master predictions scorecard & falsifiable roadmap\n"
                 "what consistency + current data point to, and what tests each next",
                 fontsize=12, pad=14)
    fig.tight_layout()
    png = "/tmp/master_scorecard.png"
    fig.savefig(png, dpi=140, bbox_inches="tight")

    counts = {s: sum(1 for r in rows if r["status"] == s) for s in STATUS_ORDER}
    summary = {
        "n_predictions": len(rows),
        "status_counts": counts,
        "sharpest_tension": "birefringence vs unscreened dark-energy gravity "
                            "(~2.5-2.8 sigma, prefers screening) [v1.79-80]",
        "sharpest_near_future_test": "LiteBIRD/CMB-S4 cosmic birefringence "
                                     "(detection -> ~11 sigma) [v1.78/81]",
        "one_line_claim": "Given amplitude/causality/holographic consistency plus "
            "two experiments, the engine points to a parity-violating, screened-"
            "scalaron EFT: it MATCHES cosmic birefringence, REQUIRES screening to "
            "survive sub-mm gravity, and predicts GW/PTA parity signals just below "
            "current reach.",
        "global_caveats": [
            "toy O(1) constraint prefactors (the realism program tests which "
            "conclusions survive a factor-~2; the central tension does -- v1.80)",
            "order-of-magnitude cross-sector/messenger mappings (kappa_beta, lam_map, "
            "rho_inflow, BH-entropy factors)",
            "cosmic birefringence is a ~3.6 sigma HINT, not a discovery "
            "(polarization-angle systematics)",
            "screening treated as a binary flag (really density-dependent)",
            "CMB beta is axion-photon while GW/PTA are axion-graviton (one-axion "
            "assumption links them)",
        ],
        "rows": rows,
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
