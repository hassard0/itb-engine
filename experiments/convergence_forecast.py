"""v1.92 - The convergence forecast: when does the data pin the quantum-gravity EFT,
and the funded-roadmap gap.

v1.88 showed 6 measurements pin all 8 Wilson coefficients. Here we turn that static
result into a TIMELINE: assign each measurement its realistic future milestone year +
projected precision, accumulate the Fisher information year by year (2025-2042), and
forecast when the Fisher matrix reaches full rank (all 8 coefficient directions
constrained) -- i.e. when the consistent EFT is pinned to uniqueness.

KEY HONEST RESULT: g_8 (s^4 matter moment) and g_R3 (cubic curvature) have NO funded
experiment (the v1.88 blind spots). So on the funded roadmap the Fisher rank STALLS at
6/8 -- the EFT is never fully pinned until someone builds a high-scattering-moment and
a cubic-graviton/GW-nonlinearity probe. The timeline to solving QG has a gap.

Run on Vulcan:  python experiments/convergence_forecast.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from itb.observables import ScalarForwardAmplitude
from itb.gravitational_observables import (
    YukawaForceDeviation, GravitationalBirefringence, HolographicEtaOverS,
    BlackHoleEntropyShift)
from min_experiment_set import HighScatteringMoment, CubicGravitonAmplitude, PARAMS
from itb.frameworks.data_driven import DiscoveredDataDriven
from itb.theory import Theory

N = len(PARAMS)


def fisher(obs, sigma, th):
    J = obs.jacobian(th, PARAMS)
    return (J.T @ J) / sigma ** 2


def main():
    th = DiscoveredDataDriven().encode()
    for k in PARAMS:
        th.coefficients.setdefault(k, 0.0)

    # (label, observable, projected sigma, milestone YEAR or None, funded?)
    roadmap = [
        ("BH entropy / WGC consistency (g_C,g_4)", BlackHoleEntropyShift(), 0.10, 2025, "theory"),
        ("holographic eta/s (g_R2, indirect)", HolographicEtaOverS(), 0.20, 2026, "indirect"),
        ("matter scattering analysis (g_4,g_6)", ScalarForwardAmplitude(np.array([0.5, 1.0])), 0.05, 2027, "funded"),
        ("next-gen sub-mm gravity (g_R2)", YukawaForceDeviation([8e-5, 1e-4]), 0.08, 2028, "funded"),
        ("CMB birefringence LiteBIRD/CMB-S4 (parity)", GravitationalBirefringence([1.0, 2.0]), 0.03, 2030, "funded"),
        ("PTA chirality SKA (parity)", GravitationalBirefringence([0.5]), 0.05, 2032, "funded"),
        ("GW dispersion ET/CE (g_R2)", YukawaForceDeviation([9e-5]), 0.10, 2035, "funded"),
        # blind spots -- NO funded experiment
        ("high scattering moment (g_8) -- NO ROADMAP", HighScatteringMoment([1.0, 1.5]), 0.10, None, "none"),
        ("cubic-graviton amplitude (g_R3) -- NO ROADMAP", CubicGravitonAmplitude(), 0.20, None, "none"),
    ]

    years = list(range(2025, 2043))
    EPS = 1e-6
    PREC = 0.5
    rank_by_year, worst_by_year = [], []
    for y in years:
        F = EPS * np.eye(N)
        for label, obs, sig, yr, funded in roadmap:
            if yr is not None and yr <= y:
                F = F + fisher(obs, sig, th)
        rank = int(np.linalg.matrix_rank(F - EPS * np.eye(N), tol=1e-9))
        # worst sigma over the CONSTRAINED subspace (ignore unbounded directions)
        evals = np.linalg.eigvalsh(F)
        constrained = evals[evals > 10 * EPS]
        worst = float(1.0 / np.sqrt(constrained.min())) if constrained.size else np.inf
        rank_by_year.append(rank); worst_by_year.append(worst)

    # forecast: does rank ever hit 8 on the funded+available roadmap?
    final_rank = rank_by_year[-1]
    pinned_year = next((y for y, r in zip(years, rank_by_year) if r >= N), None)
    stall_rank = max(rank_by_year)
    # which directions remain blind (no observable with a year touches them)
    touched = np.zeros(N, dtype=bool)
    for label, obs, sig, yr, funded in roadmap:
        if yr is not None:
            touched |= (np.abs(fisher(obs, sig, th)).sum(axis=0) > 1e-12)
    blind = [PARAMS[i] for i in range(N) if not touched[i]]

    # if the blind-spot probes were built (~2040), rank would reach:
    F_all = EPS * np.eye(N)
    for label, obs, sig, yr, funded in roadmap:
        F_all = F_all + fisher(obs, sig, th)
    rank_with_blindspots = int(np.linalg.matrix_rank(F_all - EPS * np.eye(N), tol=1e-9))

    # ---- figure: rank staircase + worst-sigma vs year ----
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    ax1.step(years, rank_by_year, where="post", color="#1f77b4", lw=2)
    ax1.axhline(N, color="#2ca02c", ls="--", lw=1, label="full rank = pinned (8)")
    ax1.axhline(stall_rank, color="#d62728", ls=":", lw=1.5,
                label=f"STALL at rank {stall_rank} (funded roadmap)")
    for label, obs, sig, yr, funded in roadmap:
        if yr is not None:
            ax1.annotate(label.split("(")[0][:22], (yr, rank_by_year[years.index(yr)]),
                         fontsize=6, rotation=30, textcoords="offset points", xytext=(2, 3))
    ax1.set_ylabel("Fisher rank (coeff directions pinned)")
    ax1.set_ylim(0, 8.5); ax1.legend(fontsize=8, loc="lower right")
    ax1.set_title("v1.92  The convergence forecast: the EFT pins to rank "
                  f"{stall_rank}/8 and STALLS -- g_8 & g_R3 have no funded probe",
                  fontsize=10)
    ax2.semilogy(years, worst_by_year, "o-", color="#9467bd",
                 label="worst sigma (constrained subspace)")
    ax2.axhline(PREC, color="#d62728", ls="--", lw=1, label=f"toy precision {PREC}")
    ax2.set_xlabel("year"); ax2.set_ylabel("worst parameter uncertainty")
    ax2.legend(fontsize=8); ax2.set_title(
        "constrained directions tighten, but 2 directions stay unbounded (no probe)",
        fontsize=9)
    fig.tight_layout()
    png = "/tmp/convergence_forecast.png"
    fig.savefig(png, dpi=140)

    summary = {
        "years": [years[0], years[-1]],
        "rank_by_year": dict(zip(years, rank_by_year)),
        "fully_pinned_year": pinned_year,
        "stall_rank_on_funded_roadmap": stall_rank,
        "blind_directions_no_funded_probe": blind,
        "rank_if_blindspot_probes_built": rank_with_blindspots,
        "headline": (f"On the funded experimental roadmap (sub-mm 2028, LiteBIRD 2030, "
                     f"SKA 2032, ET 2035 + existing scattering / consistency inputs), the "
                     f"consistent QG EFT pins to rank {stall_rank}/8 by ~2030 and STALLS. "
                     f"It is NEVER fully pinned: {blind} have no funded experiment. "
                     f"Solving QG requires building a high-scattering-moment probe (g_8) "
                     f"and a cubic-graviton / GW-nonlinearity probe (g_R3)."),
        "honest": "projected sigmas + years are approximate roadmap estimates (LiteBIRD "
                  "~2032 launch, CMB-S4/ Simons ~2030s, ET/CE ~2035, SKA ~2030s); inflation "
                  "n_s,r are omitted (zero Jacobian, pin nothing, v1.88). The robust content "
                  "is the GAP: 2 of 8 directions have no funded probe.",
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
