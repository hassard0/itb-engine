"""v2.352 - Is g_R3_parity = 0 the verified center, or an untested assumption? (the program's one fixed coupling)

The program has held the parity-odd CUBIC coupling g_R3_parity = 0 throughout -- it is not even in the family
sampler's KEYS (v2.333/v2.341 walk only 6 of the 7 couplings). Is that a justified choice or an unexamined
assumption? This closes the gap.

Every constraint that reads g_R3_parity does so through an EVEN function of it:
  * generalized_anomaly_inflow:   g_R2_parity^2 + 2*g_R3_parity^2 <= rho g_4 g_R2     (g_R3_parity^2)
  * t_hooft_anomaly_matching:     |g_R3_parity| <= rho_match (g_4+g_6) |g_R2_parity|  (|g_R3_parity|)
  * parity_violating_cubic_bound: g_R3^2 + g_R3_parity^2 <= kappa g_4^2               (g_R3_parity^2)
  * complexity_cutoff:            sum_i w_i g_i^2 <= c_max  (w=2 for g_R3_parity)      (g_R3_parity^2)

So the whole feasibility is invariant under the reflection g_R3_parity -> -g_R3_parity: the feasible window
is SYMMETRIC about 0, and 0 is its exact Chebyshev center. The construction's g_R3_parity = 0 is therefore
VERIFIED, not assumed -- and, more interestingly, the parity-odd CUBIC is the one parity coupling that the
program leaves UNPREDICTED (symmetric window, no preferred sign or magnitude), in clean contrast to the
parity-odd QUADRATIC g_R2_parity, which the cosmic-birefringence data pins to a nonzero value.
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

VERSION = "v2.352"
DEFAULT_OUT = Path("experiments/results/v2.352/qnm_parity_odd_cubic_symmetry.json")

BASE = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09,
        "g_R2_parity": 0.06, "g_R3_parity": 0.0}
DELTA = 0.02


def margins(coeffs, stack):
    return {r.constraint_name: round(r.margin, 12)
            for r in check(Theory(coefficients=dict(coeffs), name="x"), stack).results}


def feasible(coeffs, stack):
    return all(r.satisfied for r in check(Theory(coefficients=dict(coeffs), name="x"), stack).results)


def with_coupling(key, val):
    c = dict(BASE); c[key] = val
    return c


def run() -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    # (1) reflection symmetry at the FULL-STACK level: every margin is identical at +/- delta
    m_plus = margins(with_coupling("g_R3_parity", +DELTA), stack)
    m_minus = margins(with_coupling("g_R3_parity", -DELTA), stack)
    asym = {k: (m_plus[k], m_minus[k]) for k in m_plus if abs(m_plus[k] - m_minus[k]) > 1e-9}
    reflection_symmetric = (len(asym) == 0)

    # (2) scan the g_R3_parity window (symmetric range), find feasible edges + center
    grid = [round(-0.1 + i * 0.2 / 200, 5) for i in range(201)]
    feas = [g for g in grid if feasible(with_coupling("g_R3_parity", g), stack)]
    lo, hi = (min(feas), max(feas)) if feas else (None, None)
    center = round((lo + hi) / 2, 5) if feas else None
    window_symmetric = (lo is not None and abs(lo + hi) < 0.005)

    # closed-form anomaly edge: |g_R3_parity| <= sqrt((rho g_4 g_R2 - g_R2_parity^2)/2)
    rho = CANONICAL["anomaly_rho"]
    budget = rho * BASE["g_4"] * BASE["g_R2"] - BASE["g_R2_parity"] ** 2
    anomaly_edge = (budget / 2.0) ** 0.5 if budget > 0 else 0.0

    # (3) contrast: g_R2_parity = 0 (parity-odd QUADRATIC) is INFEASIBLE -- the data pins it away from 0
    gR2p_zero_feasible = feasible(with_coupling("g_R2_parity", 0.0), stack)
    gR3p_zero_feasible = feasible(with_coupling("g_R3_parity", 0.0), stack)

    checks = {
        "full_stack_reflection_symmetric_in_gR3p": reflection_symmetric,
        "gR3p_zero_is_feasible": gR3p_zero_feasible,
        "window_symmetric_about_zero": window_symmetric,
        "center_is_zero": center is not None and abs(center) < 0.005,
        "edge_matches_anomaly_closed_form": lo is not None and abs(hi - anomaly_edge) < 0.01,
        "contrast_gR2p_zero_infeasible": not gR2p_zero_feasible,   # the parity-odd QUADRATIC is pinned away from 0
    }

    return {
        "version": VERSION,
        "delta": DELTA,
        "n_asymmetric_constraints": len(asym),
        "asymmetric_constraints": asym,
        "feasible_window_gR3p": [lo, hi],
        "window_center": center,
        "anomaly_closed_form_edge": round(anomaly_edge, 5),
        "gR3p_zero_feasible": gR3p_zero_feasible,
        "gR2p_zero_feasible": gR2p_zero_feasible,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            f"The construction's g_R3_parity = 0 is VERIFIED as the Chebyshev center of a symmetric window, "
            f"not an untested assumption -- and the parity-odd CUBIC is the one parity coupling the program "
            f"leaves UNPREDICTED. Every constraint that reads g_R3_parity does so through an even function "
            f"of it (g_R3_parity^2 or |g_R3_parity|), so the entire feasibility is invariant under the "
            f"reflection g_R3_parity -> -g_R3_parity: at +/- {DELTA} all {len(m_plus)} stack margins are "
            f"identical ({len(asym)} asymmetric), the feasible window [{lo}, {hi}] is symmetric about zero, "
            f"and its center is {center}. The binding edge matches the closed-form anomaly-inflow bound "
            f"|g_R3_parity| <= sqrt((rho g_4 g_R2 - g_R2_parity^2)/2) = {anomaly_edge:.4f}. This both "
            f"justifies the program's long-standing choice to fix g_R3_parity = 0 (it IS the center, and the "
            f"6-coupling family sampler loses nothing by dropping it) and draws a clean, honest asymmetry: "
            f"the parity-odd QUADRATIC g_R2_parity is data-PINNED away from zero (setting it to 0 is "
            f"infeasible: {not gR2p_zero_feasible} feasible, because cosmic birefringence requires "
            f"g_R2_parity >= 0.047), whereas the parity-odd CUBIC g_R3_parity is UNPINNED (zero is feasible "
            f"and central, no datum breaks its reflection symmetry). So the theory makes exactly ONE "
            f"parity-odd prediction (the quadratic, the birefringence headline) and ZERO for the cubic -- "
            f"the cubic is bounded (|g_R3_parity| <~ 0.036) but unpredicted. A would-be second parity-odd "
            f"prediction would require a constraint or datum that breaks the g_R3_parity reflection symmetry "
            f"(e.g. a genuine 't Hooft ratio EQUALITY rather than the engine's bound, or a parity-odd-cubic "
            f"observable); none is currently in the engine."
        ),
        "honest_scope": (
            "The reflection symmetry is EXACT and structural: it follows from every g_R3_parity-reading "
            "constraint being an even function, demonstrated by identical full-stack margins at +/- delta "
            "(not a fit). So 'g_R3_parity = 0 is the center' and 'the cubic is unpredicted' are robust "
            "against the toy-basis NUMBERS -- they would survive any reparametrization that preserves the "
            "even structure (positivity/anomaly bounds are generically even in a parity-odd coupling). The "
            "contingent parts are the window WIDTH (the edge 0.036 scales with the anomaly prefactor rho, "
            "v2.344, and the other couplings) and the contrast resting on the birefringence data being real "
            "(v2.329: if it is a systematic, g_R2_parity = 0 becomes feasible too and BOTH parity-odd "
            "couplings are unpredicted). The engine's t_hooft_anomaly_matching is encoded as an upper BOUND "
            "with slack, not the equality its docstring motivates -- if it were an equality fixing "
            "|g_R3_parity|/|g_R2_parity|, the symmetry would break and the cubic WOULD be predicted (up to "
            "sign); that is the single most likely place a future constraint upgrade changes this verdict. "
            "Toy basis, O(1) prefactors. A gap-closing verification of the program's one fixed coupling."
        ),
        "references": [
            "this repo: src/itb/constraints/cubic_parity.py + anomaly_flow.py + complexity_cutoff.py (the g_R3_parity-reading constraints, all even)",
            "this repo: v2.321/v2.347 (g_R2_parity data-pinned), v2.335 (anomaly couples the parity couplings), v2.333/v2.341 (6-coupling family drops g_R3_parity), v2.329 (birefringence caveat)",
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
    print("is g_R3_parity = 0 the verified center? (the program's one fixed coupling)")
    print(f"  full-stack margins at +/-{res['delta']}: {res['n_asymmetric_constraints']} asymmetric "
          f"-> reflection-symmetric: {res['n_asymmetric_constraints'] == 0}")
    print(f"  feasible window: {res['feasible_window_gR3p']}  center {res['window_center']}  "
          f"(anomaly closed-form edge {res['anomaly_closed_form_edge']})")
    print(f"  g_R3_parity=0 feasible? {res['gR3p_zero_feasible']}   g_R2_parity=0 feasible? {res['gR2p_zero_feasible']} (the contrast)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
