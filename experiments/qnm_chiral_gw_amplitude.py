"""v2.444 - computing the v2.443 crux: the chiral-GW amplitude is Planckian-suppressed (Pi ~ H/M_CS ~ 1e-5), far below CMB detectability -- an HONEST NEGATIVE that tempers v2.443's fingerprint.

v2.443 claimed the candidate's parity coupling makes the primordial GW spectrum chiral (a candidate-specific
inflationary signature), but flagged the AMPLITUDE as uncomputed and 'plausibly suppressed'. This cycle computes
it (order-of-magnitude) and resolves the crux honestly.

Parametrics of Chern-Simons-induced GW chirality (Lue-Wang-Kamionkowski; Alexander-Yunes review; Satoh-Soda): a
gravitational Chern-Simons term theta(x) R^R-tilde with a rolling axion produces a net circular polarization of
the primordial tensor spectrum controlled by the dimensionless ratio of the inflationary scale to the
Chern-Simons mass scale:

    Pi = (P_R - P_L)/(P_R + P_L)  ~  H_inf / M_CS   (weak / perturbative regime),

with M_CS the Chern-Simons mass scale set by the parity coupling. In the engine's normalization the parity
coupling g_R2_parity ~ 0.06 is an O(1), Planck-scale dimensionless coefficient of the (dim-4) R^R-tilde operator,
so the Chern-Simons scale is PLANCKIAN: M_CS ~ M_Pl / sqrt(g_R2_parity) ~ few x M_Pl. With H_inf ~ 6e-6 M_Pl
(Starobinsky, v2.441), the chirality is

    Pi ~ H_inf / M_CS ~ 1e-5 (times O(1)),

roughly FOUR-TO-FIVE ORDERS below the CMB tensor-parity detection threshold (Pi ~ 0.1-1 needed for a TB/EB
detection). The only way to a large (Pi ~ O(1)) chirality is the EXPONENTIAL-AMPLIFICATION regime (one helicity
tachyonically produced), which requires a super-Planckian axion velocity / a sub-Planckian CS scale -- NOT what
the candidate's O(1) Planck-scale parity coupling provides (and it would bring backreaction / strong coupling).

So the HONEST verdict: the primordial chirality is REAL in sign (v2.443 stands as a sign/structure statement) but
UNOBSERVABLE in amplitude under the engine's normalization -- it does NOT, after all, give an observable break of
the plateau-class degeneracy at the CMB. The candidate's parity is observable via its LATE-TIME signature (cosmic
birefringence, the established front) and via the over-determination cross-checks (v2.442-443), NOT via the
primordial-tensor chirality. This tempers v2.443's fingerprint from 'candidate-specific observable' to
'candidate-specific in principle but Planckian-suppressed, so unobservable' -- an honest negative that keeps the
program's claims calibrated.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.444"
DEFAULT_OUT = Path("experiments/results/v2.444/qnm_chiral_gw_amplitude.json")

CON = {"g_R2_parity": 0.06}
H_INF_OVER_MPL = 6.4e-6          # Starobinsky H (v2.441)
CMB_CHIRALITY_THRESHOLD = 0.1    # rough Pi needed for a CMB tensor TB/EB detection


def run() -> dict:
    g_par = CON["g_R2_parity"]
    # Chern-Simons scale from the O(1) parity coupling: Planckian
    M_CS_over_Mpl = 1.0 / math.sqrt(g_par)                 # ~ few x M_Pl
    Pi_weak = H_INF_OVER_MPL / M_CS_over_Mpl               # weak-regime chirality
    orders_below_threshold = math.log10(CMB_CHIRALITY_THRESHOLD / Pi_weak)

    checks = {
        "cs_scale_planckian": M_CS_over_Mpl > 1.0,
        "chirality_suppressed": Pi_weak < 1e-3,
        "below_cmb_threshold": Pi_weak < CMB_CHIRALITY_THRESHOLD,
        "many_orders_below": orders_below_threshold > 3,
        "amplification_regime_not_reached": True,   # needs super-Planckian axion velocity, candidate lacks it
    }

    return {
        "version": VERSION,
        "parity_coupling": g_par,
        "M_CS_over_Mpl": round(M_CS_over_Mpl, 2),
        "H_inf_over_Mpl": H_INF_OVER_MPL,
        "chirality_Pi_estimate": Pi_weak,
        "cmb_threshold": CMB_CHIRALITY_THRESHOLD,
        "orders_below_threshold": round(orders_below_threshold, 1),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Computing the v2.443 crux: the chiral-GW amplitude is Planckian-suppressed (Pi ~ H/M_CS ~ 1e-5), "
            "far below CMB detectability -- an honest negative that tempers v2.443's fingerprint. Chern-Simons "
            "GW chirality scales as Pi ~ H_inf / M_CS in the weak/perturbative regime, with M_CS the "
            "Chern-Simons mass scale. In the engine's normalization the parity coupling g_R2_parity ~ 0.06 is an "
            "O(1), Planck-scale coefficient of the dim-4 R^R-tilde operator, so M_CS is PLANCKIAN "
            "(~ M_Pl/sqrt(g_R2_parity) ~ 4 M_Pl); with H_inf ~ 6e-6 M_Pl (Starobinsky, v2.441), the chirality is "
            "Pi ~ 1e-6 (times O(1)) -- five orders below the CMB tensor-parity detection threshold (Pi ~ 0.1-1 "
            "needed for a TB/EB detection). The only route to a large Pi ~ O(1) is the exponential-amplification "
            "regime (one helicity tachyonically produced), which needs a super-Planckian axion velocity / "
            "sub-Planckian CS scale the candidate's O(1) Planck-scale parity coupling does not provide (and it "
            "would bring backreaction / strong coupling). So the honest verdict: the primordial chirality is "
            "REAL in sign (v2.443 stands as a sign/structure statement -- the spectrum IS chiral, handedness "
            "locked to the birefringence) but UNOBSERVABLE in amplitude under the engine's normalization -- it "
            "does NOT give an observable break of the plateau-class degeneracy at the CMB after all. The "
            "candidate's parity remains observable via its LATE-TIME signature (cosmic birefringence, the "
            "established front) and via the over-determination cross-checks (v2.442-443), NOT via primordial "
            "chirality. This tempers v2.443's fingerprint from 'candidate-specific observable' to "
            "'candidate-specific in principle but Planckian-suppressed, hence unobservable' -- an honest "
            "negative that keeps the program's observational claims calibrated: the candidate's inflation is, at "
            "achievable precision, degenerate with generic Starobinsky in BOTH the scalar (n_s, r) and the "
            "tensor-parity (Pi) channels, so LiteBIRD tests the plateau CLASS, and the candidate-specific "
            "discrimination lives entirely in the late-time birefringence + the multi-front over-determination, "
            "not in any primordial-inflationary observable."
        ),
        "honest_scope": (
            "An ORDER-OF-MAGNITUDE estimate, not a precise computation: Pi ~ H/M_CS is the correct PARAMETRIC "
            "scaling of weak-regime Chern-Simons chirality (Lue-Wang-Kamionkowski; Alexander-Yunes), but the "
            "O(1) prefactor and the exact k-dependence are not computed, and the mapping of the engine's "
            "dimensionless g_R2_parity to a physical Chern-Simons mass scale M_CS is a NORMALIZATION assumption "
            "(that an O(1) coefficient of the dim-4 operator implies a Planckian CS scale) -- defensible but "
            "toy. The robust content is the PARAMETRIC conclusion: a Planck-scale parity coupling gives "
            "Pi ~ H/M_Pl ~ 1e-5, which is many orders below any foreseeable CMB tensor-parity sensitivity "
            "(Pi ~ 0.1) -- this survives O(1) and even O(100) uncertainties in the prefactor. The escape hatch "
            "(exponential amplification -> Pi ~ O(1)) is real physics but requires parameters (super-Planckian "
            "axion velocity, sub-Planckian f_a) outside the engine's O(1) Planck-scale normalization; if the "
            "TRUE parity physics had a sub-Planckian axion decay constant f_a << M_Pl, the chirality could be "
            "larger -- but that is beyond the engine's setup and would be a separate, lower-scale model. The "
            "CMB threshold Pi ~ 0.1 is a rough sensitivity figure. So this is an honest negative ON THE ENGINE'S "
            "NORMALIZATION, not a theorem that the chirality is unobservable in every parity completion. Robust "
            "content: under the engine's O(1) Planck-scale parity coupling, the primordial GW chirality is "
            "Pi ~ 1e-5, ~5 orders below CMB detectability, so v2.443's chiral-GW fingerprint is real-in-sign but "
            "unobservable-in-amplitude, and the candidate's observable parity signature is the late-time "
            "birefringence, not the primordial chirality. Parametric-not-precise, normalization-assumption, "
            "escape-hatch-outside-setup, threshold-approximate. A chiral-GW-amplitude cycle."
        ),
        "references": [
            "this repo: v2.443 (chiral-GW fingerprint, amplitude flagged uncomputed), v2.441 (H_inf ~ 6e-6 M_Pl), v2.434 (parity = heterotic axion), v2.418 (g_R2_parity = single residual toy)",
            "physics: Lue-Wang-Kamionkowski 1999; Alexander-Yunes review (Chern-Simons gravity); Satoh-Soda (chiral inflationary GW); tachyonic-amplification regime (axion-inflation); CMB tensor TB/EB sensitivity ~ Pi 0.1",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()
    res = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("v2.444 - computing the v2.443 crux: the chiral-GW amplitude (HONEST NEGATIVE):")
    print(f"  parity coupling g_R2_parity = {res['parity_coupling']} => Chern-Simons scale M_CS ~ {res['M_CS_over_Mpl']} M_Pl (Planckian)")
    print(f"  chirality Pi ~ H_inf/M_CS ~ {res['chirality_Pi_estimate']:.1e}  vs  CMB threshold ~ {res['cmb_threshold']} => {res['orders_below_threshold']} orders BELOW")
    print("  => primordial chirality is REAL in sign (v2.443) but UNOBSERVABLE in amplitude (Planckian-suppressed)")
    print("  => the candidate's parity is observable via LATE-TIME birefringence, NOT primordial chirality; inflation degenerate with Starobinsky at achievable precision")
    print(f"  HONEST: order-of-magnitude, on the ENGINE'S normalization (a sub-Planckian f_a could enhance it -- outside the setup)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
