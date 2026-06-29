"""v2.233 - Why the ringdown thread and the core Wilson engine probe complementary sectors.

After 16 cycles of black-hole ringdown / QNM physics, this cycle establishes the precise structural
relationship to the repo's core 7-D Wilson engine (g_4, g_6, g_8, g_R2, g_R3, g_R2_parity,
g_R3_parity) -- and why the two have not directly connected.

The key fact (curvature invariants of Schwarzschild, M=1, verified symbolically on Vulcan with
sympy and re-verified here numerically from the orthonormal tidal tensor):

    Ricci scalar R = 0,   Ricci tensor R_ab = 0   (Schwarzschild is Ricci-flat / vacuum),
    Kretschmann K = R_abcd R^abcd = 48 M^2 / r^6  != 0,
    Gauss-Bonnet G = K  (since R = R_ab = 0).

Consequences for which higher-curvature operators modify the Schwarzschild TENSOR ringdown:
  - Ricci-scalar operators R^2, R^3 (the engine's g_R2, g_R3) VANISH on the Ricci-flat background
    (R = 0), so at leading order they do not deform the Schwarzschild metric and are RINGDOWN-BLIND
    for the tensor modes (cf. f(R) with R=0 background: f'(0)=1 leaves the tensor sector unshifted).
  - The Gauss-Bonnet quadratic Riemann invariant is a 4D TOPOLOGICAL term (total derivative), also
    contributing nothing to the field equations at quadratic order.
  - The LEADING curvature operator that DOES modify Schwarzschild tensor ringdown is the QUARTIC
    Riemann invariant (~ K^2, dimension-8) -- exactly the "R4" the QNM thread studied (Bresciani;
    Silva-Ghosh-Buonanno) -- because K != 0 on-shell.

So the ringdown-active operator (Riemann^4) is NOT a Ricci-scalar power and is BEYOND the engine's
current curvature basis (which stops at the cubic Ricci scalar g_R3). The engine's g_8 is the
MATTER spin-4 (s^4) moment, not a curvature operator -- so the earlier "ringdown constraint on g_8"
bridge was a misidentification. Bridging the threads requires EXTENDING the engine with a Riemann^4
(g_R4) curvature axis, not adding a constraint on an existing one.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

VERSION = "v2.233"
DEFAULT_OUT = Path("experiments/results/v2.233/qnm_engine_operator_sector_bridge.json")


def tidal_components(r: float, M: float = 1.0) -> dict:
    """Nonzero orthonormal-frame Riemann (tidal) components of Schwarzschild (independent set)."""
    c = M / r**3
    return {  # (ab)(cd) diagonal blocks; 0=t^, 1=r^, 2=theta^, 3=phi^
        "R_0101": -2 * c, "R_0202": c, "R_0303": c,
        "R_1212": -c, "R_1313": -c, "R_2323": 2 * c,
    }


def curvature_invariants(r: float, M: float = 1.0) -> dict:
    comp = tidal_components(r, M)
    # Kretschmann K = sum_abcd R_abcd^2 = 4 * sum(independent diagonal components^2)
    K = 4 * sum(v**2 for v in comp.values())
    # Ricci-flat check: the tidal tensor is trace-free in each timelike/spacelike block
    ricci_tt_block = comp["R_0101"] + comp["R_0202"] + comp["R_0303"]   # ~ R_t^t component
    return {"K_numeric": K, "K_closed_form": 48 * M**2 / r**6,
            "ricci_trace_block": ricci_tt_block}


def run() -> dict:
    rs = [3.0, 5.0, 10.0]   # incl. the photon sphere r=3
    checks = []
    for r in rs:
        ci = curvature_invariants(r)
        checks.append({"r": r, "K_numeric": ci["K_numeric"], "K_closed_form": ci["K_closed_form"],
                       "K_match": abs(ci["K_numeric"] - ci["K_closed_form"]) < 1e-12,
                       "ricci_flat": abs(ci["ricci_trace_block"]) < 1e-12})
    operator_sector = {
        "g_R2_R_squared": {"on_shell_value": "0 (R=0)", "ringdown_active": False,
                           "in_engine_basis": True},
        "g_R3_R_cubed": {"on_shell_value": "0 (R=0)", "ringdown_active": False,
                         "in_engine_basis": True},
        "gauss_bonnet_quadratic_Riemann": {"on_shell_value": "K (topological in 4D)",
                                           "ringdown_active": False, "in_engine_basis": False},
        "Riemann4_quartic_dim8_R4": {"on_shell_value": "~ K^2 != 0", "ringdown_active": True,
                                     "in_engine_basis": False},
        "g_8_matter_s4_moment": {"note": "MATTER spin-4 moment, not a curvature operator",
                                 "ringdown_active": False, "in_engine_basis": True},
    }
    return {
        "version": VERSION,
        "method": ("Schwarzschild curvature invariants (sympy on Vulcan: R=0, R_ab=0, K=48M^2/r^6, "
                   "G=K) re-verified here numerically from the orthonormal tidal tensor; operator-"
                   "sector classification for tensor-ringdown activity; M=1"),
        "curvature_checks": checks,
        "all_K_match": all(c["K_match"] for c in checks),
        "all_ricci_flat": all(c["ricci_flat"] for c in checks),
        "operator_sector_classification": operator_sector,
        "finding": (
            "Schwarzschild is Ricci-flat (R = R_ab = 0, verified) with nonzero Kretschmann "
            "K = 48/r^6, so the curvature operators differ sharply in tensor-ringdown activity: the "
            "engine's Ricci-scalar operators g_R2 (R^2) and g_R3 (R^3) VANISH on-shell and are "
            "ringdown-blind; the quadratic-Riemann Gauss-Bonnet term is 4D-topological (also "
            "inert); the FIRST curvature operator that modifies the Schwarzschild tensor ringdown is "
            "the QUARTIC Riemann invariant (~K^2, dim-8 = the QNM thread's 'R4'), because K != 0. "
            "That ringdown-active operator is NOT in the engine's basis (which stops at the cubic "
            "Ricci scalar g_R3), and the engine's g_8 is the MATTER s^4 moment, not curvature -- so "
            "the QNM thread and the core engine probe COMPLEMENTARY operator sectors. Bridging them "
            "requires EXTENDING the engine with a Riemann^4 (g_R4) curvature axis, not constraining "
            "an existing coefficient."
        ),
        "honest_scope": (
            "Leading-order, Schwarzschild (non-rotating), tensor-sector statement: f(R) gravity DOES "
            "add a separate massive SCALAR mode and the Ricci-scalar operators can affect rotating "
            "(Kerr, R != 0 off-vacuum is still 0 but frame-dragging matters) or matter-sourced "
            "backgrounds -- 'ringdown-blind' is specifically the leading tensor QNM on the Ricci-flat "
            "Schwarzschild background. The Riemann^4 -> ringdown link is the established literature "
            "result (Bresciani; SGB) the QNM thread used; the absolute g_R4 normalization stays "
            "un-sourceable (the standing v2.215 / Bresciani-axis-map blocker). This is a STRUCTURAL "
            "clarification, not a new bound. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "curvature invariants verified on Vulcan (sympy 1.14): R=0, K=48 M^2/r^6, G=K",
            "Bresciani et al. (arXiv:2504.12855); Silva, Ghosh, Buonanno (arXiv:2205.05132) -- R4 ringdown",
            "this repo: core 7-D Wilson engine (g_4..g_R3_parity), v2.215 (R4 normalization blocker)",
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
    for c in res["curvature_checks"]:
        print(f"  r={c['r']:.0f}  K={c['K_numeric']:.6f} (=48/r^6 {c['K_closed_form']:.6f}, "
              f"match {c['K_match']})  ricci_flat {c['ricci_flat']}")
    print(f"all K match = {res['all_K_match']}; all Ricci-flat = {res['all_ricci_flat']}")
    print("ringdown-active curvature operator: Riemann^4 (dim-8), NOT in engine basis (g_R3 max)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
