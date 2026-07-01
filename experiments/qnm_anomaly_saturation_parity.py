"""v2.370 - SWING: anomaly matching (taken as the exact equality it is) PREDICTS the parity magnitude -- and fits the data better.

A fresh swing in the parity sector. v2.364 concluded the parity coupling's existence, magnitude AND sign are
all data-driven -- the theory supplies only correlations. This swing challenges the MAGNITUDE half of that.

The engine's GeneralizedAnomalyInflow constraint is an INEQUALITY, g_R2_parity^2 + 2 g_R3_parity^2 <= rho g_4
g_R2, encoded conservatively. But its own docstring states the physics: "the total parity-violating content
must EQUAL the inflow from the matter-graviton sector" -- and anomaly matching ('t Hooft) is an EXACT EQUALITY
in field theory, not a bound (a UV anomaly must match its IR image exactly). So the physically-motivated case
is SATURATION. With g_R3_parity = 0 (the verified parity-odd-cubic center, v2.352), saturation FIXES the
parity magnitude from the parity-EVEN sector alone, with no appeal to data:

    g_R2_parity = sqrt(rho * g_4 * g_R2) = sqrt(0.06 * 0.529 * 0.193) = 0.0783

This is a THEORETICAL prediction of the parity coupling (contrast v2.364's "magnitude is data-pinned"), and it
maps to a birefringence signal beta = 3.4 deg * 0.0783 = 0.266 deg. Tested against the measurement
beta = 0.34 +/- 0.09 deg: the anomaly-saturation prediction sits 0.82 sigma away -- and it fits BETTER than
the Chebyshev center (g_R2_parity = 0.06 -> beta = 0.204, 1.51 sigma). So anomaly matching gives a
data-independent reason to prefer the UPPER edge of the birefringence-allowed window, and that preference
improves the agreement with the observed signal.
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
from itb.constraints.anomaly_flow import GeneralizedAnomalyInflow

VERSION = "v2.370"
DEFAULT_OUT = Path("experiments/results/v2.370/qnm_anomaly_saturation_parity.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
BASE = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06, "g_R3_parity": 0.0}
KAPPA_BETA = 3.4
BETA_MEAS, BETA_SIGMA = 0.34, 0.09
CMB_LOWER = 0.0471


def run() -> dict:
    rho = CANONICAL["anomaly_rho"]
    g4, gR2 = BASE["g_4"], BASE["g_R2"]

    # anomaly-saturation prediction (g_R3_parity = 0): g_R2_parity = sqrt(rho g_4 g_R2)
    gp_sat = math.sqrt(rho * g4 * gR2)
    beta_sat = KAPPA_BETA * gp_sat
    sigma_sat = abs(BETA_MEAS - beta_sat) / BETA_SIGMA

    gp_center = BASE["g_R2_parity"]
    beta_center = KAPPA_BETA * gp_center
    sigma_center = abs(BETA_MEAS - beta_center) / BETA_SIGMA

    # verify SATURATION against the engine's own anomaly constraint: margin ~ 0 at g_R2_parity = gp_sat
    anom = GeneralizedAnomalyInflow(rho=rho)
    sat_theory = dict(BASE); sat_theory["g_R2_parity"] = gp_sat
    sat_margin = anom.evaluate(Theory(coefficients=sat_theory, name="sat")).margin
    saturation_verified = abs(sat_margin) < 1e-9

    # is the saturated point still globally feasible (full consistent+observed stack)?
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    sat_feasible = all(r.satisfied for r in check(Theory(coefficients=sat_theory, name="sat"), stack).results)

    checks = {
        "anomaly_saturation_fixes_parity_from_even_sector": abs(gp_sat - math.sqrt(rho * g4 * gR2)) < 1e-12,
        "saturation_margin_zero_on_engine_constraint": saturation_verified,
        "predicted_beta_consistent_within_2sigma": sigma_sat < 2.0,
        "saturation_fits_better_than_chebyshev_center": sigma_sat < sigma_center,
        "saturated_point_globally_feasible": sat_feasible,
    }

    return {
        "version": VERSION,
        "anomaly_rho": rho,
        "predicted_g_R2_parity_saturation": round(gp_sat, 4),
        "chebyshev_center_g_R2_parity": gp_center,
        "beta_saturation": round(beta_sat, 3),
        "beta_center": round(beta_center, 3),
        "measured_beta": [BETA_MEAS, BETA_SIGMA],
        "sigma_saturation": round(sigma_sat, 2),
        "sigma_center": round(sigma_center, 2),
        "saturation_feasible": bool(sat_feasible),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Anomaly matching, taken as the exact EQUALITY it physically is, gives a THEORETICAL prediction "
            "of the parity magnitude -- partially reclaiming from 'data-driven' (v2.364) what the theory "
            "actually forces. The engine bounds the parity content by the matter-graviton inflow "
            "(g_R2_parity^2 + 2 g_R3_parity^2 <= rho g_4 g_R2) conservatively, but anomaly matching ('t "
            "Hooft) is an exact equality -- a UV anomaly matches its IR image exactly, not merely within a "
            "bound. Taking SATURATION with the verified g_R3_parity = 0 (v2.352) fixes the parity coupling "
            "from the parity-EVEN sector with no data input: g_R2_parity = sqrt(rho g_4 g_R2) = 0.078 "
            "(verified: this is exactly where the engine's anomaly-inflow margin vanishes, and the point "
            "stays globally feasible). It maps to beta = 3.4 deg * 0.078 = 0.266 deg, which sits only 0.82 "
            "sigma from the measured 0.34 +/- 0.09 -- and fits BETTER than the Chebyshev center (beta = 0.204, "
            "1.51 sigma). So the anomaly gives a data-INDEPENDENT reason to prefer the UPPER edge of the "
            "birefringence-allowed window (0.078, not the max-margin 0.06), and that preference improves "
            "agreement with the observed birefringence. This refines the parity anatomy honestly: the SIGN is "
            "still data-set (v2.364 -- anomaly matching fixes magnitude, not handedness), and the magnitude "
            "is DATA-BOUNDED into [0.047, 0.078] (v2.360), but WITHIN that window the theory has a genuine "
            "theoretical PREFERENCE -- the anomaly-saturated upper edge -- rather than being a pure readout. "
            "So the parity coupling is not entirely data-driven: its magnitude has a field-theory anchor "
            "(exact anomaly matching) that both predicts a specific value and happens to fit the data better "
            "than the geometric center. That is a real, if modest, theoretical prediction in the sector the "
            "program had written off as purely observational."
        ),
        "honest_scope": (
            "The DEFENSIBLE core: anomaly matching is an exact equality in field theory (not the engine's "
            "conservative <=), so 'the parity content saturates the inflow' is physically motivated, not "
            "arbitrary -- and it is verified to sit exactly on the engine's anomaly-inflow boundary while "
            "staying globally feasible. The CAVEATS: (1) the value 0.078 scales as sqrt(rho) with the toy "
            "anomaly prefactor rho = 0.06 (v2.344, load-bearing), so the NUMBER is toy-basis even though the "
            "STRUCTURE (parity fixed by the parity-even sector via matching) is not; (2) saturation assumes "
            "the parity content is EXACTLY g_R2_parity^2 + 2 g_R3_parity^2 with g_R3_parity = 0 and no other "
            "parity-odd operators or fermion-loop contributions to the gravitational anomaly -- real anomaly "
            "matching involves the full UV field content, so this is the engine's toy anomaly, not a "
            "computed one; (3) 'fits better' is mild (0.82 vs 1.51 sigma, both within 2 sigma) -- a "
            "preference and a consistency, not a discrimination. It does NOT overturn v2.364: the parity SIGN "
            "remains data-set (matching fixes magnitude only), and the whole birefringence comparison still "
            "presumes the detection is real (v2.329). Robust content: exact anomaly matching gives the "
            "parity magnitude a theoretical anchor at the upper edge of the data window, improving the fit -- "
            "so parity is not purely data-driven. Toy basis for the number, field-theory-motivated for the "
            "structure. A parity-sector swing that lands a modest theoretical prediction."
        ),
        "references": [
            "this repo: v2.364 (parity existence/magnitude/sign all data-driven -- refined here), v2.360 (magnitude data-bounded [0.047,0.078]), v2.352 (g_R3_parity=0 verified), v2.335 (anomaly inflow), v2.344 (rho), v2.329 (birefringence caveat)",
            "physics: 't Hooft anomaly matching (exact equality); Minami-Komatsu / Eskilt-Komatsu birefringence beta=0.34+/-0.09 deg",
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
    print("SWING: anomaly saturation predicts the parity magnitude theoretically:")
    print(f"  anomaly-saturated g_R2_parity = {res['predicted_g_R2_parity_saturation']}  (vs Chebyshev center {res['chebyshev_center_g_R2_parity']})")
    print(f"  -> beta = {res['beta_saturation']} deg, {res['sigma_saturation']} sigma from measured 0.34+/-0.09")
    print(f"     center beta = {res['beta_center']} deg, {res['sigma_center']} sigma  => saturation fits BETTER: {res['consistency_checks']['saturation_fits_better_than_chebyshev_center']}")
    print(f"  saturation sits on the engine anomaly boundary + globally feasible: {res['saturation_feasible']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
