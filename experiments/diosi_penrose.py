"""v1.90 - Ingest the Diosi-Penrose exclusion: is gravity classical?

A real, sharp falsification in a sector the engine has only gestured at (the
penrose_diosi framework). Penrose (1996) / Diosi (1989): gravity itself induces
wavefunction collapse, with a rate set by the gravitational self-energy difference
between superposed mass configurations. The model needs a regularization length R_0;
the PARAMETER-FREE version takes R_0 at the nucleon/nucleus scale (~1e-15 m).

The collapse forces charged particles to emit spontaneous radiation, with a rate
that scales as 1/R_0^3. The 2021 underground germanium experiment (Donadi,
Piscicchia, Curceanu, Diosi, Laubenstein, Bassi, Nature Physics 17, 74 (2021))
found NO excess X-rays in 1-4 keV and bounded

        R_0 > 0.54 Angstrom = 5.4e-11 m   (95% CL),

EXCLUDING the parameter-free Diosi-Penrose model (R_0 ~ 1e-15 m) by a huge margin.
We quantify the exclusion and connect it to the engine's premise.

Run on Vulcan:  python experiments/diosi_penrose.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R0_NUCLEON_m = 1.0e-15        # parameter-free DP regularization (nucleon size)
R0_NUCLEUS_m = 1.0e-14       # alternative parameter-free choice (nucleus)
R0_BOUND_m = 5.4e-11         # Donadi et al 2021, 95% CL lower limit (0.54 Angstrom)


def rate_ratio(R0_m):
    """DP spontaneous-emission rate relative to the experimental upper bound.
    Rate ~ 1/R_0^3, normalized so ratio = 1 at the excluded R_0 bound. ratio > 1
    => above the measured limit => EXCLUDED."""
    return (R0_BOUND_m / R0_m) ** 3


def main():
    ratio_nucleon = rate_ratio(R0_NUCLEON_m)
    ratio_nucleus = rate_ratio(R0_NUCLEUS_m)
    excluded_nucleon = ratio_nucleon > 1.0
    excluded_nucleus = ratio_nucleus > 1.0
    # how many orders of magnitude over the bound
    orders_nucleon = np.log10(ratio_nucleon)

    # ---- figure: DP rate vs R_0, with the bound + parameter-free scales ----
    R0 = np.logspace(-15.5, -9, 400)
    ratio = rate_ratio(R0)
    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    ax.loglog(R0 * 1e10, ratio, color="#1f77b4", lw=2,
              label=r"DP spontaneous-emission rate $\propto 1/R_0^3$")
    ax.axhline(1.0, color="#d62728", lw=2, ls="--",
               label="Donadi et al 2021 95% CL limit")
    ax.axhspan(1.0, 1e50, color="#d62728", alpha=0.08)
    ax.axvline(R0_NUCLEON_m * 1e10, color="#7f2704", lw=1.5, ls=":",
               label="parameter-free R_0 (nucleon, 1e-15 m)")
    ax.axvline(R0_BOUND_m * 1e10, color="#2ca02c", lw=1.5, ls="-.",
               label="allowed R_0 > 0.54 Angstrom")
    ax.scatter([R0_NUCLEON_m * 1e10], [ratio_nucleon], s=130, marker="*",
               color="#7f2704", edgecolor="black", zorder=6)
    ax.annotate(f"parameter-free DP\nEXCLUDED by ~{orders_nucleon:.0f} orders",
                (R0_NUCLEON_m * 1e10, ratio_nucleon), fontsize=8.5, color="#7f2704",
                textcoords="offset points", xytext=(12, -10))
    ax.set_xlabel(r"regularization length $R_0$ (Angstrom)", fontsize=12)
    ax.set_ylabel("rate / experimental limit  (>1 = excluded)", fontsize=12)
    ax.set_title("v1.90  The Diosi-Penrose exclusion: classical-gravity collapse\n"
                 "the parameter-free model is ruled out by ~14 orders of magnitude",
                 fontsize=10)
    ax.set_ylim(1e-12, 1e16)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    png = "/tmp/diosi_penrose.png"
    fig.savefig(png, dpi=140)

    summary = {
        "experiment": "Donadi-Piscicchia-Curceanu-Diosi-Laubenstein-Bassi, "
                      "Nature Physics 17, 74 (2021): underground Ge X-ray search",
        "bound": "R_0 > 0.54 Angstrom (5.4e-11 m), 95% CL",
        "parameter_free_R0_nucleon_m": R0_NUCLEON_m,
        "rate_over_limit_at_nucleon_R0": f"{ratio_nucleon:.2e}",
        "exclusion_orders_of_magnitude": round(float(orders_nucleon), 1),
        "parameter_free_DP_excluded": bool(excluded_nucleon),
        "even_nucleus_scale_excluded": bool(excluded_nucleus),
        "R0_must_exceed_nucleon_by_factor": f"{R0_BOUND_m / R0_NUCLEON_m:.1e}",
        "is_gravity_classical": "The simplest 'gravity is classical and causes "
            "collapse' (parameter-free Diosi-Penrose) model is FALSIFIED. To survive, "
            "DP needs an unmotivated macroscopic R_0 > 0.54 A, the collapse agent must "
            "not be gravity, OR there is no gravitational collapse -- consistent with "
            "gravity being QUANTUM, the engine's whole premise.",
        "engine_connection": "The engine's penrose_diosi framework represents the "
            "classical-gravity-collapse hypothesis; this real data weakly DISFAVORS it "
            "vs the quantum-gravity EFT the rest of the program assumes.",
        "honest": "DP spontaneous emission scales robustly as 1/R_0^3; the exact "
            "prefactor (and whether R_0 is the nucleon ~1e-15 m or nucleus ~1e-14 m) "
            "shifts the orders modestly -- the parameter-free model is excluded either "
            "way (by ~14 or ~11 orders).",
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
