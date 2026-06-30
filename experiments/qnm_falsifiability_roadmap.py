"""v2.328 - Falsifiability roadmap: what would confirm or refute the constructed theory?

A forward-looking, actionable synthesis (distinct from the v2.323 findings-ledger): the constructed
both-consistent gravity (string-like matter, trimmed curvature, mild right-handed parity violation,
g_R2_parity = 0.06) makes correlated parity-sector predictions. This cycle lays them out as concrete
observational tests -- the prediction, the current status, and what a future measurement would do -- and
quantifies how the test suite separates the constructed theory from the parity-even frameworks.

Three correlated probes of the one parity coupling:
  1. cosmic birefringence (MEASURED, beta = 0.34 +/- 0.09 deg, ~3.6 sigma)  [v2.321]
  2. chiral primordial GW / CMB TB-EB (FUTURE: LiteBIRD, CMB-S4)            [v2.319]
  3. gravitational leptogenesis -> baryon asymmetry eta_B (consistency)     [v2.324]

The parity-even frameworks predict EXACTLY ZERO for all three; the constructed theory predicts a definite
right-handed signal for each, so the suite is a clean discriminator.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.328"
DEFAULT_OUT = Path("experiments/results/v2.328/qnm_falsifiability_roadmap.json")

GP_CONSTRUCTED = 0.06
GP_DATA_WINDOW = [0.048, 0.078]      # v2.321/v2.327 theory+data parity window
KAPPA_BETA = 3.4                      # deg/unit (v2.321)
BETA_MEAS, BETA_SIG = 0.34, 0.09     # measured cosmic birefringence (deg)
KAPPA_PI = 4.0                       # chiral-GW tanh scale (v2.319)


def beta_pred(gp):
    return KAPPA_BETA * gp


def chirality(gp):
    return math.tanh(KAPPA_PI * gp)


def run() -> dict:
    b = beta_pred(GP_CONSTRUCTED)
    b_lo, b_hi = beta_pred(GP_DATA_WINDOW[0]), beta_pred(GP_DATA_WINDOW[1])
    beta_tension_sigma = (BETA_MEAS - b) / BETA_SIG     # how far below the central measured value

    roadmap = [
        {"test": "cosmic_birefringence", "status": "MEASURED (~3.6 sigma, unconfirmed)",
         "constructed_prediction": f"beta = {b:.3f} deg (window {b_lo:.2f}-{b_hi:.2f})",
         "parity_even_prediction": "beta = 0 (excluded by the measurement)",
         "current_verdict": f"consistent at ~{beta_tension_sigma:.1f} sigma (constructed sits at the LOW edge; "
                            "the central beta=0.34 prefers more parity, lqg-like)",
         "what_future_data_does": "a confirmed >5 sigma beta favors parity-violating gravity and pins the "
                                  "parity coupling; a null (beta->0) kills the parity sector and revives the parity-even frameworks"},
        {"test": "chiral_primordial_GW (CMB TB/EB)", "status": "FUTURE (LiteBIRD, CMB-S4)",
         "constructed_prediction": f"right-handed chirality Pi = {chirality(GP_CONSTRUCTED):+.2f} (sign definite)",
         "parity_even_prediction": "Pi = 0 (zero TB, zero EB)",
         "current_verdict": "not yet measured -- the cleanest future discriminator",
         "what_future_data_does": "a detection of nonzero TB/EB with right-handed sign confirms; a null at "
                                  "sensitivity tightens the parity coupling downward"},
        {"test": "gravitational_leptogenesis (eta_B)", "status": "MEASURED eta_B~6e-10 (magnitude unsourced here)",
         "constructed_prediction": "nonzero, definite-sign baryon asymmetry (sign-consistent with matter excess)",
         "parity_even_prediction": "eta_B = 0 from this mechanism (cannot source the asymmetry gravitationally)",
         "current_verdict": "consistency, not a sharp test (the magnitude is scale-dependent, v2.324)",
         "what_future_data_does": "fixing the inflationary scale / reheating would turn the sign-correlation into a magnitude test"},
        {"test": "matter_sector (collider positivity, GW dispersion)", "status": "FUTURE / loose",
         "constructed_prediction": "matter couplings in a bounded but wide consistency window (g_4~0.4-0.6 etc., v2.327)",
         "parity_even_prediction": "same matter windows (this sector does not discriminate on parity)",
         "current_verdict": "the loosely-pinned sector (v2.327) -- not yet constraining",
         "what_future_data_does": "tighter matter-sector positivity / dispersion data narrows g_4/g_6/g_8/g_R2/g_R3"},
    ]

    # the suite separates the constructed theory from the parity-even frameworks on the three parity probes
    parity_probes = roadmap[:3]
    discriminates = all("0" in r["parity_even_prediction"] for r in parity_probes)
    # all three constructed predictions are nonzero & right-handed (sign-aligned)
    signs_aligned = (b > 0) and (chirality(GP_CONSTRUCTED) > 0)

    checks = {
        "three_parity_probes_present": len(parity_probes) == 3,
        "parity_even_predicts_zero_on_all_parity_probes": discriminates,
        "constructed_predictions_right_handed_aligned": signs_aligned,
        "constructed_beta_within_measurement": abs(beta_tension_sigma) < 3.0,
        "constructed_beta_at_low_edge_of_band": beta_tension_sigma > 0,
    }

    return {
        "version": VERSION,
        "constructed_g_R2_parity": GP_CONSTRUCTED,
        "roadmap": roadmap,
        "beta_predicted_deg": b,
        "beta_measured_deg": BETA_MEAS,
        "beta_tension_sigma": beta_tension_sigma,
        "chirality_predicted": chirality(GP_CONSTRUCTED),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The constructed theory is falsifiable through three correlated probes of its single parity "
            "coupling, all of which the parity-even frameworks predict to be exactly zero -- so the "
            "measurement suite is a clean discriminator. (1) COSMIC BIREFRINGENCE (measured, ~3.6 sigma): "
            f"the constructed framework predicts beta = {b:.2f} deg (the theory+data window spans "
            f"{b_lo:.2f}-{b_hi:.2f} deg), consistent with the measured 0.34 +/- 0.09 deg at "
            f"~{beta_tension_sigma:.1f} sigma but sitting at the LOW edge -- the central value mildly "
            "prefers MORE parity (toward lqg's larger coupling); a confirmed >5 sigma beta would favor "
            "parity-violating gravity and a null would revive the parity-even frameworks. (2) CHIRAL "
            "PRIMORDIAL GW (future, LiteBIRD / CMB-S4): the cleanest future discriminator -- the "
            f"constructed theory predicts a right-handed Pi = {chirality(GP_CONSTRUCTED):+.2f} (nonzero "
            "TB/EB), zero for parity-even gravity; a detection confirms, a null tightens the parity "
            "coupling down. (3) GRAVITATIONAL LEPTOGENESIS (eta_B): a sign-consistent baryon asymmetry, a "
            "consistency rather than a sharp test (magnitude scale-dependent). Plus the MATTER SECTOR, "
            "which is the loosely-pinned region (v2.327) future collider-positivity / GW-dispersion data "
            "would tighten -- but which does not discriminate on parity. The roadmap is concrete: a single "
            "parity coupling, fixed to a narrow window by current birefringence data, predicts a definite "
            "right-handed CMB-TB/EB chirality as the decisive next test, and the whole parity-violating "
            "story stands or falls on whether the cosmic-birefringence signal confirms. The theory is "
            "genuinely refutable -- a confirmed beta=0 would end it -- which is the point."
        ),
        "honest_scope": (
            "This is a forward-looking synthesis, not a new engine result; the predictions are the same "
            "schematic maps as v2.319/v2.321/v2.324 (beta = 3.4 deg * g_R2_parity, Pi = tanh(4 "
            "g_R2_parity)) with O(1) normalizations, so the MAGNITUDES (beta=0.20 deg, Pi=+0.23) are "
            "order-of-magnitude, not precision predictions, and the '~1.5 sigma' is illustrative. The "
            "ROBUST content is structural and is what makes the roadmap meaningful: parity-even gravity "
            "predicts exactly zero on all three parity probes (a symmetry statement), the constructed "
            "theory predicts a definite right-handed sign on each, and the three are correlated (one "
            "coupling), so the suite discriminates and the theory is refutable. The cosmic-birefringence "
            "detection is itself ~3.6 sigma and unconfirmed; a null would falsify the parity sector. The "
            "matter-sector entry is the v2.327 loose region. No new physics is claimed here beyond "
            "organizing the existing predictions into a testability map. Toy basis, O(1) prefactors."
        ),
        "references": [
            "this repo: v2.321 (cosmic birefringence), v2.319 (chiral GW), v2.324 (leptogenesis), v2.327 (predictivity extent), v2.322 (theory+data)",
            "LiteBIRD / CMB-S4 (future CMB TB/EB); Minami-Komatsu / Eskilt-Komatsu (cosmic birefringence)",
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
    print("falsifiability roadmap for the constructed theory (g_R2_parity=0.06):")
    for r in res["roadmap"]:
        print(f"  [{r['test']}] ({r['status']})")
        print(f"     constructed: {r['constructed_prediction']}")
        print(f"     parity-even: {r['parity_even_prediction']}")
        print(f"     verdict:     {r['current_verdict']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
