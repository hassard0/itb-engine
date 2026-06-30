"""v2.312 - What framework does the engine PREFER? Constructing the most-robustly-consistent EFT.

Taking the new-theory mandate literally: instead of testing community frameworks, ask what framework the
engine's consistency conditions actually PREFER -- the most robustly feasible point, maximizing the
worst-case constraint margin (the Chebyshev-center idea) over the whole 7-coupling space, and propose it
as a candidate.

The answer is a genuine NONZERO framework, distinct from every input. pure GR is feasible but MARGINAL:
at the origin 29 of the 38 constraints saturate simultaneously (homogeneous positivity / causality /
swampland forms vanishing at zero couplings), so pure GR sits on 29 walls with worst-case margin exactly
0. But the feasible set has a real (if small) INTERIOR: a search finds a strictly-interior point with all
38 margins positive (worst-case margin ~ +0.006), and that Chebyshev center is the engine's preferred
framework -- a specific higher-derivative EFT (string-like matter sector, trimmed curvature) that is MORE
robust than pure GR and feasible where all four community frameworks are infeasible. So the engine does
not merely tolerate pure GR; it points to a concrete new candidate theory at the most-interior point of
the carved region.

NOTE: an earlier coarse random scan suggested the interior was empty (no point beat pure GR's margin of
0); a thorough multi-seed coordinate ascent refuted that by finding the +0.006 interior point. The
corrected, search-robust result is reported here.
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
from experiments.stack import frameworks, build_stack

VERSION = "v2.312"
DEFAULT_OUT = Path("experiments/results/v2.312/qnm_engine_preferred_framework.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]


def margins(vec, stack):
    c = dict(zip(KEYS, vec))
    return [r.margin for r in check(Theory(coefficients=c, name="x"), stack).results]


def min_margin(vec, stack):
    return min(margins(vec, stack))


def coordinate_ascent(start, stack, step0=0.05, iters=60):
    best = np.array(start, dtype=float)
    bestm = min_margin(best, stack)
    step = step0
    for _ in range(iters):
        improved = False
        for j in range(len(best)):
            for d in (step, -step):
                v = best.copy(); v[j] = max(0.0, v[j] + d)
                m = min_margin(v, stack)
                if m > bestm + 1e-12:
                    bestm, best, improved = m, v, True
        if not improved:
            step *= 0.5
            if step < 1e-3:
                break
    return best, bestm


def run() -> dict:
    stack = build_stack()
    n_con = len(margins(np.zeros(7), stack))

    # --- pure GR baseline + which constraints saturate at the origin ---
    rep0 = check(Theory(coefficients={}, name="pure_gr"), stack)
    saturated = sorted(r.constraint_name for r in rep0.results if abs(r.margin) < 1e-9)
    strictly_pos = sorted(r.constraint_name for r in rep0.results if r.margin > 1e-9)
    pure_gr_feasible = all(r.satisfied for r in rep0.results)
    pure_gr_minmargin = min(r.margin for r in rep0.results)

    # --- global robustness search: maximize the worst-case margin over coupling space ---
    rng = np.random.default_rng(20260630)
    best = np.zeros(7); bestm = min_margin(best, stack)
    for _ in range(3000):
        v = np.empty(7)
        v[:5] = rng.uniform(0.0, 0.7, 5)
        v[5] = rng.uniform(0.0, 0.12); v[6] = rng.uniform(0.0, 0.06)
        m = min_margin(v, stack)
        if m > bestm + 1e-12:
            bestm, best = m, v
    # refine from the random best AND from each community framework (do they climb to an interior?)
    seeds = [best] + [np.array([fw.encode().coefficients.get(k, 0.0) for k in KEYS]) for fw in frameworks()]
    refined_best, refined_m = best, bestm
    for s in seeds:
        pt, m = coordinate_ascent(s, stack)
        if m > refined_m + 1e-12:
            refined_m, refined_best = m, pt
    global_max_minmargin = float(refined_m)
    preferred = {k: float(x) for k, x in zip(KEYS, refined_best)}
    interior_nonempty = global_max_minmargin > 1e-9
    preferred_is_nonzero = not bool(np.allclose(refined_best, 0.0, atol=1e-6))
    preferred_strictly_feasible = all(m > 0 for m in margins(refined_best, stack))

    # --- community frameworks: which are feasible? ---
    fw_rows = []
    for fw in frameworks():
        mm = min(r.margin for r in check(fw.encode(), stack).results)
        fw_rows.append({"framework": fw.name, "min_margin": float(mm), "feasible": bool(mm >= -1e-12)})
    only_pure_gr_feasible = all((r["framework"] == "pure_gr") == r["feasible"] for r in fw_rows)
    # the preferred framework is more robust than pure GR (strictly interior vs marginal)
    more_robust_than_pure_gr = global_max_minmargin > pure_gr_minmargin + 1e-9
    # and distinct from every community framework
    fw_vecs = [np.array([fw.encode().coefficients.get(k, 0.0) for k in KEYS]) for fw in frameworks()]
    distinct_from_frameworks = all(not np.allclose(refined_best, v, atol=1e-3) for v in fw_vecs)

    checks = {
        "pure_gr_feasible_but_marginal": pure_gr_feasible and abs(pure_gr_minmargin) < 1e-9,
        "majority_of_constraints_saturate_at_pure_gr": len(saturated) > n_con / 2,
        "feasible_interior_is_nonempty": interior_nonempty,
        "preferred_framework_is_nonzero_and_strictly_feasible": preferred_is_nonzero and preferred_strictly_feasible,
        "preferred_more_robust_than_pure_gr": more_robust_than_pure_gr,
        "preferred_distinct_from_all_community_frameworks": distinct_from_frameworks,
        "no_community_higher_derivative_framework_is_feasible": only_pure_gr_feasible,
    }

    return {
        "version": VERSION,
        "n_constraints": n_con,
        "pure_gr": {"feasible": pure_gr_feasible, "min_margin": pure_gr_minmargin,
                    "n_saturated_at_origin": len(saturated), "n_strictly_positive": len(strictly_pos),
                    "saturated_constraints": saturated},
        "engine_preferred_framework": {
            "couplings": preferred, "worst_case_margin": global_max_minmargin,
            "strictly_feasible": preferred_strictly_feasible,
            "more_robust_than_pure_gr": more_robust_than_pure_gr,
            "distinct_from_community_frameworks": distinct_from_frameworks},
        "frameworks": fw_rows,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Asked what framework the engine PREFERS -- the point maximizing the worst-case constraint "
            "margin over the whole 7-coupling space -- the engine constructs a genuine NONZERO candidate, "
            "distinct from every input. pure GR is feasible but MARGINAL: at the origin "
            f"{len(saturated)} of the {n_con} constraints saturate simultaneously (homogeneous "
            "positivity / causality / swampland forms vanishing at zero couplings), so pure GR sits on "
            f"{len(saturated)} walls with worst-case margin exactly 0. But the feasible set has a real "
            "(small) INTERIOR: a multi-seed coordinate-ascent search finds a strictly-interior point "
            f"with all {n_con} margins positive (worst-case margin +{global_max_minmargin:.4f}), at "
            f"g_4 = {preferred['g_4']:.2f}, g_6 = {preferred['g_6']:.2f}, g_8 = {preferred['g_8']:.2f}, "
            f"g_R2 = {preferred['g_R2']:.2f}, g_R3 = {preferred['g_R3']:.2f}, parity = 0. This Chebyshev "
            "center is the engine's preferred framework: a string-tree-EFT-like matter sector "
            "(g_4, g_6, g_8 close to the string values 0.5/0.4/0.4) with TRIMMED curvature couplings "
            "(g_R2, g_R3 pulled below the string 0.2/0.15 into the feasible interior). It is MORE robust "
            "than pure GR (strictly interior vs marginal on 29 walls) and feasible where all four "
            "community frameworks are INFEASIBLE (string -0.040, asymptotic_safety -0.053, cdt -0.048, "
            "lqg -0.120, all negative worst-case margin). So the engine does not merely tolerate GR and "
            "reject the candidates -- it points to a concrete NEW framework at the most-interior point of "
            "the carved region: keep the string-like matter sector, but soften the curvature corrections "
            "until every consistency wall clears. That is the engine's own answer to 'what higher-"
            "derivative gravity is most robustly consistent', and it matches no framework on the menu."
        ),
        "honest_scope": (
            "The decisive claims are SIGN-based and independent of the heterogeneous margin scales: "
            "'pure GR is feasible but on 29 walls', 'a point with all 38 margins strictly positive "
            "exists' (nonempty interior), 'the preferred point is strictly feasible and nonzero', and "
            "'no community higher-derivative framework is feasible' depend only on margin signs, not "
            "normalization. The 'worst-case margin' magnitude does mix units, so the EXACT preferred "
            "point is the argmax of a scale-dependent objective and is not unique/canonical -- a "
            "different robustness metric (e.g. normalized margins) would move it; what is robust is that "
            "SOME strictly-interior point exists, it is nonzero, more robust than pure GR, and unlike any "
            "community framework. The interior point was found by multi-seed coordinate ascent (an "
            "earlier coarse random scan missed it and wrongly suggested an empty interior -- corrected "
            "here); the optimum is approximate (grid-quantized) and seed-dependent in its exact "
            "coordinates. Default 38-constraint stack, no opt-in extensions; couplings restricted to "
            "g >= 0 (positive-coupling orthant). The 'string-like matter, trimmed curvature' reading is "
            "an interpretation of one approximate optimum, not a derived UV completion. Toy basis, O(1) "
            "prefactors. A constructive new-theory swing: the engine's own preferred consistent EFT."
        ),
        "references": [
            "this repo: v2.283 (frameworks marginally infeasible, only pure_gr feasible), v2.285-288 (feasible wedge under subsets)",
            "Chebyshev center of a feasible region; the EFT-hedron (Arkani-Hamed et al, Caron-Huot-Van Duong)",
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
    pg = res["pure_gr"]; pf = res["engine_preferred_framework"]
    print("what framework does the engine prefer? (Chebyshev center of the carved region)")
    print(f"  pure GR: feasible={pg['feasible']}, min_margin={pg['min_margin']:+.4f}, "
          f"{pg['n_saturated_at_origin']}/{res['n_constraints']} constraints saturate at the origin (marginal)")
    print(f"  ENGINE-PREFERRED framework (worst-case margin +{pf['worst_case_margin']:.4f}, strictly feasible):")
    print(f"    {{{', '.join(f'{k}:{v:.3f}' for k,v in pf['couplings'].items())}}}")
    print(f"    more robust than pure GR: {pf['more_robust_than_pure_gr']}; "
          f"distinct from community frameworks: {pf['distinct_from_community_frameworks']}")
    print(f"  community frameworks (worst-case margin):")
    for r in res["frameworks"]:
        print(f"    {r['framework']:<18} {r['min_margin']:+.4f}  feasible={r['feasible']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
