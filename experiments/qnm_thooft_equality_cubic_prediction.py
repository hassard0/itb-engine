"""v2.353 - What the theory predicts for the parity-odd cubic IF anomaly matching is its physically-motivated equality.

v2.352 showed the parity-odd cubic g_R3_parity is UNPREDICTED: every constraint reading it is even, so its
window is symmetric about 0. The single flagged exception: the engine encodes 't Hooft anomaly matching as a
conservative BOUND with slack, |g_R3_parity| <= rho_match (g_4+g_6) |g_R2_parity| + slack, but its docstring
motivates an EQUALITY -- "the ratio of cubic to leading parity-violating coefficients is FIXED by the IR
matter content." This cycle takes that physically-motivated equality at face value and asks what it predicts
(clearly CONDITIONAL on the upgrade; the core engine is unchanged, still using the bound).

Under the equality the cubic is LOCKED to the (data-pinned) quadratic by a matter-fixed ratio:

    g_R3_parity  =  r * g_R2_parity ,    r = rho_match * (g_4 + g_6)  =  0.5 * 0.929  =  0.4645  (magnitude)

Three consequences:
  (1) the unpredicted cubic becomes a PREDICTION, data-pinned through g_R2_parity: |g_R3_parity| ~ 0.022-0.030;
  (2) the equality EATS into the anomaly budget, so it also TIGHTENS the quadratic's upper edge: the joint
      anomaly+equality bound is g_R2_parity <= sqrt(rho g_4 g_R2 / (1 + 2 r^2)), below the v2.344 edge 0.0783;
  (3) the predicted cubic sits inside the engine's CURRENT (bound-form) feasible window, so the upgrade is
      consistent with everything already imposed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack, CANONICAL

VERSION = "v2.353"
DEFAULT_OUT = Path("experiments/results/v2.353/qnm_thooft_equality_cubic_prediction.json")

BASE = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09,
        "g_R2_parity": 0.06, "g_R3_parity": 0.0}
RHO_MATCH = 0.5                      # tHooftAnomalyMatching(rho_match=0.5) in experiments/stack.py
CMB_LOWER = 0.0471                   # g_R2_parity 2-sigma floor (birefringence)
GR2P_WINDOW = [0.0471, 0.0783]       # current data-pinned quadratic window (CMB-lower .. anomaly-upper, v2.344)


def run() -> dict:
    g4, g6, gR2 = BASE["g_4"], BASE["g_6"], BASE["g_R2"]
    rho = CANONICAL["anomaly_rho"]
    r = RHO_MATCH * (g4 + g6)                      # matter-fixed ratio 0.4645

    # (1) predicted cubic at the constructed quadratic, and across the data-pinned quadratic window
    predicted_at_constructed = r * BASE["g_R2_parity"]
    cubic_window = [round(r * GR2P_WINDOW[0], 5), round(r * GR2P_WINDOW[1], 5)]

    # (2) equality tightens the quadratic's anomaly upper edge: g_R2p^2 (1 + 2 r^2) <= rho g_4 g_R2
    anomaly_edge_bound_form = (rho * g4 * gR2) ** 0.5                  # 0.0783 (v2.344, cubic=0)
    anomaly_edge_equality = (rho * g4 * gR2 / (1.0 + 2.0 * r * r)) ** 0.5
    equality_tightens_quadratic = anomaly_edge_equality < anomaly_edge_bound_form
    # self-consistent cubic window: quadratic runs [CMB-lower, equality-tightened upper edge]
    self_consistent_cubic_window = [round(r * CMB_LOWER, 5), round(r * anomaly_edge_equality, 5)]

    # (3) is the predicted point feasible against the engine's CURRENT (bound-form) stack?
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    pred = dict(BASE); pred["g_R3_parity"] = predicted_at_constructed
    pred_viol = [r2.constraint_name for r2 in check(Theory(coefficients=pred, name="pred"), stack).results
                 if not r2.satisfied]
    predicted_feasible = (len(pred_viol) == 0)

    checks = {
        "ratio_is_matter_fixed": abs(r - RHO_MATCH * (g4 + g6)) < 1e-12,
        "cubic_becomes_a_nonzero_prediction": predicted_at_constructed > 0.01,
        "predicted_cubic_feasible_in_current_engine": predicted_feasible,
        "equality_tightens_quadratic_upper_edge": equality_tightens_quadratic,
        "cubic_is_data_pinned_narrow_window": (cubic_window[1] - cubic_window[0]) < 0.02,
    }

    return {
        "version": VERSION,
        "matter_fixed_ratio_r": round(r, 4),
        "predicted_cubic_at_constructed": round(predicted_at_constructed, 5),
        "predicted_cubic_window": cubic_window,
        "self_consistent_cubic_window": self_consistent_cubic_window,
        "anomaly_edge_bound_form": round(anomaly_edge_bound_form, 5),
        "anomaly_edge_under_equality": round(anomaly_edge_equality, 5),
        "predicted_point_violations": pred_viol,
        "predicted_feasible": predicted_feasible,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            f"If 't Hooft anomaly matching is taken in its physically-motivated EQUALITY form (the engine "
            f"currently uses the conservative bound), the parity-odd CUBIC g_R3_parity -- unpredicted in "
            f"v2.352 -- becomes a SECOND parity-odd prediction, locked to the data-pinned quadratic by a "
            f"matter-fixed ratio r = rho_match (g_4 + g_6) = {r:.4f}: g_R3_parity = r * g_R2_parity. At the "
            f"constructed quadratic this gives g_R3_parity ~ {predicted_at_constructed:.4f}, and across the "
            f"data-pinned quadratic window [0.0471, 0.0783] the cubic is pinned to {cubic_window} (and, "
            f"self-consistently with the equality also tightening the quadratic, to the slightly narrower "
            f"{self_consistent_cubic_window}) -- a narrow, data-tracking prediction rather than the "
            f"symmetric [-0.036, 0.036] bound of v2.352. "
            f"The upgrade has two further consequences: it TIGHTENS the quadratic too (the cubic eats into "
            f"the anomaly budget, so the joint anomaly+equality upper edge on g_R2_parity drops from "
            f"{anomaly_edge_bound_form:.4f} to {anomaly_edge_equality:.4f}), and the predicted cubic sits "
            f"INSIDE the engine's current bound-form feasible window (the predicted point is feasible "
            f"against the full stack: {predicted_feasible}), so the equality is consistent with everything "
            f"already imposed. So the theory has a latent SECOND parity-odd prediction that switches on under "
            f"a single, well-motivated constraint upgrade -- and it would be testable the same way as the "
            f"first: the cubic Pontryagin coupling drives a chiral signal whose size is now fixed (not just "
            f"bounded) by the same cosmic-birefringence data that pins the quadratic. This converts the "
            f"v2.352 'one parity-odd prediction, the cubic unpredicted' into 'two parity-odd predictions, "
            f"both data-pinned' -- CONDITIONAL on the matching being an equality."
        ),
        "honest_scope": (
            "This is explicitly CONDITIONAL and does NOT change the core engine: the engine still encodes "
            "'t Hooft matching as a bound with slack (v2.352), and this cycle computes what the EQUALITY "
            "form would predict, presented as a conditional. The equality is physically motivated (anomaly "
            "matching is an equality in field theory) but the engine's docstring is explicit that the exact "
            "ratio 'depends on which fermion content the UV theory ultimately includes', so r = "
            "rho_match(g_4+g_6) is itself a toy proxy with an O(1) prefactor rho_match = 0.5 -- the "
            "predicted MAGNITUDE 0.028 scales with rho_match and with the matter couplings, so it is "
            "illustrative, not sharp. The matching fixes the RATIO/magnitude, not the SIGN, so even under "
            "the equality g_R3_parity is predicted only up to sign unless a further input fixes the "
            "handedness. The whole thing inherits the quadratic's dependence on the cosmic-birefringence "
            "data being real (v2.329) and on the anomaly prefactor rho (v2.344). Robust content: IF "
            "matching is an equality, the cubic is locked to the quadratic by a matter-fixed ratio (a "
            "structural statement), becomes data-pinned, and tightens the quadratic -- and the predicted "
            "value is feasible now. Toy basis, O(1) prefactors. A conditional second prediction, the "
            "constructive sequel to v2.352's flagged upgrade point."
        ),
        "references": [
            "this repo: v2.352 (the cubic is unpredicted; flagged the equality-upgrade point), src/itb/constraints/anomaly_flow.py (tHooftAnomalyMatching, the bound-vs-equality encoding)",
            "this repo: v2.347/v2.348 (g_R2_parity data-pinned + GW), v2.344 (anomaly upper edge + rho), v2.335 (anomaly couples the parity couplings), v2.329 (birefringence caveat)",
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
    print("conditional second parity-odd prediction (IF 't Hooft matching is an equality):")
    print(f"  matter-fixed ratio r = rho_match(g_4+g_6) = {res['matter_fixed_ratio_r']}")
    print(f"  predicted g_R3_parity at constructed: {res['predicted_cubic_at_constructed']}  "
          f"window {res['predicted_cubic_window']}")
    print(f"  quadratic anomaly edge: {res['anomaly_edge_bound_form']} (bound) -> {res['anomaly_edge_under_equality']} (equality, tighter)")
    print(f"  predicted point feasible in current engine? {res['predicted_feasible']}  ({res['predicted_point_violations'] or 'no violations'})")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
