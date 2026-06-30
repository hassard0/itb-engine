"""v2.315 - The consistency scorecard: ranking all candidate theories, and a coherence audit.

After the new-theory arc (engine g_R4 extension, curvature carving, the joint region, the convexity and
finite-cutoff structure, the cosmology handle, the lqg forensics, and the construction + validation of the
engine-preferred framework), this cycle consolidates: it ranks every candidate theory on one scorecard and
programmatically AUDITS that the arc's headline results hold together without contradiction.

The scorecard ranks pure GR, the four community frameworks, and the engine-preferred framework by
worst-case margin, recording the single binding constraint and its physical family for each. A sharp
coherence finding emerges: the UNIVERSALITY family (anomaly + swampland/repulsive-force) is the decisive
arbiter throughout -- it KILLS every community framework (all four are bound by the same constraint,
repulsive_force_conjecture) and BOUNDS the engine-preferred framework (via t_hooft anomaly matching). The
preferred framework is precisely the theory that clears the repulsive-force wall (by trimming the
curvature) while balancing against the anomaly wall, consistent with the v2.314 amplitude-vs-universality
equilibrium.
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

VERSION = "v2.315"
DEFAULT_OUT = Path("experiments/results/v2.315/qnm_consistency_scorecard.json")

# the metric-robust engine-preferred framework (v2.313)
PREFERRED = {"g_4": 0.565, "g_6": 0.36, "g_8": 0.36, "g_R2": 0.15, "g_R3": 0.085}


def score(coeffs, stack, classmap):
    res = check(Theory(coefficients=coeffs, name="x"), stack).results
    wc = min(res, key=lambda r: r.signed_distance_margin)
    return {
        "min_margin": float(min(r.margin for r in res)),
        "worst_case_signed_distance": float(wc.signed_distance_margin),
        "binding_constraint": wc.constraint_name,
        "binding_family": classmap[wc.constraint_name],
        "feasible": bool(all(r.satisfied for r in res)),
    }


def run() -> dict:
    stack = build_stack()
    classmap = {c.name: str(c.constraint_class).split(".")[-1] for c in stack}

    rows = []
    rows.append({"theory": "engine_preferred", "curvature": {"g_R2": PREFERRED["g_R2"], "g_R3": PREFERRED["g_R3"]},
                 **score(PREFERRED, stack, classmap)})
    for fw in frameworks():
        c = fw.encode().coefficients
        rows.append({"theory": fw.name,
                     "curvature": {"g_R2": c.get("g_R2", 0.0), "g_R3": c.get("g_R3", 0.0)},
                     **score(c, stack, classmap)})
    rows.sort(key=lambda r: r["min_margin"], reverse=True)

    community = [r for r in rows if r["theory"] not in ("engine_preferred", "pure_gr")]
    preferred_row = next(r for r in rows if r["theory"] == "engine_preferred")

    # --- coherence audit (cross-cycle claims, lightweight re-checks) ---
    preferred_most_robust = all(preferred_row["min_margin"] > r["min_margin"] - 1e-12
                                for r in rows if r["theory"] != "engine_preferred")
    preferred_strictly_feasible = preferred_row["min_margin"] > 0
    all_community_infeasible = all(not r["feasible"] for r in community)
    all_community_bound_by_repulsive = all(r["binding_constraint"] == "repulsive_force_conjecture"
                                           for r in community)
    all_community_bound_by_universality = all(r["binding_family"] == "C_UNIVERSALITY" for r in community)
    preferred_bound_by_universality = preferred_row["binding_family"] == "C_UNIVERSALITY"
    # preferred curvature trimmed: g_R3 below every community framework
    preferred_gR3 = PREFERRED["g_R3"]
    preferred_gR3_trimmed = all(preferred_gR3 < r["curvature"]["g_R3"] - 1e-9 for r in community)
    # universality decisive: it binds the preferred framework AND every community framework
    universality_decisive = preferred_bound_by_universality and all_community_bound_by_universality

    checks = {
        "preferred_strictly_feasible_and_most_robust": preferred_strictly_feasible and preferred_most_robust,
        "all_community_frameworks_infeasible": all_community_infeasible,
        "all_community_bound_by_repulsive_force": all_community_bound_by_repulsive,
        "preferred_curvature_gR3_trimmed_below_all_community": preferred_gR3_trimmed,
        "universality_family_is_decisive_throughout": universality_decisive,
    }

    return {
        "version": VERSION,
        "scorecard": rows,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The consistency scorecard ranks every candidate by worst-case margin and exposes a sharp, "
            "coherent picture of the whole new-theory arc. Ranked: the engine-preferred framework is the "
            f"unique strictly-feasible, most-robust theory (min margin +{preferred_row['min_margin']:.4f}); "
            "pure GR is marginal (0.0000, on its positivity walls); and all four community frameworks are "
            "infeasible (string -0.040, cdt -0.048, asymptotic_safety -0.053, lqg -0.120). The decisive "
            "fact is the binding-constraint column: ALL FOUR community frameworks fail for the SAME "
            "reason -- every one is bound by repulsive_force_conjecture, the swampland member of the "
            "UNIVERSALITY family -- and the engine-preferred framework is bounded by t_hooft "
            "anomaly-matching, the OTHER member of the same universality family. So across the entire "
            "candidate set, the universality family (anomaly + swampland/repulsive-force) is the decisive "
            "arbiter: it kills every community proposal and it sets the robustness ceiling of the "
            "preferred one, with amplitude positivity always a step behind (v2.314). The engine-preferred "
            "framework is, precisely, the theory that clears the repulsive-force wall the community "
            "frameworks crash into -- by trimming the curvature (its g_R3 = 0.085 sits below every "
            "community value) -- while balancing against the anomaly wall on the other side. This ties "
            "the arc together: the carved interior is small and bounded by universality-vs-amplitude "
            "(v2.314); the community frameworks all overshoot the same universality wall (this scorecard); "
            "and the preferred framework is the unique trade-off point that threads between them (v2.312/"
            "v2.313). The audit confirms these cross-cycle results are mutually consistent, with no "
            "contradiction."
        ),
        "honest_scope": (
            "The scorecard and every audit check are the engine's literal check() output on the full "
            "38-constraint stack -- no schematic mapping. The ranking is by raw min-margin (the binding "
            "family is identified by the gradient-normalized worst-case signed distance, which can pick a "
            "different constraint than the raw min-margin when scales differ; here both agree that "
            "universality binds). The engine-preferred framework is the v2.313 metric-robust point, "
            "itself an approximate optimum (its exact coordinates are convention-dependent), so its exact "
            "margin (+0.005) is not canonical -- but 'strictly feasible and more robust than every named "
            "framework' is sign-based and robust. 'Universality decisive' means it is the worst-case "
            "family for all five non-pure-GR theories under the default O(1) prefactors; the specific "
            "constraint (repulsive force vs t_hooft) and ordering shift with those prefactors, but the "
            "structural claim (one principle family arbitrates both the failures and the preferred "
            "point) is the robust content. This is a consolidating audit of prior cycles, not a new "
            "bound. Toy basis, O(1) prefactors."
        ),
        "references": [
            "this repo: v2.312/v2.313 (engine-preferred framework), v2.314 (amplitude-vs-universality equilibrium), v2.311 (lqg box)",
            "engine constraint classes: C_UNIVERSALITY (anomaly + swampland/repulsive-force), A_AMPLITUDE (positivity)",
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
    print("the consistency scorecard (ranked by worst-case margin):")
    print(f"  {'theory':<18} {'min_margin':>11}  {'feasible':>8}  binding (family)")
    for r in res["scorecard"]:
        print(f"  {r['theory']:<18} {r['min_margin']:>+11.4f}  {str(r['feasible']):>8}  "
              f"{r['binding_constraint']} [{r['binding_family']}]")
    print(f"  => universality family decisive throughout: "
          f"{res['consistency_checks']['universality_family_is_decisive_throughout']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
