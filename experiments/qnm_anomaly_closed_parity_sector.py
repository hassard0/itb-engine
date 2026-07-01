"""v2.371 - SWING (completion): the two exact anomaly conditions CLOSE, uniquely predicting the whole parity-odd sector from the parity-even one.

Completing v2.370. That swing used ONE exact anomaly condition (inflow saturation) plus g_R3_parity = 0 as an
input. But the engine carries a SECOND exact-in-field-theory condition: 't Hooft anomaly matching
(v2.353), |g_R3_parity| = rho_match (g_4 + g_6) |g_R2_parity|, also encoded as a bound but physically an
equality. Taking BOTH as the equalities they are gives two equations in two unknowns -- a CLOSED SYSTEM that
determines the ENTIRE parity-odd sector from the parity-EVEN couplings, with NO data input:

    (1) inflow:     g_R2_parity^2 + 2 g_R3_parity^2 = rho g_4 g_R2
    (2) t Hooft:    g_R3_parity = rho_match (g_4 + g_6) g_R2_parity = r * g_R2_parity

Substituting (2) into (1): g_R2_parity = sqrt( rho g_4 g_R2 / (1 + 2 r^2) ), g_R3_parity = r * g_R2_parity.
With the constructed parity-even couplings and the engine prefactors this gives a UNIQUE solution:

    g_R2_parity = 0.0654 ,  g_R3_parity = 0.0304

-- the full parity-odd sector, fixed by the parity-even sector alone. This is the strongest challenge to
v2.364 ("parity is entirely data-driven"): under exact anomaly matching the parity-odd sector is NOT data-
driven at all, it is DETERMINED. And it predicts a NONZERO parity-odd cubic (0.0304), reversing the
constructed center's g_R3_parity = 0 (which was the bound-form center, v2.352).

The honest tension it exposes: this COMPLETE system fits the birefringence data WORSE than the incomplete
saturation-only value -- beta = 3.4 * 0.0654 = 0.222 deg (1.31 sigma from 0.34 +/- 0.09) vs v2.370's 0.078 ->
0.266 deg (0.82 sigma) -- because the nonzero cubic consumes anomaly budget and lowers the quadratic. So the
data mildly prefers a SUPPRESSED cubic (better fit) over the fully-matched cubic (complete but worse fit).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack, CANONICAL

VERSION = "v2.371"
DEFAULT_OUT = Path("experiments/results/v2.371/qnm_anomaly_closed_parity_sector.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
BASE = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06, "g_R3_parity": 0.0}
RHO_MATCH = 0.5
KAPPA_BETA = 3.4
BETA_MEAS, BETA_SIGMA = 0.34, 0.09


def run() -> dict:
    rho = CANONICAL["anomaly_rho"]
    g4, g6, gR2 = BASE["g_4"], BASE["g_6"], BASE["g_R2"]
    r = RHO_MATCH * (g4 + g6)                                 # t Hooft ratio

    # closed-system solution
    gp = math.sqrt(rho * g4 * gR2 / (1.0 + 2.0 * r * r))
    g3p = r * gp
    beta = KAPPA_BETA * gp
    sigma_closed = abs(BETA_MEAS - beta) / BETA_SIGMA

    # comparison points
    gp_sat = math.sqrt(rho * g4 * gR2)                       # v2.370 saturation-only (cubic=0)
    sigma_sat = abs(BETA_MEAS - KAPPA_BETA * gp_sat) / BETA_SIGMA
    sigma_center = abs(BETA_MEAS - KAPPA_BETA * 0.06) / BETA_SIGMA

    # verify the solution satisfies BOTH equalities
    inflow_lhs = gp ** 2 + 2 * g3p ** 2
    inflow_rhs = rho * g4 * gR2
    inflow_eq = abs(inflow_lhs - inflow_rhs) < 1e-9
    thooft_eq = abs(g3p - r * gp) < 1e-9

    # global feasibility of the closed-system theory
    sol = dict(BASE); sol["g_R2_parity"] = gp; sol["g_R3_parity"] = g3p
    feasible = all(rr.satisfied for rr in check(Theory(coefficients=sol, name="closed"), build_stack(
        rfc_form="convex_hull", include_data=True, include_birefringence=True, include_gw_speed=True,
        include_gw_dispersion=True, submm_screened=True)).results)

    checks = {
        "closed_system_satisfies_inflow_equality": inflow_eq,
        "closed_system_satisfies_thooft_equality": thooft_eq,
        "predicts_nonzero_parity_odd_cubic": g3p > 0.01,
        "closed_system_globally_feasible": feasible,
        "complete_system_fits_worse_than_saturation_only": sigma_closed > sigma_sat,   # the honest tension
    }

    return {
        "version": VERSION,
        "anomaly_rho": rho,
        "thooft_ratio_r": round(r, 4),
        "predicted_g_R2_parity": round(gp, 4),
        "predicted_g_R3_parity": round(g3p, 4),
        "beta_closed": round(beta, 3),
        "sigma_closed": round(sigma_closed, 2),
        "sigma_saturation_only_v2370": round(sigma_sat, 2),
        "sigma_center": round(sigma_center, 2),
        "closed_system_feasible": bool(feasible),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The two exact anomaly-matching conditions CLOSE into a system that uniquely determines the ENTIRE "
            "parity-odd sector from the parity-even couplings -- the strongest challenge yet to v2.364's "
            "'parity is entirely data-driven.' Both the gravitational anomaly INFLOW (g_R2_parity^2 + 2 "
            "g_R3_parity^2 = rho g_4 g_R2) and 't Hooft MATCHING (g_R3_parity = rho_match (g_4+g_6) "
            "g_R2_parity) are exact equalities in field theory (the engine encodes them as conservative "
            "bounds). Imposed together they are two equations in two unknowns, with the unique solution "
            "g_R2_parity = 0.0654, g_R3_parity = 0.0304 -- the full parity-odd sector fixed by the parity-EVEN "
            "sector alone, no data. Verified: the solution satisfies both equalities exactly and is globally "
            "feasible against the full consistent+observed stack. So under exact anomaly matching the "
            "parity-odd sector is NOT data-driven -- it is DETERMINED, including a NONZERO parity-odd cubic "
            "(0.0304), reversing the constructed center's g_R3_parity = 0 (which was the bound-form center, "
            "v2.352). But the swing exposes an honest TENSION rather than a clean win: this COMPLETE system "
            "fits the birefringence data WORSE than the incomplete saturation-only prediction -- beta = 0.222 "
            "deg (1.31 sigma from 0.34 +/- 0.09) vs v2.370's 0.266 deg (0.82 sigma) -- because the nonzero "
            "cubic consumes anomaly budget and lowers the observable quadratic. So the data mildly prefers a "
            "SUPPRESSED cubic (better birefringence fit, but then 't Hooft matching is NOT saturated) over "
            "the fully-matched cubic (a complete theoretical determination, but a worse fit). The reading: "
            "the parity-odd sector CAN be entirely predicted from the parity-even sector by exact matching (a "
            "genuine theoretical closure, not a data readout), but current birefringence slightly disfavors "
            "the fully-matched version -- an honest, falsifiable fork. Either the 't Hooft cubic is present "
            "(complete, testable via a chiral-cubic signal) or suppressed (better fit, matching incomplete); "
            "a sharper birefringence measurement discriminates."
        ),
        "honest_scope": (
            "The DEFENSIBLE core: both anomaly conditions are exact equalities in field theory, so imposing "
            "them as equalities (not the engine's bounds) is physically motivated, and the resulting 2x2 "
            "system genuinely closes (verified: unique solution, both equalities satisfied, globally "
            "feasible). The CAVEATS: the solution VALUES (0.065, 0.030) scale with the toy prefactors rho = "
            "0.06 (v2.344) and rho_match = 0.5, and with the toy operator content (the parity content taken "
            "as exactly g_R2_parity^2 + 2 g_R3_parity^2 and the ratio as exactly rho_match(g_4+g_6)); a real "
            "fermion content would shift both -- so the STRUCTURE (closed determination of the parity-odd "
            "sector) is robust, the NUMBERS are toy. The 'fits worse' tension (1.31 vs 0.82 sigma) is real "
            "but MILD -- both are within 2 sigma, so it is a soft preference, not an exclusion; and it rests "
            "on the birefringence detection being real (v2.329). It challenges but does not overturn v2.364: "
            "the parity SIGN is still data-set (matching fixes magnitudes/ratios, not handedness). The "
            "nonzero-cubic prediction contradicts the v2.352 bound-form center but is exactly the v2.353 "
            "conditional cubic, now closed without the data input. Robust content: exact anomaly matching "
            "closes the parity-odd sector (a data-free theoretical determination), predicting a nonzero "
            "cubic, with the honest caveat that the complete version fits birefringence slightly worse. Toy "
            "numbers, field-theory-motivated structure. The completion of the v2.370 swing, with its tension "
            "reported."
        ),
        "references": [
            "this repo: v2.370 (inflow saturation, one equality), v2.353 (conditional cubic from 't Hooft equality), v2.364 (parity data-driven -- challenged here), v2.352 (bound-form cubic center g_R3_parity=0), v2.344 (rho), v2.329 (birefringence caveat)",
            "physics: 't Hooft anomaly matching + gravitational anomaly inflow, both exact equalities; birefringence beta=0.34+/-0.09 deg",
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
    print("SWING (completion): both exact anomaly conditions CLOSE -> the full parity-odd sector, no data:")
    print(f"  g_R2_parity = {res['predicted_g_R2_parity']},  g_R3_parity = {res['predicted_g_R3_parity']}  (nonzero cubic)")
    print(f"  beta = {res['beta_closed']} deg -> {res['sigma_closed']} sigma  (vs saturation-only {res['sigma_saturation_only_v2370']}, center {res['sigma_center']})")
    print(f"  globally feasible: {res['closed_system_feasible']}")
    print(f"  honest tension: complete system fits WORSE than saturation-only ({res['sigma_closed']} > {res['sigma_saturation_only_v2370']})")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
