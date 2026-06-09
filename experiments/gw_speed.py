"""v1.84 - The third experiment: GW170817 graviton speed, and what it does (and
does NOT) constrain.

We ingest the GW170817 speed bound |delta c_GW|/c < 5e-16 on the tensor-propagation
sector and ask whether it squeezes the dark-energy (low) cutoff the way sub-mm
gravity (v1.77) does. The honest answer (Dr. M.-confirmed): NO -- for higher-
derivative gravity the speed deviation is frequency-suppressed,
delta c_GW/c ~ g*(E_GW/E_cutoff)^2, and LIGO GWs are so low-energy that even at the
dark-energy cutoff delta c_GW ~ 1e-20, orders below the bound. GW170817 is a SPEED
test, blind to (k/M)^2 dispersion at LIGO frequencies. So the three experiments do
NOT triangulate identically: the low-cutoff pressure comes specifically from light
LONG-RANGE modes (sub-mm scalaron), not the high-derivative tensor sector.

Run on Vulcan:  python experiments/gw_speed.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")

from itb.predict import FRAMEWORKS
from itb.constraints.gw_speed import (
    delta_cGW, CGW_BOUND, E_GW_LIGO_eV, E_LAMBDA_DE_eV, E_HIGH_eV, GWSpeedBound)
from itb.holographic_ac import gC_from_gR2


def main():
    # representative curvature coupling per framework: |g_R2| + |g_C|
    fw_rows = []
    for name, fw in FRAMEWORKS.items():
        c = fw.encode().coefficients
        gR2 = c.get("g_R2", 0.0)
        gC = c.get("g_C", gC_from_gR2(gR2))
        g = abs(gR2) + abs(gC)
        dc_low = delta_cGW(g, E_LAMBDA_DE_eV)
        dc_high = delta_cGW(g, E_HIGH_eV)
        fw_rows.append({"framework": name, "g_curv": round(g, 3),
                        "delta_cGW_low_cutoff": dc_low,
                        "delta_cGW_high_cutoff": dc_high,
                        "low_excluded": dc_low > CGW_BOUND})
    fw_rows.sort(key=lambda r: -r["g_curv"])

    # critical cutoff where GW170817 would START to bite (for g~0.4)
    g_ref = 0.4
    E_crit = E_GW_LIGO_eV * np.sqrt(g_ref / CGW_BOUND)   # delta=bound -> solve E
    # margin of the dark-energy cutoff above the critical one
    safety_factor = E_LAMBDA_DE_eV / E_crit

    # does the constraint exclude any framework at the low cutoff?
    excluded_low = [r["framework"] for r in fw_rows if r["low_excluded"]]

    # ---- figure: delta c_GW vs the bound, low vs high cutoff ----
    fig, ax = plt.subplots(figsize=(11, 6.5))
    names = [r["framework"] for r in fw_rows]
    y = np.arange(len(names))[::-1]
    dc_low = [max(r["delta_cGW_low_cutoff"], 1e-40) for r in fw_rows]
    dc_high = [max(r["delta_cGW_high_cutoff"], 1e-40) for r in fw_rows]
    ax.scatter(dc_low, y, s=70, color="#d62728", label="dark-energy cutoff (2.4 meV)",
               zorder=5)
    ax.scatter(dc_high, y, s=55, color="#1f77b4", marker="s",
               label="high cutoff (1e25 eV)", zorder=5)
    ax.axvline(CGW_BOUND, color="black", lw=2, ls="--",
               label=f"GW170817 bound (5e-16)")
    ax.axvspan(CGW_BOUND, 1e2, color="#d62728", alpha=0.08)
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8)
    ax.set_xscale("log"); ax.set_xlim(1e-40, 1e2)
    ax.set_xlabel(r"$|\delta c_{\rm GW}|/c$  predicted")
    ax.set_title("v1.84  GW170817 is BLIND to higher-derivative gravity\n"
                 "even at the dark-energy cutoff, delta c_GW (red) sits ~5 orders "
                 "below the bound -- GW speed does NOT squeeze the low cutoff",
                 fontsize=9.5)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    png = "/tmp/gw_speed.png"
    fig.savefig(png, dpi=140)

    # data-driven EFT
    dd = next(r for r in fw_rows if r["framework"] == "discovered_data_driven")
    summary = {
        "GW170817_bound": CGW_BOUND,
        "scaling": "delta c_GW/c = kappa_c * (|g_R2|+|g_C|) * (E_GW/E_cutoff)^2",
        "E_GW_LIGO_eV": E_GW_LIGO_eV,
        "dark_energy_cutoff_eV": E_LAMBDA_DE_eV,
        "frameworks_excluded_at_low_cutoff": excluded_low,
        "verdict": ("GW170817 does NOT exclude any framework even at the dark-energy "
                    "cutoff (blind to (k/M)^2 dispersion at LIGO frequencies)"),
        "data_driven_delta_cGW_low": dd["delta_cGW_low_cutoff"],
        "data_driven_ratio_to_bound": dd["delta_cGW_low_cutoff"] / CGW_BOUND,
        "critical_cutoff_eV_where_it_bites": float(E_crit),
        "dark_energy_cutoff_safety_factor": float(safety_factor),
        "honest_synthesis": "The three experiments do NOT triangulate identically. "
            "Sub-mm gravity (v1.77, matter/long-range scalaron) squeezes the dark-"
            "energy cutoff; GW170817 (tensor/high-derivative) does NOT -- it is a "
            "speed test, blind to the frequency-suppressed (k/M)^2 dispersion at LIGO "
            "frequencies. The RELEVANT tensor-sector probe is LIGO's intra-messenger "
            "DISPERSION test (waveform phase Psi(f)), not the arrival-time speed test.",
        "rows": [{k: (f"{v:.2e}" if isinstance(v, float) and abs(v) < 1e-6 else v)
                  for k, v in r.items()} for r in fw_rows],
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
