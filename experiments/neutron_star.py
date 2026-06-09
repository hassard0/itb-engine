"""v1.91 - The strong-field probe: do neutron-star tides (GW170817) see the
dark-energy-cutoff curvature sector?

All ingested experiments so far are weak-field. Neutron stars are the strongest
GRAVITY accessible (compactness C = GM/Rc^2 ~ 0.2), so one might expect NS tides to
be the SHARPEST probe of higher-derivative curvature corrections. They are not.

A term g R^2/M_cutoff^2 corrects the tidal deformability at the relative level
        delta Lambda / Lambda ~ g_curv * (E_curv / M_cutoff)^2 ,
with E_curv ~ hbar c / R_NS the curvature in ENERGY units. The crucial point
(Dr. M.-confirmed): 'strong field' means strong GRAVITY (compactness ~0.2), NOT high
curvature-energy. E_curv ~ hbar c / (12 km) ~ 1.6e-11 eV -- far BELOW a meV cutoff --
so at the dark-energy cutoff the correction is ~(1.6e-11/2.4e-3)^2 ~ 1e-16: BLIND.

And GW170817 measures the (combined) Lambda-tilde only to ~tens of percent (Lambda-
tilde < ~720, Abbott et al 2017/2018), with NO propagation lever arm -- so NS tides
probe only ULTRA-low cutoffs M ~ E_curv ~ 1e-11 eV, even WEAKER than the GW speed
test. The strongest-gravity regime is the WEAKEST curvature-cutoff probe.

Honest caveat (Dr. M.): the TENSOR higher-derivative correction is blind, but the
light dark-energy SCALARON (matter fifth force) could affect Lambda -- except it is
SCREENED (chameleon/Vainshtein) in the dense NS interior, leaving it GR-like. So NS
tides are blind to the tensor sector AND screened from the scalar sector.

Run on Vulcan:  python experiments/neutron_star.py
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

HBARC_eV_m = 1.973e-7
R_NS_m = 1.2e4                 # ~12 km
E_CURV_eV = HBARC_eV_m / R_NS_m         # ~1.6e-11 eV (curvature in energy units)
E_LAMBDA_DE_eV = 2.4e-3       # dark-energy (low) cutoff
LAMBDA_PRECISION = 0.1        # GW170817 measures Lambda-tilde to ~tens of percent


def delta_Lambda_over_Lambda(g_curv, M_cutoff_eV):
    return g_curv * (E_CURV_eV / M_cutoff_eV) ** 2


def cutoff_reached(g_curv, E_probe, sensitivity):
    """Highest cutoff M a probe reaches: where the effect equals the sensitivity."""
    return E_probe * np.sqrt(g_curv / sensitivity)


def main():
    g_ref = 0.4
    dLL_de = delta_Lambda_over_Lambda(g_ref, E_LAMBDA_DE_eV)
    blind_at_de = dLL_de < LAMBDA_PRECISION
    M_NS = cutoff_reached(g_ref, E_CURV_eV, LAMBDA_PRECISION)

    # probe comparison: highest curvature cutoff each reaches (eV)
    probes = {
        "sub-mm gravity (matter, light scalaron)": E_LAMBDA_DE_eV,   # directly excites meV scalaron
        "GW dispersion (tensor, lever arm)": 1.8e-3,                 # v1.85
        "GW speed (tensor, arrival time)": cutoff_reached(g_ref, 4.1e-13, 5e-16),
        "NS tides (strong gravity, static)": M_NS,
    }

    # per-framework delta Lambda at the dark-energy cutoff (all blind)
    fw_rows = []
    for name, fw in FRAMEWORKS.items():
        c = fw.encode().coefficients
        gR2 = c.get("g_R2", 0.0)
        g = abs(gR2) + abs(c.get("g_C", gC_from_gR2(gR2)))
        fw_rows.append({"framework": name, "g_curv": round(g, 3),
                        "delta_Lambda_over_Lambda_DE_cutoff": delta_Lambda_over_Lambda(g, E_LAMBDA_DE_eV)})
    fw_rows.sort(key=lambda r: -r["g_curv"])

    # ---- figure: cutoff reach per probe (log), dark-energy line ----
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    labels = list(probes)[::-1]
    vals = [probes[k] for k in labels]
    colors = ["#2ca02c" if v >= E_LAMBDA_DE_eV * 0.5 else "#d62728" for v in vals]
    ax.barh(labels, vals, color=colors, alpha=0.85)
    ax.axvline(E_LAMBDA_DE_eV, color="black", lw=2, ls="--",
               label="dark-energy cutoff (2.4 meV)")
    ax.set_xscale("log"); ax.set_xlabel("highest curvature cutoff M the probe reaches (eV)")
    for k, v in zip(labels, vals):
        ax.text(v, k, f"  {v:.1e} eV", va="center", fontsize=8)
    ax.set_title("v1.91  Strong gravity is NOT high curvature-energy:\n"
                 "neutron-star tides are the WEAKEST probe of the dark-energy-cutoff "
                 "curvature sector", fontsize=10)
    ax.legend(fontsize=9, loc="lower right")
    fig.tight_layout()
    png = "/tmp/neutron_star.png"
    fig.savefig(png, dpi=140)

    summary = {
        "E_curv_eV": E_CURV_eV,
        "scaling": "delta Lambda/Lambda ~ g_curv (E_curv/M_cutoff)^2, E_curv ~ hbar c / R_NS",
        "delta_Lambda_over_Lambda_at_DE_cutoff": f"{dLL_de:.2e}",
        "blind_at_dark_energy_cutoff": bool(blind_at_de),
        "NS_cutoff_reached_eV": f"{M_NS:.2e}",
        "probe_cutoff_reach_eV": {k: f"{v:.2e}" for k, v in probes.items()},
        "verdict": "NS tides are BLIND to the meV cutoff -- reaching only ~1e-11 eV, "
                   "WEAKER than the GW speed test. Strong GRAVITY (compactness ~0.2) is "
                   "NOT high curvature-ENERGY (hbar c/R_NS ~ 1e-11 eV << meV); with "
                   "Lambda measured to ~10% and no lever arm, the strongest-gravity "
                   "regime is the weakest curvature-cutoff probe.",
        "scalar_vs_tensor": "The TENSOR higher-derivative correction is blind (low "
                            "E_curv). The light dark-energy SCALARON could affect Lambda "
                            "but is SCREENED (chameleon/Vainshtein) in the dense NS -- so "
                            "NS tides are blind to the tensor sector and screened from the "
                            "scalar sector.",
        "honest": "order-of-magnitude (no modified-TOV solve); robust content is the "
                  "scaling and the compactness vs curvature-energy distinction.",
        "citations": ["GW170817 tidal: Abbott et al PRL 119 (2017) 161101; PRL 121 "
                      "(2018) 161101", "Yagi-Yunes PRD 87 (2013) (NS Love numbers)"],
        "frameworks": fw_rows,
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
