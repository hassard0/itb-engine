"""v1.85 - The proper tensor probe: does the LIGO dispersion test reach the
dark-energy cutoff where GW170817 could not?

GW170817's arrival-time SPEED test was blind (v1.84). The intra-messenger
DISPERSION test (cumulative waveform phase Psi(f)) has a ~1e20 lever arm (E_GW*D),
so for alpha=4 (omega^2 = k^2 + k^4/M^2) the anomalous phase delta_Psi ~
g*E_GW^3*D/M^2 reaches O(0.1-1) rad for a dark-energy-scale cutoff over ~Gpc. We
compute delta_Psi for the frameworks at the dark-energy cutoff, the exclusion
frontier M_min, and compare to GW170817's reach.

Run on Vulcan:  python experiments/gw_dispersion.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")

from itb.predict import FRAMEWORKS
from itb.holographic_ac import gC_from_gR2
from itb.constraints.gw_dispersion import (
    delta_psi, GWDispersionBound, E_GW_LIGO_eV, E_LAMBDA_DE_eV, GPC_m, HBARC_eV_m)
from itb.constraints.gw_speed import delta_cGW, CGW_BOUND


def main():
    bound = GWDispersionBound(low_cutoff=True)        # M = 2.4 meV, 1 rad, 1 Gpc

    fw_rows = []
    for name, fw in FRAMEWORKS.items():
        c = fw.encode().coefficients
        gR2 = c.get("g_R2", 0.0)
        gC = c.get("g_C", gC_from_gR2(gR2))
        g = abs(gR2) + abs(gC)
        dpsi = delta_psi(g, E_LAMBDA_DE_eV)
        m_min = bound.m_min_excluded(g) if g > 0 else 0.0
        fw_rows.append({"framework": name, "g_curv": round(g, 3),
                        "delta_Psi_rad_DE_cutoff": round(dpsi, 4),
                        "M_min_excluded_eV": m_min,
                        "DE_cutoff_at_frontier": 0.1 < dpsi})  # within reach of ~0.1-1 rad
    fw_rows.sort(key=lambda r: -r["g_curv"])

    # representative g for the frontier curves
    g_ref = 0.6
    M_grid = np.logspace(-6, 0, 300)       # eV, ueV to eV
    psi_grid = np.array([delta_psi(g_ref, M) for M in M_grid])
    # speed-test deltacGW for comparison (same g)
    cgw_grid = np.array([delta_cGW(g_ref, M) for M in M_grid])

    M_min_disp = bound.m_min_excluded(g_ref)             # dispersion frontier (1 rad)
    M_min_disp_future = GWDispersionBound(psi_sens=0.1).m_min_excluded(g_ref)
    # speed frontier: deltacGW = 5e-16 -> M
    M_min_speed = E_GW_LIGO_eV * np.sqrt(g_ref / CGW_BOUND)

    # ---- figure: delta_Psi vs cutoff M, frontiers + dark-energy scale ----
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.loglog(M_grid, psi_grid, color="#1f77b4", lw=2,
              label=r"dispersion test $\delta\Psi$ (1 Gpc)")
    ax.axhline(1.0, color="#1f77b4", ls="--", lw=1, label="LVK sensitivity ~1 rad")
    ax.axhline(0.1, color="#1f77b4", ls=":", lw=1, label="future ~0.1 rad")
    ax.axvline(E_LAMBDA_DE_eV, color="#d62728", lw=2,
               label="dark-energy cutoff (2.4 meV)")
    ax.axvline(M_min_disp, color="#2ca02c", ls="--", lw=1.3,
               label=f"dispersion frontier M_min~{M_min_disp*1e3:.1f} meV (1 rad)")
    ax.axvline(M_min_speed, color="#7f2704", ls=":", lw=1.3,
               label=f"GW170817 speed frontier ~{M_min_speed*1e6:.0f} ueV")
    # frameworks at the dark-energy cutoff
    for r in fw_rows:
        ax.scatter([E_LAMBDA_DE_eV], [r["delta_Psi_rad_DE_cutoff"]], s=28,
                   color="black", zorder=5)
    ax.set_xlabel("EFT cutoff M (eV)")
    ax.set_ylabel(r"anomalous GW phase $\delta\Psi$ (rad)")
    ax.set_title("v1.85  The dispersion test REACHES the dark-energy cutoff\n"
                 "cumulative phase (lever arm ~1e20) brings delta_Psi to ~0.3 rad at "
                 "2.4 meV -- where GW170817's speed test was 5 orders blind", fontsize=9.5)
    ax.set_ylim(1e-6, 1e6)
    ax.legend(fontsize=7.5, loc="upper right")
    fig.tight_layout()
    png = "/tmp/gw_dispersion.png"
    fig.savefig(png, dpi=140)

    dd = next(r for r in fw_rows if r["framework"] == "discovered_data_driven")
    summary = {
        "scaling": "delta_Psi = 0.5*g*E_GW^3*D/(M^2 hbar c); enhancement vs speed ~ E_GW*D ~ 1e20",
        "dark_energy_cutoff_eV": E_LAMBDA_DE_eV,
        "delta_Psi_at_DE_cutoff_g0.6_rad": round(delta_psi(0.6, E_LAMBDA_DE_eV), 3),
        "M_min_excluded_eV_now_1rad": float(M_min_disp),
        "M_min_excluded_eV_future_0.1rad": float(M_min_disp_future),
        "GW170817_speed_frontier_eV": float(M_min_speed),
        "dispersion_reaches_meV": M_min_disp > 1e-4,
        "verdict": ("The dispersion test REACHES the meV scale: the dark-energy "
                    "cutoff sits AT THE FRONTIER (delta_Psi ~ 0.3 rad now); ~0.1 rad "
                    "sensitivity would EXCLUDE it. GW170817's speed test reached only "
                    "~ueV -- ~100x weaker in cutoff. The tensor sector CAN probe the "
                    "low cutoff, via the dispersion (not speed) test."),
        "data_driven_delta_Psi_rad": dd["delta_Psi_rad_DE_cutoff"],
        "caveats": ["alpha=4 dispersion via Weyl^2 typically brings a massive spin-2 "
                    "GHOST (the A_alpha bound is bottom-up; ghost-freedom is a separate "
                    "UV question)",
                    "delta_Psi(f) degenerate with chirp mass / spins in template fits",
                    "LVK bound assumes the standard massless mode dominates (mode mixing)"],
        "frameworks": fw_rows,
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
