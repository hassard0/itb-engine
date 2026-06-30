"""v2.336 - The constructed theory's ringdown-active quartic curvature: the smallest of all candidates.

A fresh seed that reconnects to the project's namesake -- quasi-normal modes / ringdown. The whole program
has tested the constructed theory in the PARITY sector (cosmic birefringence, chiral GW, leptogenesis). But
the quartic curvature g_R4 is the RINGDOWN-active operator -- it deforms the (2,2,0) Schwarzschild
quasi-normal mode -- and it has never been analysed for the constructed theory.

With the curvature tower turned on, the moment-tower mandate g_R4 >= g_R3^2/g_R2 (v2.292) FORCES a nonzero
quartic curvature whenever the cubic g_R3 is nonzero. The constructed theory (g_R3 = 0.09, g_R2 = 0.193)
therefore requires g_R4 >= 0.042 -- a nonzero ringdown-active quartic curvature -- with g_R4 = 0 infeasible.
And because the constructed theory has the most TRIMMED cubic curvature, its g_R4 floor is the SMALLEST of
all candidates (string 0.11, asymptotic_safety 0.067, lqg 0.30, cdt 0.10), so it predicts the MILDEST
ringdown deviation -- a CP-even, curvature-sector test channel complementary to the parity-sector
signatures, and the project's original ringdown thread.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack, frameworks

VERSION = "v2.336"
DEFAULT_OUT = Path("experiments/results/v2.336/qnm_ringdown_quartic_floor.json")

CONSTRUCTED = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}


def run() -> dict:
    tower = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True,
                        include_curvature_tower=True)

    def feasible(c):
        return all(r.satisfied for r in check(Theory(coefficients=c, name="x"), tower).results)

    def gr4_floor(g_R2, g_R3):
        return (g_R3 ** 2 / g_R2) if g_R2 > 0 else 0.0

    con_floor = gr4_floor(CONSTRUCTED["g_R2"], CONSTRUCTED["g_R3"])
    con_floor_feasible = feasible({**CONSTRUCTED, "g_R4": con_floor + 1e-4})
    con_zero_infeasible = not feasible({**CONSTRUCTED, "g_R4": 0.0})

    rows = [{"theory": "engine_constructed", "g_R2": CONSTRUCTED["g_R2"], "g_R3": CONSTRUCTED["g_R3"],
             "gR4_floor": round(con_floor, 4)}]
    for f in frameworks():
        c = f.encode().coefficients
        if c.get("g_R2", 0) > 0 and c.get("g_R3", 0) > 0:
            rows.append({"theory": f.name, "g_R2": c["g_R2"], "g_R3": c["g_R3"],
                         "gR4_floor": round(gr4_floor(c["g_R2"], c["g_R3"]), 4)})
        elif f.name == "pure_gr":
            rows.append({"theory": "pure_gr", "g_R2": 0.0, "g_R3": 0.0, "gR4_floor": 0.0})
    rows.sort(key=lambda r: r["gR4_floor"])

    hd = [r for r in rows if r["theory"] != "pure_gr"]
    constructed_smallest = min(hd, key=lambda r: r["gR4_floor"])["theory"] == "engine_constructed"
    pure_gr_zero = next((r["gR4_floor"] for r in rows if r["theory"] == "pure_gr"), None) == 0.0

    checks = {
        "constructed_requires_nonzero_quartic_curvature": con_zero_infeasible,
        "constructed_feasible_at_the_gR4_floor": con_floor_feasible,
        "gR4_floor_is_the_moment_tower_value": abs(con_floor - CONSTRUCTED["g_R3"] ** 2 / CONSTRUCTED["g_R2"]) < 1e-9,
        "constructed_has_the_smallest_gR4_floor_among_higher_derivative": constructed_smallest,
        "pure_gr_has_zero_ringdown_quartic": pure_gr_zero,
    }

    return {
        "version": VERSION,
        "gR4_floors": rows,
        "constructed_gR4_floor": round(con_floor, 4),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Reconnecting to the project's namesake -- ringdown -- the constructed theory makes a "
            "CP-even, curvature-sector prediction to complement its parity-sector signatures: a nonzero "
            "but MINIMAL ringdown-active quartic curvature. The quartic g_R4 is the operator that deforms "
            "the (2,2,0) Schwarzschild quasi-normal mode, and with the curvature tower on the moment-tower "
            "mandate g_R4 >= g_R3^2/g_R2 FORCES it nonzero whenever the cubic g_R3 is nonzero: the "
            "constructed theory (g_R3 = 0.09, g_R2 = 0.193) requires g_R4 >= 0.042, and g_R4 = 0 is "
            "infeasible. Crucially, because the constructed theory carries the most TRIMMED cubic "
            "curvature, its quartic floor (0.042) is the SMALLEST of all candidates -- below "
            "asymptotic_safety (0.067), cdt (0.10), string (0.11), and far below lqg (0.30) -- so it "
            "predicts the MILDEST ringdown deviation among the higher-derivative frameworks, while pure GR "
            "(g_R3 = 0) has g_R4 = 0 and no shift at all. So the ringdown channel is a clean, ordered "
            "CP-even discriminator: a sufficiently precise (2,2,0) ringdown measurement would place each "
            "candidate by the size of its quartic-curvature deviation -- pure GR at zero, the constructed "
            "theory just above it, and the community frameworks (larger trimmed-less curvature) higher up "
            "-- testing the curvature sector that the parity-sector probes (birefringence, chiral GW) do "
            "NOT. The constructed theory's trimmed curvature, which made it consistent in the first place, "
            "thus also makes it the most GR-like in ringdown -- the hardest of the higher-derivative "
            "candidates to distinguish from Einstein gravity by a ringdown measurement."
        ),
        "honest_scope": (
            "The g_R4 FLOOR is rigorous and exact: the moment-tower mandate g_R4 >= g_R3^2/g_R2 is the "
            "engine's literal constraint (v2.292), the floor values are exact arithmetic, and the "
            "feasibility verdicts (g_R4 = 0 infeasible, floor feasible) are the engine's literal output "
            "with the curvature tower on. What is SCHEMATIC is the map from g_R4 to an actual ringdown "
            "frequency/damping shift: the deep-research thread established that the published qNM->R^4 "
            "sensitivity is only a rank-1 (single-combination) ray with order-of-magnitude coefficients, "
            "so the SIZE of the (2,2,0) deviation per unit g_R4 is not sourced here -- only the floor on "
            "g_R4 and the ORDERING of the candidates (constructed smallest, pure GR zero) are claimed. The "
            "floors depend on the encoded g_R2, g_R3 (toy O(1) values); the ordering follows from the "
            "constructed theory's trimmed cubic curvature and is robust to that. This is a curvature-"
            "sector (CP-even) prediction, independent of the cosmic-birefringence data (it does not use "
            "g_R2_parity), so unlike the parity headline it does NOT rest on the v2.329 birefringence "
            "caveat. Toy basis, O(1) prefactors. A fresh-seed result reconnecting to the ringdown thread."
        ),
        "references": [
            "this repo: v2.292 (moment tower g_R4 >= g_R3^2/g_R2), v2.309 (joint region g_R4 floors), v2.317 (constructed framework)",
            "the (2,2,0) quasi-normal mode / quartic-curvature ringdown deformation (rank-1 qNM->R^4 sensitivity, deep-research thread)",
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
    print("the ringdown-active quartic curvature (g_R4) floor by candidate:")
    for r in res["gR4_floors"]:
        print(f"  {r['theory']:<18} g_R4_floor = {r['gR4_floor']:.4f}")
    print(f"  => constructed theory has the smallest nonzero g_R4 floor ({res['constructed_gR4_floor']}) "
          f"-> mildest ringdown deviation; pure GR = 0")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
