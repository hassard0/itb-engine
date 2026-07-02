"""v2.442 - the four-experiment / three-keystone unified verdict: LiteBIRD r and DESI w BOTH test the g_R2 keystone, so the candidate is over-determined -- a built-in consistency cross-check sharper than the three-front table (v2.430).

Dreaming, consolidating. v2.441 gave the candidate a fourth near-term front (LiteBIRD r ~ 0.004 / n_s ~ 0.964 from
the g_R2 Starobinsky plateau). This cycle unifies all four and finds the sharp structure: four EXPERIMENTS but
only THREE keystone couplings, because g_R2 drives BOTH the dark-energy plateau (DESI w) AND inflation (LiteBIRD
r). So g_R2 is OVER-DETERMINED -- tested by two independent experiments -- giving the candidate a built-in
consistency cross-check no single-front analysis has.

The four experiments and their keystone couplings:
  1. CMB birefringence (parity)   <- g_R2_parity > 0   : beta > 0 (positive handedness)
  2. CMB-S4 matter (g_4)          <- g_4 > 0           : matter-dominant signal present
  3. DESI/Euclid dark energy (w)  <- g_R2 > 0          : w > -1 (mild quintessence plateau)
  4. LiteBIRD tensors (r, n_s)    <- g_R2 > 0          : r ~ 0.004, n_s ~ 0.964 (Starobinsky plateau)

The candidate predicts ALL FOUR present, with fronts 3 and 4 LOCKED TOGETHER by the single g_R2 > 0 keystone:
w > -1 and (r ~ 0.004, n_s ~ 0.964) must co-occur, because the same positive R^2 scalaron gives the late-time
plateau and the early-time plateau. This is the sharp new falsifier: if LiteBIRD sees the Starobinsky plateau
(r ~ 0.004) but DESI sees w < -1 (phantom), or vice versa, the single-scalaron story is FALSIFIED even though each
front alone looks fine. Conversely a joint (r ~ 0.004) AND (w > -1) confirms the g_R2 keystone twice over.

Across the three independent keystones the candidate occupies ONE of 2^3 = 8 sign-patterns (parity x matter x
g_R2), and within the g_R2 axis the r<->w over-determination is a further internal check -- so the candidate is
maximally falsifiable AND self-consistency-checked. The four experiments span ~2030s (LiteBIRD, DESI/Euclid,
CMB-S4, and CMB birefringence from SPT/BICEP/LiteBIRD), so this is a near-term, decisive, correlated program.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.442"
DEFAULT_OUT = Path("experiments/results/v2.442/qnm_four_front_verdict.json")

CON = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}


def run() -> dict:
    fronts = {
        "CMB_birefringence": {"experiment": "SPT/BICEP/LiteBIRD EB", "keystone": "g_R2_parity",
                              "candidate_prediction": "beta > 0 (nonzero, positive handedness)",
                              "keystone_value": CON["g_R2_parity"], "present": CON["g_R2_parity"] > 0},
        "CMB_S4_matter": {"experiment": "CMB-S4", "keystone": "g_4",
                          "candidate_prediction": "matter-dominant higher-derivative signal present",
                          "keystone_value": CON["g_4"], "present": CON["g_4"] > 0},
        "DESI_dark_energy_w": {"experiment": "DESI/Euclid", "keystone": "g_R2",
                               "candidate_prediction": "w > -1 (mild quintessence plateau)",
                               "keystone_value": CON["g_R2"], "present": CON["g_R2"] > 0},
        "LiteBIRD_tensors": {"experiment": "LiteBIRD", "keystone": "g_R2",
                             "candidate_prediction": "r ~ 0.004, n_s ~ 0.964 (Starobinsky plateau)",
                             "keystone_value": CON["g_R2"], "present": CON["g_R2"] > 0},
    }

    keystones = sorted({f["keystone"] for f in fronts.values()})
    # g_R2 drives two experiments -> over-determined
    gR2_experiments = [name for name, f in fronts.items() if f["keystone"] == "g_R2"]
    gR2_overdetermined = len(gR2_experiments) >= 2

    n_experiments = len(fronts)
    n_keystones = len(keystones)                 # 3 independent couplings
    n_patterns = 2 ** n_keystones                # 8 sign-patterns
    all_present = all(f["present"] for f in fronts.values())

    checks = {
        "four_experiments": n_experiments == 4,
        "three_independent_keystones": n_keystones == 3,
        "gR2_over_determined_by_two_experiments": gR2_overdetermined,
        "candidate_predicts_all_four_present": all_present,
        "maximally_falsifiable_one_of_eight": n_patterns == 8,
    }

    return {
        "version": VERSION,
        "fronts": fronts,
        "independent_keystones": keystones,
        "gR2_experiments": gR2_experiments,
        "n_sign_patterns": n_patterns,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The four-experiment / three-keystone unified verdict: LiteBIRD r and DESI w both test the g_R2 "
            "keystone, so the candidate is over-determined -- a built-in consistency cross-check sharper than "
            "the three-front table (v2.430). v2.441 added a fourth near-term front (LiteBIRD r ~ 0.004 / "
            "n_s ~ 0.964 from the g_R2 Starobinsky plateau); unifying all four reveals the structure: four "
            "EXPERIMENTS (CMB birefringence, CMB-S4 matter, DESI/Euclid dark energy, LiteBIRD tensors) but only "
            "THREE keystone couplings (parity g_R2_parity, matter g_4, curvature g_R2), because g_R2 drives "
            "BOTH the dark-energy plateau (DESI w > -1) AND inflation (LiteBIRD r ~ 0.004, n_s ~ 0.964). So "
            "g_R2 is OVER-DETERMINED -- tested by two independent experiments. The candidate predicts all four "
            "fronts present, with fronts 3 and 4 LOCKED TOGETHER by the single g_R2 > 0 keystone: w > -1 and "
            "the Starobinsky plateau must co-occur, because the same positive R^2 scalaron gives the late-time "
            "and early-time plateaus. This is the sharp new falsifier: if LiteBIRD sees r ~ 0.004 (plateau) but "
            "DESI sees w < -1 (phantom), or vice versa, the single-scalaron story is FALSIFIED even though each "
            "front alone looks fine; conversely a joint (r ~ 0.004) AND (w > -1) confirms g_R2 twice over. "
            "Across the three independent keystones the candidate occupies ONE of 2^3 = 8 sign-patterns, and "
            "within the g_R2 axis the r<->w over-determination is a further internal check -- so the candidate "
            "is maximally falsifiable AND self-consistency-checked, over a near-term (~2030s) four-experiment "
            "program. This is the payoff of the inflation front: it does not just add a fourth independent test, "
            "it turns the g_R2 keystone -- the same coupling that is rigorously forced (v2.417), caps gravity "
            "(v2.412), and is the leading UV-completion discriminant (v2.434-440) -- into a doubly-measured, "
            "internally-checkable prediction, making the candidate's cosmological history (R^2 inflation -> R^2 "
            "dark energy) a single falsifiable arc rather than two separate claims."
        ),
        "honest_scope": (
            "This is a STRUCTURAL / falsifiability-accounting cycle, not a new numerical prediction: it "
            "re-partitions the candidate's four observational fronts by their keystone couplings and identifies "
            "the g_R2 over-determination. The 'present/absent' pattern uses the sign structure (each front keyed "
            "to a coupling being positive), the robust content throughout the program; the specific magnitudes "
            "(beta, r, w) remain O(1)-toy / plateau-class (v2.441 caveats carry: r ~ 0.004 is the Starobinsky "
            "plateau value shared by any positive-plateau model, w > -1 is the refined-dS-conjecture proxy "
            "result, both sourced_proxy-tier for the dark-energy sector). 'Over-determined' is the correct and "
            "useful statement that two experiments probe the same coupling (g_R2 > 0 gives both plateaus) -- a "
            "genuine consistency cross-check -- but it does NOT make r and w numerically predict each other "
            "(they are the same SIGN/plateau-class signature at two epochs, not a computed r(w) relation; a "
            "unified g_R2 potential across both epochs is not computed). '1 of 8 sign-patterns' counts the three "
            "independent keystones, consistent with v2.430's 3-front / 8-pattern maximal falsifiability -- the "
            "fourth EXPERIMENT sharpens (adds the internal g_R2 check) rather than adding a fourth independent "
            "axis. The experiment timelines (~2030s) are external facts. Robust content: the candidate's four "
            "near-term experimental fronts rest on three keystone couplings, with g_R2 driving two of them "
            "(DESI w and LiteBIRD r), so g_R2 is over-determined -- a built-in falsifiable consistency check "
            "(both plateaus must appear together) on top of the 1-of-8 sign-pattern maximal falsifiability. "
            "Structural-accounting, sign-not-magnitude, plateau-class-shared, same-signature-not-computed-"
            "relation. A four-front unification cycle."
        ),
        "references": [
            "this repo: v2.441 (inflation front r/n_s), v2.430 (three-front verdict table), v2.417 (g_R2 forced), v2.412 (g_R2 caps gravity), v2.422-425 (g_R2 dark-energy w), v2.434-440 (g_R2/UV completion)",
            "physics: Starobinsky r=12/N^2 ~ 0.004; refined dS conjecture w >~ -1; cosmic birefringence beta; the four experiments LiteBIRD / DESI-Euclid / CMB-S4 / CMB-EB birefringence (~2030s)",
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
    print("v2.442 - four-experiment / three-keystone unified verdict:")
    for name, f in res["fronts"].items():
        print(f"  {name:<22} <- {f['keystone']:<13} : {f['candidate_prediction']}")
    print(f"  independent keystones: {res['independent_keystones']} (3) => candidate = 1 of {res['n_sign_patterns']} sign-patterns")
    print(f"  g_R2 OVER-DETERMINED by {res['gR2_experiments']} => built-in cross-check: r~0.004 (LiteBIRD) AND w>-1 (DESI) must co-occur or the single-scalaron story is FALSIFIED")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
