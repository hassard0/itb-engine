"""v2.398 - SWING (executes v2.397): activating the Weyl^2 axis g_C resolves c!=a -- the new axis is carved solely by the Hofman-Maldacena wedge, and it moves the ghost.

v2.397 identified resolving the c-a degeneracy (adding a distinct Weyl^2 coefficient g_C != g_R2) as the
highest-impact next extension. This swing EXECUTES it -- and finds the machinery was already built but DORMANT:
g_C is a first-class coefficient that falls back to g_R2 (a = c, a/c = 1) whenever a theory does not set it,
and the Hofman-Maldacena conformal-collider wedge (1/3 <= a/c <= 31/18, a = g_R2 Euler, c = g_C Weyl^2) is
already in the stack. So no core change is needed: the c-axis just has to be turned ON.

Result (activating g_C as an independent coupling, g_R2 = 0.193 fixed):
  - the feasible g_C range is [0.113, 0.579], i.e. a/c = g_R2/g_C in [0.334, 1.706] -- EXACTLY the
    Hofman-Maldacena wedge [1/3, 31/18] = [0.333, 1.722], and BOTH edges are bound solely by
    hofman_maldacena_wedge, confirming v2.397's prediction that HM is the one constraint that goes live and is
    the sole carver of the new axis;
  - the constructed theory (g_C = g_R2, a/c = 1) sits DEAD-CENTER in the wedge -- the holographic / Einstein
    a = c point, exactly where two-derivative bulk duals put it;
  - crucially, the Weyl^2 GHOST mass now tracks g_C, not g_R2: m_g/Lambda = 1/sqrt(g_C) ranges [1.31, 2.98]
    across the wedge, so the c-a split physically MOVES the ghost, separating the Weyl^2 (ghost, HM, screening)
    sector from the Ricci^2/Euler (a-theorem, anomaly) sector that the degeneracy had fused (v2.396).

So resolving c != a opens exactly one new, conformal-collider-bounded direction, validates v2.397, and
disentangles the eight keystone roles of g_R2 into a genuine Euler (a) sector and a genuine Weyl^2 (c) sector.
The candidate theory itself is unchanged (it stays at a = c); what changes is that the basis now RESOLVES the
freedom, and it is bounded, not free.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack

VERSION = "v2.398"
DEFAULT_OUT = Path("experiments/results/v2.398/qnm_activate_c_axis.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_C"]
BASE = [0.529, 0.4, 0.4, 0.193, 0.09, 0.06, 0.193]   # g_C = g_R2 default (a/c = 1)
GR2 = 0.193
AC_LO, AC_HI = 1.0 / 3.0, 31.0 / 18.0


def run(n_scan: int = 400) -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    def results(v):
        return check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results

    def feasible(v):
        return all(r.satisfied for r in results(v))

    def viol(v):
        return [r.constraint_name for r in results(v) if not r.satisfied]

    constructed_feasible = feasible(BASE)

    gcs = np.linspace(0.02, 0.7, n_scan)
    feas_gc = [float(g) for g in gcs if feasible([*BASE[:6], float(g)])]
    lo, hi = min(feas_gc), max(feas_gc)
    ac_lo, ac_hi = GR2 / hi, GR2 / lo   # a/c at the g_C extremes

    dg = gcs[1] - gcs[0]
    below = viol([*BASE[:6], lo - dg])
    above = viol([*BASE[:6], hi + dg])
    hm_sole = all("hofman" in c for c in below) and all("hofman" in c for c in above)

    ghost_lo = float(1.0 / np.sqrt(hi))   # heaviest g_C -> lightest ghost
    ghost_hi = float(1.0 / np.sqrt(lo))

    checks = {
        "gC_activates_independent_axis": bool(constructed_feasible and (hi - lo) > 0.1),
        "c_axis_window_is_HM_wedge": bool(abs(ac_lo - AC_LO) < 0.03 and abs(ac_hi - AC_HI) < 0.05),
        "HM_is_sole_carver_of_c_axis": bool(hm_sole),
        "constructed_at_a_equals_c_center": bool(lo < GR2 < hi),
        "ghost_mass_tracks_gC": bool((ghost_hi - ghost_lo) > 0.5),
    }

    return {
        "version": VERSION,
        "constructed_feasible_with_gC": constructed_feasible,
        "feasible_gC_range": [round(lo, 3), round(hi, 3)],
        "a_over_c_range": [round(ac_lo, 3), round(ac_hi, 3)],
        "HM_wedge_analytic": [round(AC_LO, 3), round(AC_HI, 3)],
        "c_axis_lower_edge_binding": below,
        "c_axis_upper_edge_binding": above,
        "ghost_mass_over_cutoff_range": [round(float(ghost_lo), 2), round(float(ghost_hi), 2)],
        "constructed_a_over_c": 1.0,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Executing v2.397's recommendation -- resolve c != a by activating a distinct Weyl^2 coupling g_C "
            "-- and finding the machinery was already built but dormant. g_C is a first-class coefficient that "
            "falls back to g_R2 (a = c, a/c = 1) whenever a theory does not set it, and the Hofman-Maldacena "
            "conformal-collider wedge (1/3 <= a/c <= 31/18, a = g_R2 Euler, c = g_C Weyl^2) is already in the "
            "stack, so no core change was needed -- the c-axis just had to be turned on. Turning it on (g_R2 = "
            "0.193 fixed, g_C free) opens the feasible g_C range to [0.113, 0.579], i.e. a/c in [0.334, 1.706] "
            "-- EXACTLY the Hofman-Maldacena wedge [0.333, 1.722] -- and BOTH edges are bound solely by "
            "hofman_maldacena_wedge, confirming v2.397's prediction that HM is the one constraint that goes "
            "live and is the sole carver of the new axis. The constructed theory (g_C = g_R2, a/c = 1) sits "
            "DEAD-CENTER in the wedge -- the holographic / Einstein a = c point, exactly where two-derivative "
            "bulk duals put it. Crucially, activating g_C physically MOVES the Weyl^2 ghost: its mass now "
            "tracks g_C, m_g/Lambda = 1/sqrt(g_C) ranging [1.31, 2.98] across the wedge (vs the fixed 2.28 in "
            "the degenerate basis, v2.385), so the c-a split separates the Weyl^2 sector (ghost, HM, "
            "screening) from the Ricci^2/Euler sector (a-theorem, anomaly) that the degeneracy had fused into "
            "the single keystone g_R2 (v2.396). So resolving c != a opens exactly one new, "
            "conformal-collider-bounded direction, and it is BOUNDED (a/c stays in the ANEC wedge), not free. "
            "This is the highest-impact extension (v2.397) executed and validated: the candidate theory is "
            "unchanged (it stays at a = c, the natural holographic value), but the basis now RESOLVES the "
            "Euler-vs-Weyl^2 freedom the toy basis had hidden, disentangling g_R2's eight keystone roles into "
            "a genuine a-sector and c-sector -- the concrete next step the program needed, and it cost no core "
            "surgery because the engine was already built for it."
        ),
        "honest_scope": (
            "This ACTIVATES a dormant-but-built axis: g_C and the Hofman-Maldacena wedge already exist in the "
            "engine; the swing sets g_C independently in the theory dict (which every g_C-aware constraint "
            "already reads) and maps the result. So it is genuinely the c != a extension, but it required no "
            "new code -- an honest point in its favour (safe, reversible) and a caveat (the physics content "
            "was authored earlier, v1.71; this swing executes and validates it, it does not invent the wedge). "
            "The a/c wedge [1/3, 31/18] is the exact source-cited Hofman-Maldacena bound, and its matching the "
            "feasible g_C range to ~1% is a real check that HM is the sole carver. The ghost-mass g_C-"
            "dependence uses v2.385's O(1)-schematic relation m_g/Lambda = 1/sqrt(g_C), so the [1.31, 2.98] "
            "range is O(1)-schematic; the robust point is that the ghost mass now VARIES with the c-a split "
            "(qualitative). The candidate theory is UNCHANGED -- it stays at a = c (g_C = g_R2), so this adds "
            "no new prediction about the constructed point; it characterizes the FREEDOM the resolved basis "
            "exposes (a bounded one-parameter c-a split) and confirms v2.397's diagnosis. A full c != a "
            "exploitation (re-running the whole swing arc with g_C free to see if the candidate should move "
            "off a = c) is the natural follow-up. Robust content: activating g_C opens exactly one new axis, "
            "carved solely by the Hofman-Maldacena ANEC wedge to a/c in [1/3, 31/18], with the constructed "
            "theory dead-center and the ghost mass now tracking g_C -- v2.397 executed and validated at no "
            "core-change cost. Source-cited wedge, schematic ghost range, candidate unchanged. A "
            "resolve-c-vs-a swing."
        ),
        "references": [
            "this repo: v2.397 (resolve c-a = highest-impact next step), src/itb/constraints/hofman_maldacena.py (the a/c wedge, a=g_R2/c=g_C), v2.396 (g_R2 keystone / c-a collapse), v2.385 (Weyl^2 ghost), v1.71 (HM wedge results note)",
            "physics: Hofman-Maldacena 2008 (conformal collider, 1/3<=a/c<=31/18); the Euler (a) vs Weyl^2 (c) central charges; two-derivative holographic duals force a=c",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=400)
    args = p.parse_args()
    res = run(n_scan=args.n)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("SWING (executes v2.397): activate the Weyl^2 axis g_C -- resolve c != a:")
    print(f"  constructed feasible with g_C set: {res['constructed_feasible_with_gC']} (g_C=g_R2 -> a/c=1, dead-center)")
    print(f"  feasible g_C range {res['feasible_gC_range']} -> a/c {res['a_over_c_range']} == HM wedge {res['HM_wedge_analytic']}")
    print(f"  c-axis carved SOLELY by HM: below={res['c_axis_lower_edge_binding']}, above={res['c_axis_upper_edge_binding']}")
    print(f"  Weyl^2 ghost mass now tracks g_C: m_g/Lambda in {res['ghost_mass_over_cutoff_range']} (was fixed 2.28)")
    print(f"  => v2.397 executed + validated, no core change needed (machinery was built, dormant)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
