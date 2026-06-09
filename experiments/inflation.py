"""v1.86 - R^2 is the inflaton: the engine's g_R2 sector as Starobinsky inflation.

The SAME R^2 operator the engine uses as a dark-energy-scale scalaron (low cutoff
-> sub-mm fifth force, v1.77) is, at a HIGH cutoff (scalaron mass M ~ 3e13 GeV fixed
by the Planck amplitude A_s), the Starobinsky inflaton -- the observationally
favored single-field model. We plot the Starobinsky (n_s, r) prediction (N=50-60)
against the Planck 2018 + BICEP/Keck 2021 allowed region and the excluded classic
models, and state the multi-scale story honestly.

Run on Vulcan:  python experiments/inflation.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

sys.path.insert(0, "src")

from itb.gravitational_observables import StarobinskyInflation
from itb.predict import FRAMEWORKS

# Planck 2018 + BICEP/Keck 2021 (approx): n_s = 0.9649 +/- 0.0042, r < 0.036 (95%)
NS_MEAS, NS_SIG = 0.9649, 0.0042
R_UPPER = 0.036


def main():
    Ns = np.arange(50, 61)
    staro = [(1 - 2.0 / N, 12.0 / N ** 2) for N in Ns]
    ns55, r55 = StarobinskyInflation(55).n_s(), StarobinskyInflation(55).r()

    # consistency with Planck + BK
    ns_ok = abs(ns55 - NS_MEAS) < 2 * NS_SIG
    r_ok = r55 < R_UPPER
    consistent = ns_ok and r_ok

    # every consistent framework has g_R2 > 0 -> R^2 inflation viable
    viable = {name: StarobinskyInflation().viable(fw.encode())
              for name, fw in FRAMEWORKS.items()}
    n_viable = sum(viable.values())

    # ---- n_s - r plane ----
    fig, ax = plt.subplots(figsize=(10, 7))
    # Planck+BK allowed region (approx 95%): n_s band, r below upper limit
    ax.axhspan(0, R_UPPER, xmin=0, xmax=1, color="#cfe8cf", alpha=0.0)  # placeholder
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((NS_MEAS - 2 * NS_SIG, 0.0), 4 * NS_SIG, R_UPPER,
                           facecolor="#9ecae1", alpha=0.35,
                           label="Planck+BK allowed (95%)"))
    ax.axvline(NS_MEAS, color="#08519c", ls=":", lw=1)
    ax.axhline(R_UPPER, color="#08519c", ls="--", lw=1, label="BK18 r < 0.036")

    # Starobinsky line (N=50-60)
    sx = [s[0] for s in staro]; sy = [s[1] for s in staro]
    ax.plot(sx, sy, "-", color="#d62728", lw=2.5, zorder=5,
            label="Starobinsky R^2 (N=50-60)")
    ax.scatter([ns55], [r55], s=110, color="#d62728", edgecolor="black", zorder=6,
               marker="*", label=f"engine R^2 sector (N=55): n_s={ns55:.3f}, r={r55:.4f}")
    for N in (50, 60):
        ax.annotate(f"N={N}", (1 - 2.0 / N, 12.0 / N ** 2),
                    textcoords="offset points", xytext=(4, 4), fontsize=8)

    # excluded / contrast models
    ax.scatter([0.967], [0.13], s=80, color="#7f2704", marker="X", zorder=5)
    ax.annotate("m^2 phi^2 (EXCLUDED)", (0.967, 0.13), textcoords="offset points",
                xytext=(6, -2), fontsize=8, color="#7f2704")
    ax.add_patch(Ellipse((0.95, 0.07), 0.02, 0.06, facecolor="#ff7f0e", alpha=0.25))
    ax.annotate("natural inflation\n(disfavored)", (0.945, 0.085), fontsize=7.5,
                color="#ff7f0e")
    ax.annotate("alpha-attractors / Higgs\n(~ Starobinsky)", (0.962, 0.012),
                fontsize=7.5, color="#2ca02c")

    ax.set_xlabel(r"scalar spectral index $n_s$", fontsize=12)
    ax.set_ylabel(r"tensor-to-scalar ratio $r$", fontsize=12)
    ax.set_xlim(0.94, 0.98); ax.set_ylim(0, 0.16)
    ax.set_title("v1.86  R^2 is the inflaton: the engine's g_R2 sector is "
                 "Starobinsky inflation\nin the Planck+BICEP/Keck sweet spot "
                 "(one operator, two epochs)", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    png = "/tmp/inflation.png"
    fig.savefig(png, dpi=140)

    summary = {
        "starobinsky_N55": {"n_s": round(ns55, 4), "r": round(r55, 5)},
        "starobinsky_N_range_50_60": {"n_s": [round(s[0], 4) for s in staro][::5],
                                      "r": [round(s[1], 5) for s in staro][::5]},
        "planck_bk": {"n_s": f"{NS_MEAS} +/- {NS_SIG}", "r_upper_95": R_UPPER},
        "consistent_with_data": bool(consistent),
        "n_s_within_2sigma": bool(ns_ok), "r_below_upper": bool(r_ok),
        "frameworks_inflation_viable_gR2_positive": f"{n_viable}/{len(FRAMEWORKS)}",
        "multi_scale_story": "The same dimensionless R^2 coefficient g_R2 gives (a) "
            "Starobinsky inflation at a HIGH cutoff (scalaron mass ~3e13 GeV, fixed by "
            "A_s) and (b) the dark-energy-scale scalaron / sub-mm fifth force at a LOW "
            "cutoff (~meV). One operator, two epochs -- but a single real theory picks "
            "ONE scale; the engine's g_R2 is the common dimensionless coefficient.",
        "honest_caveat": "n_s and r are set by N (e-folds / plateau geometry), NOT by "
            "the dimensionless g_R2. The robust content: a POSITIVE R^2 term (g_R2>0, "
            "which every consistent framework has) gives the plateau potential -> the "
            "Planck sweet spot. R^2 inflation is the/among the best-fit models.",
        "citations": ["Starobinsky 1980 PLB 98,171", "Planck 2018 Akrami et al A&A 641,A6",
                      "BICEP/Keck 2021 Ade et al PRL 127,261802"],
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
