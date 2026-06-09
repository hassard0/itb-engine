"""v1.76 - Confronting the central prediction with real sub-mm gravity data.

The island center predicts a fractional Yukawa deviation of strength alpha ~ 1/3
at Compton wavelength lambda ~ 80 um (v1.74/v1.75). In the standard parametrization
        V(r) = -G m1 m2 / r * (1 + alpha * exp(-r/lambda)),
this is a CONCRETE, falsifiable point. We confront it with the published
Eot-Wash / Washington torsion-balance 95% CL exclusion of the gravitational
inverse-square law.

IMPORTANT PHYSICS: SCALAR_AMP = 1/3 is NOT a free toy number. In metric f(R)
gravity the extra scalar (scalaron) couples to matter with beta = 1/sqrt(6), giving
a fifth-force strength alpha = 2 beta^2 = 1/3 in the unscreened regime. The R^2
operator IS an f(R) theory, so alpha ~ 1/3 is the genuine prediction, and the
confrontation is physical, not an artifact of a toy prefactor.

Experimental exclusion curve (|alpha| excluded ABOVE the listed value, 95% CL),
read from the published figures -- DERIVED/READ here, not from Dr. M.:
  - Lee, Adelberger, et al., PRL 124, 101101 (2020), "New Test of the
    Gravitational Inverse-Square Law at the Submillimeter Scale" (strongest:
    |alpha|=1 excluded for lambda > 38.6 um).
  - Kapner et al., PRL 98, 021101 (2007) (|alpha|=1 excluded for lambda > 56 um).
  - Adelberger/Eot-Wash ISL compilation.
The points below are order-of-magnitude readings of the 2020 95% CL curve in the
(lambda, |alpha|) plane (log-log); the verdict is robust to ~factor-1.5 reading
uncertainty because the prediction misses the curve by ~an order of magnitude.
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")

# (lambda_um, alpha_excluded_above) 95% CL, Eot-Wash 2020-ish curve
EXCLUSION = [
    (20.0, 25.0),
    (30.0, 3.0),
    (38.6, 1.0),     # Lee 2020 headline: alpha=1 excluded for lambda>38.6um
    (50.0, 0.35),
    (56.0, 0.18),    # near Kapner 2007 alpha=1 -> note curve, here 95% band
    (60.0, 0.15),
    (70.0, 0.08),
    (80.0, 0.045),
    (100.0, 0.02),
    (150.0, 0.006),
    (200.0, 0.003),
]
_L = np.array([p[0] for p in EXCLUSION])
_A = np.array([p[1] for p in EXCLUSION])

# engine central prediction
ALPHA = 1.0 / 3.0
ALPHA_BAND = (1.0 / 6.0, 2.0 / 3.0)       # SCALAR_AMP realism band
LAMBDA = 80.0
LAMBDA_BAND = (60.0, 110.0)               # v1.75 robustness band

# lambda <-> g_R2:  lambda_um = (hbar c sqrt(6 g_R2) / E_Lambda) * 1e6
HBARC_eV_m = 1.973e-7
E_LAMBDA_DE = 2.4e-3


def alpha_excluded_at(lam_um):
    """Interpolate the 95% CL exclusion (log-log)."""
    return float(np.exp(np.interp(np.log(lam_um), np.log(_L), np.log(_A))))


def g_R2_for_lambda(lam_um):
    """Invert lambda_um = 82.2 * sqrt(6 g_R2) -> g_R2."""
    s = lam_um / ((HBARC_eV_m / E_LAMBDA_DE) * 1e6)   # = sqrt(6 g_R2)
    return (s * s) / 6.0


def main():
    bound_at_80 = alpha_excluded_at(LAMBDA)
    ratio = ALPHA / bound_at_80           # >1 means excluded
    excluded = ALPHA > bound_at_80

    # at alpha=1/3, what lambda is the exclusion boundary? (solve interp = 1/3)
    lam_grid = np.linspace(20, 200, 4000)
    bound_grid = np.array([alpha_excluded_at(l) for l in lam_grid])
    # boundary: largest lambda where bound >= ALPHA (excluded region is lambda above)
    below = lam_grid[bound_grid >= ALPHA]
    lam_boundary = float(below.max()) if below.size else None   # allowed if lambda<=this

    # does ANY corner of the prediction box escape exclusion?
    corners = [(ll, aa) for ll in LAMBDA_BAND for aa in ALPHA_BAND]
    corner_status = [{"lambda_um": ll, "alpha": round(aa, 3),
                      "excluded": aa > alpha_excluded_at(ll),
                      "bound": round(alpha_excluded_at(ll), 4)} for ll, aa in corners]
    box_fully_excluded = all(c["excluded"] for c in corner_status)

    # what g_R2 would be needed to reach the allowed region (lambda <= lam_boundary)?
    g_R2_allowed = g_R2_for_lambda(lam_boundary) if lam_boundary else None
    g_R2_at_80 = g_R2_for_lambda(80.0)

    # ---- exclusion plot ----
    fig, ax = plt.subplots(figsize=(9, 7))
    ll = np.linspace(20, 200, 500)
    bb = np.array([alpha_excluded_at(l) for l in ll])
    ax.fill_between(ll, bb, 1e3, color="#d62728", alpha=0.18,
                    label="excluded by Eot-Wash (95% CL)")
    ax.plot(ll, bb, "-", color="#d62728", lw=2,
            label="Eot-Wash 2020 exclusion (Lee et al)")
    # engine prediction box + point
    ax.add_patch(plt.Rectangle((LAMBDA_BAND[0], ALPHA_BAND[0]),
                               LAMBDA_BAND[1] - LAMBDA_BAND[0],
                               ALPHA_BAND[1] - ALPHA_BAND[0],
                               fill=True, facecolor="#1f77b4", alpha=0.25,
                               edgecolor="#1f77b4", lw=1.5,
                               label="engine prediction (realism band)"))
    ax.scatter([LAMBDA], [ALPHA], s=120, marker="*", color="#1f77b4",
               edgecolor="black", zorder=6, label=r"central prediction $\alpha=1/3$, $\lambda=80\,\mu$m")
    ax.axhline(ALPHA, color="#1f77b4", ls=":", lw=1, alpha=0.6)
    ax.axhline(1.0, color="gray", ls="--", lw=0.8, alpha=0.6)
    ax.annotate(r"f(R) scalaron $\alpha=1/3$", (185, ALPHA * 1.1), fontsize=9,
                color="#1f77b4", ha="right")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"Yukawa range $\lambda$ ($\mu$m)", fontsize=12)
    ax.set_ylabel(r"fifth-force strength $|\alpha|$ (relative to gravity)", fontsize=12)
    ax.set_title("v1.76  The central prediction vs real sub-mm gravity data\n"
                 f"predicted (80um, 1/3) is EXCLUDED by ~{ratio:.0f}x "
                 f"(bound at 80um: |alpha| < {bound_at_80:.3f})", fontsize=10)
    ax.set_xlim(20, 200); ax.set_ylim(1e-3, 1e2)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    png = "/tmp/submm_confrontation.png"
    fig.savefig(png, dpi=140)

    summary = {
        "prediction": {"alpha": round(ALPHA, 4), "lambda_um": LAMBDA,
                       "alpha_band": [round(a, 4) for a in ALPHA_BAND],
                       "lambda_band_um": list(LAMBDA_BAND),
                       "note": "alpha=1/3 is the physical f(R) scalaron coupling, not a free knob"},
        "exclusion_bound_at_80um": round(bound_at_80, 4),
        "exclusion_ratio_predicted_over_bound": round(ratio, 2),
        "VERDICT": ("EXCLUDED" if excluded else "ALLOWED"),
        "box_fully_excluded": bool(box_fully_excluded),
        "corner_status": corner_status,
        "alpha_1_3_allowed_below_lambda_um": round(lam_boundary, 1) if lam_boundary else None,
        "g_R2_at_80um": round(g_R2_at_80, 4),
        "g_R2_needed_to_be_allowed (<=)": round(g_R2_allowed, 4) if g_R2_allowed else None,
        "interpretation": (
            "The dark-energy-scale f(R) scalaron (alpha=1/3, lambda~80um) is "
            "EXCLUDED by Eot-Wash sub-mm gravity by ~an order of magnitude. This "
            "reproduces the known tension of unscreened dark-energy-scale scalar "
            "fifth forces. Resolutions: (a) heavier scalaron lambda<~%.0fum "
            "(g_R2<~%.2f), (b) a higher cutoff E_Lambda, or (c) chameleon screening."
            % (lam_boundary, g_R2_allowed) if lam_boundary else "n/a"),
        "citations": ["Lee et al PRL 124,101101 (2020)",
                      "Kapner et al PRL 98,021101 (2007)"],
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
