"""v2.453 - the complete scale-independent inflation prediction set: given n_s, the candidate's R^2 plateau pins (r, n_t, alpha_s) via three parameter-free relations -- completing v2.452 (which pinned only r).

Continuing the dimensionless vein. The candidate's R^2 (Starobinsky) inflation is a ONE-PARAMETER family (the
e-fold number N), so a single measured observable fixes ALL the others through scale-independent relations. Given
n_s:

    N     = 2 / (1 - n_s)
    r     = 3 (1 - n_s)^2               (tensor-to-scalar, v2.452)
    n_t   = - r / 8                     (single-field tensor consistency)
    alpha_s = - 2 / N^2 = -(1-n_s)^2/2  (running of the scalar tilt)

None of these carries a scale or an O(1)-toy magnitude. At the Planck value n_s = 0.9649 (N ~ 57):

    r      = 0.0037
    n_t    = -0.00046
    alpha_s = -0.00062

So the candidate's inflation makes a COMPLETE set of scale-independent predictions from one number: r ~ 0.0037
(LiteBIRD), n_t ~ -5e-4 (the single-field tensor consistency, tiny but definite), and a running alpha_s ~ -6e-4
(CMB-S4 targets sigma(alpha_s) ~ few x 1e-3, so this is a soft target). This completes the inflation front's
scale-independent predictions begun in v2.452, and together with beta ~ alpha_EM (v2.451) the candidate now has a
scale-independent core -- a set of predictions that need neither the string scale nor any O(1)-toy coefficient.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.453"
DEFAULT_OUT = Path("experiments/results/v2.453/qnm_inflation_consistency_set.json")

NS = 0.9649
NS_ERR = 0.0042
CMB_S4_SIGMA_ALPHA_S = 3e-3


def predict(ns: float) -> dict:
    N = 2.0 / (1.0 - ns)
    r = 3.0 * (1.0 - ns) ** 2
    n_t = -r / 8.0
    alpha_s = -2.0 / N ** 2
    return {"N": N, "r": r, "n_t": n_t, "alpha_s": alpha_s}


def run() -> dict:
    p = predict(NS)
    # n_t via the single-field consistency r = -8 n_t
    single_field_consistency = abs(p["n_t"] + p["r"] / 8.0) < 1e-12
    alpha_s_form = abs(p["alpha_s"] + (1 - NS) ** 2 / 2.0) < 1e-9   # alpha_s = -(1-n_s)^2/2

    checks = {
        "r_relation_scale_independent": abs(p["r"] - 3 * (1 - NS) ** 2) < 1e-12,
        "n_t_single_field_consistency": single_field_consistency,
        "alpha_s_relation": alpha_s_form,
        "complete_set_from_ns": all(k in p for k in ("r", "n_t", "alpha_s")),
        "N_in_inflation_window": 40 < p["N"] < 70,
    }

    return {
        "version": VERSION,
        "n_s": NS,
        "predictions_at_measured_ns": {"N": round(p["N"], 1), "r": round(p["r"], 5),
                                       "n_t": round(p["n_t"], 6), "alpha_s": round(p["alpha_s"], 6)},
        "relations": {"r": "3(1-n_s)^2", "n_t": "-r/8 (single-field consistency)", "alpha_s": "-2/N^2 = -(1-n_s)^2/2"},
        "cmb_s4_sigma_alpha_s": CMB_S4_SIGMA_ALPHA_S,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The complete scale-independent inflation prediction set: given n_s, the candidate's R^2 plateau "
            "pins (r, n_t, alpha_s) via three parameter-free relations -- completing v2.452, which pinned only "
            "r. Because R^2 (Starobinsky) inflation is a one-parameter family (the e-fold number N), a single "
            "measured observable fixes all the others through scale-independent relations: N = 2/(1-n_s), "
            "r = 3(1-n_s)^2, n_t = -r/8 (the single-field tensor consistency), and alpha_s = -2/N^2 = "
            "-(1-n_s)^2/2 (the running of the scalar tilt). None carries a scale or an O(1)-toy magnitude. At "
            "the Planck value n_s = 0.9649 (N ~ 57): r = 0.0037, n_t = -0.00046, alpha_s = -0.00062. So the "
            "candidate's inflation makes a COMPLETE set of scale-independent predictions from one number -- "
            "r ~ 0.0037 (LiteBIRD-testable), the tiny-but-definite tensor tilt n_t ~ -5e-4 fixed by "
            "single-field consistency, and a small negative running alpha_s ~ -6e-4 (a soft CMB-S4 target, "
            "sigma(alpha_s) ~ few x 1e-3). This completes the inflation front's scale-independent predictions "
            "begun in v2.452, and together with beta ~ alpha_EM (v2.451) the candidate now has a "
            "SCALE-INDEPENDENT CORE: a set of falsifiable predictions -- the birefringence size and the full "
            "inflation consistency set -- that need neither the string scale nor any O(1)-toy coefficient, the "
            "sharpest and most scale-clean part of the candidate's observational content."
        ),
        "honest_scope": (
            "These are the standard single-field / Starobinsky consistency relations to LEADING order in 1/N, "
            "and they are PLATEAU-CLASS -- shared by any plateau/R^2-like model, so they validate the plateau "
            "CLASS, not uniquely THIS candidate (same status as v2.442/v2.452). The n_t = -r/8 relation is the "
            "generic single-field-slow-roll tensor consistency (not Starobinsky-specific); r = 3(1-n_s)^2 and "
            "alpha_s = -2/N^2 are the Starobinsky/plateau forms. Finite-N and reheating corrections shift the "
            "leading values (a few % in n_s, order-1 relative in the small quantities r, n_t, alpha_s), so the "
            "numbers are leading-order with real theory uncertainty; the RELATIONS are robust to leading order. "
            "Observability differs sharply: r ~ 0.0037 is a genuine near-term target (LiteBIRD), but n_t ~ -5e-4 "
            "is far below any foreseeable tensor-tilt sensitivity, and alpha_s ~ -6e-4 is below the nominal "
            "CMB-S4 target (sigma ~ 3e-3), so those two are 'definite but effectively unmeasurable' predictions "
            "-- honest to state, not near-term discriminators. 'Scale-independent core' is a framing of the "
            "subset of predictions free of toy scales (v2.451 + this), not a new physical result. Robust "
            "content: the candidate's plateau inflation is a one-parameter family whose (r, n_t, alpha_s) are "
            "fixed by n_s through scale-independent, parameter-free relations -- r = 3(1-n_s)^2 ~ 0.0037 "
            "(testable), n_t = -r/8 and alpha_s = -2/N^2 (definite but tiny) -- completing the inflation front's "
            "scale-clean predictions, plateau-class and leading-order-in-1/N. "
            "Plateau-class-not-unique, leading-order, n_t-and-alpha_s-effectively-unmeasurable, framing-of-a-subset. "
            "An inflation-consistency-set cycle."
        ),
        "references": [
            "this repo: v2.452 (r = 3(1-n_s)^2), v2.451 (alpha_EM birefringence), v2.441 (Starobinsky n_s, r), v2.442 (over-determination)",
            "physics: Starobinsky 1980; single-field consistency n_t = -r/8; Starobinsky alpha_s = -2/N^2; Planck 2018 (n_s = 0.9649); LiteBIRD (r), CMB-S4 (alpha_s ~ few x 1e-3)",
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
    pr = res["predictions_at_measured_ns"]
    print("v2.453 - the complete scale-independent inflation prediction set (from n_s alone):")
    print(f"  n_s = {res['n_s']} (N ~ {pr['N']})  =>  r = {pr['r']}, n_t = {pr['n_t']}, alpha_s = {pr['alpha_s']}")
    print(f"  relations (all scale-independent): r={res['relations']['r']}, n_t={res['relations']['n_t']}, alpha_s={res['relations']['alpha_s']}")
    print("  => COMPLETE inflation set from one number; with beta ~ alpha_EM (v2.451) = the candidate's scale-independent core")
    print("  (honest: r~0.0037 LiteBIRD-testable; n_t~-5e-4 + alpha_s~-6e-4 definite but effectively unmeasurable; plateau-class)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
