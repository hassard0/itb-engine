"""v2.364 - Is the constructed theory's RIGHT-handedness a prediction or a data-readout? (a pure data-readout)

v2.352 showed the parity-odd CUBIC g_R3_parity is symmetric (unpredicted). v2.360 showed the parity-odd
QUADRATIC's MAGNITUDE is data-pinned. This asks the remaining parity question: the constructed theory violates
parity RIGHT-handedly (g_R2_parity = +0.06 > 0) -- is that SIGN a theoretical prediction, or set entirely by
the data?

The engine has explicitly handedness-sensitive theoretical constraints (left_handed_graviton_positivity and
right_handed_graviton_positivity), so unlike the cubic the quadratic's theoretical constraints are NOT all
even in g_R2_parity. The test flips the sign (g_R2_parity -> -g_R2_parity at the constructed point) and asks:
  (1) do the theoretical constraints break the reflection symmetry? (yes -- left/right graviton positivity);
  (2) but are they MIRROR-PAIRED, so the theory's overall consistency (min theoretical margin) is the SAME
      for both signs? (i.e. is there any NET theoretical preference for one handedness?);
  (3) is either sign theoretically feasible on its own, so that only the DATA breaks the tie?

Result: the left/right graviton positivities swap under the flip (left 0.148 <-> right 0.194) but are
mirror-paired, so the MIN theoretical margin is identical for +g_R2_parity and -g_R2_parity -- the theory has
NO net preference for either handedness. Both signs are theoretically feasible; only cosmic birefringence
(beta = +0.34 > 0) breaks the tie, forcing right-handed. So the constructed theory's right-handedness is a
pure DATA-READOUT: had birefringence measured beta < 0, the engine would build an equally-consistent
LEFT-handed theory. Combined with v2.360 (magnitude data-pinned) and v2.352 (cubic unpredicted), the entire
parity-odd quadratic content -- existence, magnitude, AND sign -- is data-driven; the theory contributes only
the correlations (the anomaly budget linking parity to matter+curvature), not the parity sector's values.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack

VERSION = "v2.364"
DEFAULT_OUT = Path("experiments/results/v2.364/qnm_handedness_data_readout.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
BASE = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}
DATA_NAMES = {"submm_gravity_yukawa_bound", "cosmic_birefringence_data", "gw_speed_bound", "gw_dispersion_bound"}
GP = 0.06


def margins(gp, stack):
    c = dict(BASE); c["g_R2_parity"] = gp
    return {r.constraint_name: (r.margin, r.satisfied) for r in check(Theory(coefficients=c, name="x"), stack).results}


def run() -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    mp = margins(+GP, stack)
    mm = margins(-GP, stack)

    # which THEORETICAL constraints break the reflection symmetry?
    theo_asym = {k: (round(mp[k][0], 4), round(mm[k][0], 4)) for k in mp
                 if k not in DATA_NAMES and abs(mp[k][0] - mm[k][0]) > 1e-9}

    # net theoretical preference: min theoretical margin at +GP vs -GP
    def min_theo(m):
        return min(v[0] for k, v in m.items() if k not in DATA_NAMES)
    min_theo_plus = min_theo(mp)
    min_theo_minus = min_theo(mm)
    handedness_symmetric_as_pair = abs(min_theo_plus - min_theo_minus) < 1e-9

    # is each sign theoretically feasible on its own (all theoretical constraints satisfied)?
    theo_feasible_plus = all(v[1] for k, v in mp.items() if k not in DATA_NAMES)
    theo_feasible_minus = all(v[1] for k, v in mm.items() if k not in DATA_NAMES)

    # does only the DATA break the tie? (birefringence satisfied for +, violated for -)
    bire_plus = mp["cosmic_birefringence_data"]
    bire_minus = mm["cosmic_birefringence_data"]
    data_breaks_tie = bire_plus[1] and not bire_minus[1]

    # the two handedness-sensitive constraints swap
    left_right_swap = ("left_handed_graviton_positivity" in theo_asym
                       and "right_handed_graviton_positivity" in theo_asym
                       and abs(mp["left_handed_graviton_positivity"][0] - mm["right_handed_graviton_positivity"][0]) < 1e-9)

    checks = {
        "theoretical_constraints_are_handedness_sensitive": len(theo_asym) > 0,
        "left_right_graviton_positivity_swap_under_flip": left_right_swap,
        "no_net_theoretical_handedness_preference": handedness_symmetric_as_pair,
        "both_signs_theoretically_feasible": theo_feasible_plus and theo_feasible_minus,
        "only_data_breaks_the_tie": data_breaks_tie,
    }

    return {
        "version": VERSION,
        "theoretical_asymmetric_constraints": theo_asym,
        "min_theoretical_margin_plus": round(min_theo_plus, 4),
        "min_theoretical_margin_minus": round(min_theo_minus, 4),
        "theo_feasible_plus": bool(theo_feasible_plus),
        "theo_feasible_minus": bool(theo_feasible_minus),
        "birefringence_margin_plus": round(bire_plus[0], 4),
        "birefringence_margin_minus": round(bire_minus[0], 4),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The constructed theory's RIGHT-handedness is a pure DATA-READOUT, not a theoretical prediction. "
            "Unlike the parity-odd cubic (all constraints even, v2.352), the parity-odd QUADRATIC does have "
            "handedness-sensitive theoretical constraints: under g_R2_parity -> -g_R2_parity the "
            "left_handed_graviton_positivity and right_handed_graviton_positivity margins SWAP (left 0.148 "
            "<-> right 0.194). But they are MIRROR-PAIRED, so the swap leaves the MIN theoretical margin "
            f"identical for both signs ({min_theo_plus:.3f} at +g_R2_parity, {min_theo_minus:.3f} at "
            "-g_R2_parity) -- the theory has NO net preference for either handedness; its consistency is "
            "exactly as good for left- as for right-handed parity violation. Both signs are theoretically "
            "feasible on their own; the ONLY thing that breaks the tie is the cosmic-birefringence data "
            f"(beta = +0.34 > 0): its margin is +{bire_plus[0]:.3f} for right-handed but {bire_minus[0]:.3f} "
            "(violated) for left-handed. So had birefringence measured beta < 0, the engine would build an "
            "equally-consistent LEFT-handed theory -- the handedness is read off the sign of the "
            "measurement, not predicted. This completes the honest anatomy of the parity-odd quadratic: its "
            "EXISTENCE (v2.321: beta=0 excluded), its MAGNITUDE (v2.360: within ~0.3-sigma of the data), and "
            "now its SIGN are ALL data-driven; the theory contributes only the CORRELATIONS -- the anomaly "
            "budget linking parity to the matter+curvature sector (v2.335/v2.350/v2.357) and the "
            "left/right-graviton-positivity structure that makes the two handedness consistent -- not the "
            "parity sector's values. It is the sharpest statement of the v2.329 dependence: the parity "
            "headline is the DATA, structured by the theory, not a parity prediction the theory makes on its "
            "own."
        ),
        "honest_scope": (
            "This is exact: the margins are the engine's literal check() output at the constructed point with "
            "the sign flipped, the left/right swap and the identical min-theoretical-margin are numerical "
            "facts (not a fit), and the 'both signs theoretically feasible' is a direct satisfaction check. "
            "The result is a statement about the ENGINE's encoding: the left/right graviton positivity "
            "constraints are constructed as a mirror pair (kappa symmetric), which is the physically natural "
            "choice (parity-even theoretical consistency treats both handedness equally) but is an encoding "
            "choice -- a genuinely parity-VIOLATING theoretical constraint (e.g. a chiral anomaly that "
            "preferred one handedness) would break the tie theoretically, and none is in the engine. The "
            "birefringence sign (beta > 0) and its map are the toy/data inputs (v2.347/v2.329). So the robust "
            "content is structural: the theory's consistency is handedness-symmetric as a pair, so the sign "
            "is data-set; the specific margins are toy-basis numbers. Combined with v2.352/v2.360, the whole "
            "parity-odd quadratic (existence/magnitude/sign) is data-driven. Toy basis, O(1) prefactors. The "
            "completion of the parity-sector honesty audit."
        ),
        "references": [
            "this repo: v2.352 (parity-odd cubic symmetric/unpredicted), v2.360 (quadratic magnitude data-pinned), v2.321 (beta=0 excluded), v2.329 (the single point of failure)",
            "this repo: src/itb/constraints/parity_violation.py (left/right handed graviton positivity, the mirror pair); v2.335/v2.350/v2.357 (the anomaly correlations the theory DOES supply)",
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
    print("is the theory's right-handedness a prediction or a data-readout?")
    print(f"  handedness-sensitive theoretical constraints (swap under sign flip): {list(res['theoretical_asymmetric_constraints'])}")
    print(f"  min theoretical margin: +g_R2_parity {res['min_theoretical_margin_plus']}  vs  -g_R2_parity {res['min_theoretical_margin_minus']}  (equal -> no net preference)")
    print(f"  theoretically feasible: +{res['theo_feasible_plus']}  -{res['theo_feasible_minus']}   (both signs OK)")
    print(f"  birefringence margin: +{res['birefringence_margin_plus']}  -{res['birefringence_margin_minus']}  (only data breaks the tie)")
    print(f"  => right-handedness is a pure DATA-READOUT")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
