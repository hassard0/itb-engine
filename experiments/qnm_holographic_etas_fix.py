"""v2.462 - bug-fix in the holographic sector: the eta/s observable was a factor-of-2 error (1 - 8 lambda instead of the correct Brigante 1 - 4 lambda), inconsistent with holographic_ac.py and with the famous 16/25 KSS-violation floor. Corrected + verified consistent.

Examining the holographic sector (off the axion/dark-energy track) surfaced a genuine internal inconsistency: the
candidate's shear-viscosity 'prediction' eta/s was implemented two different ways.

  * src/itb/holographic_ac.py:            eta/s = (1/4pi)(1 - 4 lambda_GB)   -- CORRECT (Brigante-Liu-Myers-
    Shenker-Yaida 2008); its docstring even states the famous '16/25 KSS-violation floor' (1 - 4*9/100 = 16/25).
  * src/itb/gravitational_observables.py: eta/s = (1/4pi)(1 - 8 lambda_GB)   -- WRONG (factor of 2), and it stated
    a wrong causality floor 'eta/s >= 0.28' instead of the correct 16/25 = 0.64.

The two disagreed on the candidate's value (g_R2 ~ 0.19): the wrong (1-8L) gave eta/s ~ 0.665, the correct (1-4L)
gives eta/s ~ 0.833 -- and 0.83 is the value the README/foundational summary always quoted (~0.81), so the
gravitational_observables implementation was the outlier error. Fixed gravitational_observables.py to the correct
1 - 4 lambda (predict + jacobian + docstring + causality floor), consistent with holographic_ac.py and Brigante;
updated the two hard-coded test assertions (test_holographic_etas.py).

After the fix (verified): candidate g_R2 = 0.19 -> eta/s = 0.833 KSS-units (KSS-violating, < 1); the largest
framework g_R2 = 0.4 -> eta/s = 0.648, sitting at the Brigante causality floor 16/25 = 0.64. The two modules now
agree. This is a holographic PORTRAIT contingent on an assumed Gauss-Bonnet AdS/CFT dual (a what-if, as
holographic_ac.py flags) and the lam_map ~ 0.22 mapping is order-of-magnitude, so the robust content is the
ORDERING by g_R2 and the KSS-violating sign, not the exact value -- but at least the value is now correct and
internally consistent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")
from itb.theory import Theory
from itb.gravitational_observables import HolographicEtaOverS
from itb.holographic_ac import lambda_GB, eta_over_s_kss

VERSION = "v2.462"
DEFAULT_OUT = Path("experiments/results/v2.462/qnm_holographic_etas_fix.json")

MU = 0.22
G_R2_CANDIDATE = 0.19
G_R2_MAX = 0.40


def run() -> dict:
    obs = HolographicEtaOverS(lam_map=MU)
    # gravitational_observables value
    etas_gravobs_cand = float(obs.predict(Theory(coefficients={"g_R2": G_R2_CANDIDATE}))[0])
    etas_gravobs_max = float(obs.predict(Theory(coefficients={"g_R2": G_R2_MAX}))[0])
    # holographic_ac value (independent module)
    etas_ac_cand = eta_over_s_kss(lambda_GB(G_R2_CANDIDATE, MU))
    etas_ac_max = eta_over_s_kss(lambda_GB(G_R2_MAX, MU))

    brigante_floor = 16.0 / 25.0

    checks = {
        "two_modules_consistent": abs(etas_gravobs_cand - etas_ac_cand) < 1e-9,
        "candidate_etas_kss_violating": 0 < etas_gravobs_cand < 1.0,
        "candidate_etas_matches_quoted_value": abs(etas_gravobs_cand - 0.83) < 0.02,   # ~0.81-0.83
        "largest_gR2_at_brigante_floor": abs(etas_gravobs_max - brigante_floor) < 0.02,
        "not_the_old_wrong_value": abs(etas_gravobs_cand - 0.665) > 0.1,               # not the old 1-8L value
    }

    return {
        "version": VERSION,
        "eta_over_s_candidate": round(etas_gravobs_cand, 4),
        "eta_over_s_candidate_holographic_ac_module": round(etas_ac_cand, 4),
        "eta_over_s_largest_gR2": round(etas_gravobs_max, 4),
        "brigante_floor": round(brigante_floor, 4),
        "old_wrong_value_1_minus_8L": round(1.0 - 8.0 * MU * G_R2_CANDIDATE, 4),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Bug-fix in the holographic sector: the candidate's eta/s observable was a factor-of-2 error "
            "(1 - 8 lambda instead of the correct Brigante 1 - 4 lambda), inconsistent with holographic_ac.py "
            "and with the famous 16/25 KSS-violation floor -- now corrected and verified consistent. Examining "
            "the holographic sector (off the axion/dark-energy track) surfaced that the shear-viscosity "
            "prediction eta/s was implemented two different ways: holographic_ac.py used the correct "
            "eta/s = (1/4pi)(1 - 4 lambda_GB) (Brigante-Liu-Myers-Shenker-Yaida 2008, whose docstring even "
            "states the 16/25 floor), while gravitational_observables.py used (1/4pi)(1 - 8 lambda_GB) -- a "
            "factor-of-2 error that also mis-stated the causality floor as 0.28 instead of 16/25 = 0.64. The two "
            "disagreed on the candidate's value: the wrong (1-8L) gave eta/s ~ 0.665, the correct (1-4L) gives "
            "eta/s ~ 0.833 -- and ~0.83 is the value the summary always quoted (~0.81), so "
            "gravitational_observables was the outlier error. Fixed it to 1 - 4 lambda (predict + jacobian + "
            "docstring + floor), consistent with holographic_ac.py and Brigante, and updated the two hard-coded "
            "test assertions. Verified: candidate g_R2 = 0.19 -> eta/s = 0.833 KSS-units (KSS-violating), and "
            "the largest framework g_R2 = 0.4 -> eta/s = 0.648 at the Brigante causality floor 16/25 = 0.64; the "
            "two modules now agree. The eta/s remains a holographic PORTRAIT contingent on an assumed "
            "Gauss-Bonnet AdS/CFT dual (a what-if, as holographic_ac.py flags), with the lam_map ~ 0.22 mapping "
            "order-of-magnitude -- so the robust content is the ORDERING by g_R2 and the KSS-violating sign, not "
            "the exact value -- but the value is now correct and internally consistent. A concrete "
            "internal-consistency bug found and fixed by cross-checking two modules against the published "
            "Brigante result, exactly the kind of latent error the honest-scrutiny discipline is meant to catch."
        ),
        "honest_scope": (
            "This is a CODE / physics-consistency FIX, not a new prediction: it corrects the eta/s observable to "
            "the standard Brigante form and makes the two engine modules agree. The eta/s observable is still a "
            "holographic PORTRAIT -- it assumes the candidate has a Gauss-Bonnet AdS/CFT dual, which is NOT "
            "established (the candidate is a flat-space EFT); holographic_ac.py already flags this as a "
            "'what-if'. The lam_map = 0.22 (g_R2 -> lambda_GB) is an order-of-magnitude toy map chosen so the "
            "largest g_R2 sits under the causality bound, so the specific eta/s = 0.833 is toy-normalized; the "
            "robust content is the ORDERING (larger g_R2 => lower eta/s) and the KSS-violating SIGN (eta/s < "
            "1/4pi for g_R2 > 0), not the precise number. The Brigante 1 - 4 lambda form is the correct "
            "linear-order AdS5/GB result, but the candidate's g_R2 is not literally a bulk GB coupling -- the "
            "map is the toy part. The fix does not change any CONSTRAINT (eta/s is an observable output, not a "
            "feasibility constraint), so the candidate / feasible region is unaffected; only the reported eta/s "
            "value changes (0.665 -> 0.833). Robust content: the holographic eta/s observable had a "
            "factor-of-2 error (1-8 lambda) inconsistent with the correct Brigante 1-4 lambda in holographic_ac.py; "
            "fixed to 1-4 lambda, giving a consistent candidate eta/s ~ 0.83 (KSS-violating) with the largest "
            "g_R2 at the 16/25 causality floor -- an internal-consistency correction to a what-if holographic "
            "portrait, robust content being the ordering and KSS-violating sign. Code-fix-not-new-prediction, "
            "holographic-portrait-what-if, lam_map-toy, observable-not-constraint-so-region-unaffected. A "
            "holographic-etas-fix cycle."
        ),
        "references": [
            "this repo: src/itb/holographic_ac.py (correct 1-4 lambda), src/itb/gravitational_observables.py (the fixed observable), v1.67/v1.72 (holographic sector), v2.385 (ghost-safe Weyl^2)",
            "physics: Brigante-Liu-Myers-Shenker-Yaida 2008 (eta/s = (1/4pi)(1-4 lambda_GB), causality floor 16/25); KSS bound eta/s >= 1/4pi; Myers-Sinha (a, c from lambda_GB)",
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
    print("v2.462 - holographic eta/s bug-fix (1 - 8 lambda -> correct Brigante 1 - 4 lambda):")
    print(f"  candidate g_R2=0.19: eta/s = {res['eta_over_s_candidate']} (KSS-violating); holographic_ac module agrees: {res['eta_over_s_candidate_holographic_ac_module']}")
    print(f"  largest g_R2=0.4: eta/s = {res['eta_over_s_largest_gR2']} (at Brigante floor 16/25 = {res['brigante_floor']})")
    print(f"  old WRONG value (1-8 lambda) was {res['old_wrong_value_1_minus_8L']} -- corrected")
    print("  => two modules now consistent; eta/s remains a what-if holographic portrait (robust content = ordering + KSS-violating sign)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
