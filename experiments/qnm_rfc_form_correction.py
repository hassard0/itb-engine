"""v2.316 - Correction: the 'all frameworks infeasible' verdict was a deprecated-RFC-form artifact.

A scrutiny cycle on the decisive constraint of the recent arc. v2.315 found that every community framework
is infeasible, all bound by repulsive_force_conjecture (the universality/swampland member), and built a
whole picture on it ('only pure GR feasible', 'universality decisive', 'the engine prefers a unique
constructed framework over all community ones', v2.312-v2.315). On scrutiny that verdict is an ARTIFACT of
a deprecated constraint encoding -- and the engine itself documents this.

build_stack() defaults to the repulsive-force conjecture in its ``matter_product`` form
(g_4*g_6 - g_R2 - gamma*g_R2^2 >= 0). The engine's own docstring (RepulsiveForceConjecture) says this form
'excludes EVERY candidate framework for any gamma>0 -- a 100% universal exclusion that is an artifact of
the spurious product (the encoded frameworks all have g_4*g_6 ~ g_R2 by construction)', and recommends the
physically-corrected ``convex_hull`` form (g_4 - g_R2 - gamma*g_R2^2 >= 0) for new analyses, which
'excludes none of them, isolating the real discriminating physics in the complexity-cutoff and
cubic-curvature constraints'. The recent cycles used the default and so inherited the artifact.

Under the recommended form the picture changes decisively: three of the four community frameworks become
FEASIBLE; only lqg remains infeasible -- and for the cubic-curvature / cft reason v2.311 already
identified (its outlier g_R3), not the repulsive-force box. This cycle documents the correction and
separates what was artifact from what is robust.
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
from itb.constraints.swampland_variants import RepulsiveForceConjecture

VERSION = "v2.316"
DEFAULT_OUT = Path("experiments/results/v2.316/qnm_rfc_form_correction.json")


def score_all(form):
    stack = build_stack(rfc_form=form)
    cm = {c.name: str(c.constraint_class).split(".")[-1] for c in stack}
    rows = []
    for fw in frameworks():
        res = check(fw.encode(), stack).results
        wc = min(res, key=lambda r: r.signed_distance_margin)
        rows.append({"framework": fw.name,
                     "min_margin": float(min(r.margin for r in res)),
                     "feasible": bool(all(r.satisfied for r in res)),
                     "n_fail": int(sum(1 for r in res if not r.satisfied)),
                     "binding": wc.constraint_name, "binding_family": cm[wc.constraint_name]})
    return rows


def run() -> dict:
    # confirm the default form
    default_stack = build_stack()
    rfc = next((c for c in default_stack if c.name == "repulsive_force_conjecture"), None)
    default_form = getattr(rfc, "form", None)

    mp = score_all("matter_product")
    ch = score_all("convex_hull")
    by = {r["framework"]: r for r in mp}
    cy = {r["framework"]: r for r in ch}

    community = ["string_tree_eft", "asymptotic_safety", "lqg_induced", "cdt"]
    mp_all_community_infeasible = all(not by[f]["feasible"] for f in community)
    ch_newly_feasible = sorted(f for f in community if not by[f]["feasible"] and cy[f]["feasible"])
    ch_still_infeasible = sorted(f for f in community if not cy[f]["feasible"])
    lqg_infeasible_both = (not by["lqg_induced"]["feasible"]) and (not cy["lqg_induced"]["feasible"])
    # under the recommended form, the discriminating physics for lqg is cubic-curvature / cft, not RFC
    lqg_binding_ch = cy["lqg_induced"]["binding"]
    docstring = RepulsiveForceConjecture.__doc__ or ""
    engine_documents_artifact = ("artifact" in docstring and "convex_hull" in docstring
                                 and "excludes EVERY candidate framework" in docstring)

    checks = {
        "default_rfc_form_is_matter_product": default_form == "matter_product",
        "matter_product_excludes_all_community": mp_all_community_infeasible,
        "convex_hull_makes_three_community_feasible": ch_newly_feasible == ["asymptotic_safety", "cdt", "string_tree_eft"],
        "lqg_infeasible_under_both_forms": lqg_infeasible_both,
        "engine_docstring_documents_the_artifact": engine_documents_artifact,
    }

    return {
        "version": VERSION,
        "default_rfc_form": default_form,
        "scores_matter_product": mp,
        "scores_convex_hull": ch,
        "newly_feasible_under_convex_hull": ch_newly_feasible,
        "still_infeasible_under_convex_hull": ch_still_infeasible,
        "lqg_binding_under_convex_hull": lqg_binding_ch,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The recent arc's decisive verdict -- 'all community frameworks infeasible, all bound by "
            "repulsive_force_conjecture, universality decisive' (v2.315), and 'the engine prefers a "
            "unique constructed framework over every community one' (v2.312) -- is an ARTIFACT of a "
            "deprecated constraint encoding, which the engine itself documents. build_stack() defaults "
            "the repulsive-force conjecture to its matter_product form (g_4*g_6 - g_R2 - gamma*g_R2^2 "
            ">= 0); the RepulsiveForceConjecture docstring states this form 'excludes EVERY candidate "
            "framework for any gamma>0 -- a 100% universal exclusion that is an artifact of the spurious "
            "product (the encoded frameworks all have g_4*g_6 ~ g_R2 by construction)', and recommends "
            "the physically-corrected convex_hull form (g_4 - g_R2 - gamma*g_R2^2 >= 0) for new "
            "analyses. Re-scoring under the recommended form changes the picture decisively: three of the "
            "four community frameworks become FEASIBLE -- string_tree_eft (+0.0060), asymptotic_safety "
            "(+0.0036), and cdt (+0.0073) -- and only lqg_induced remains infeasible (-0.075), now bound "
            f"by {lqg_binding_ch} (a cubic-curvature / CFT condition), exactly the 'real discriminating "
            "physics' the docstring points to and the outlier-g_R3 mechanism v2.311 already identified. "
            "So the honest correction: the 'universal exclusion' and 'engine prefers a unique framework' "
            "headlines of v2.312-v2.315 were specific to the deprecated default form; under the engine's "
            "recommended form the community higher-derivative frameworks (except lqg) ARE in the "
            "consistent region. What survives is narrower but real: lqg is infeasible under BOTH forms -- "
            "the genuine boundary framework -- and its infeasibility traces to its outlier cubic "
            "curvature (v2.311's primary finding), not to the repulsive-force box (v2.311's secondary, "
            "matter_product-specific finding). The carving / convexity / moment-tower / finite-cutoff / "
            "cosmology results, which do not invoke the repulsive-force conjecture, are unaffected. Future "
            "cycles should pass form='convex_hull'."
        ),
        "honest_scope": (
            "This is a self-correction, and the correction itself is the engine's literal verdict: the "
            "form-dependence is direct check() output, and the artifact is documented in the engine's own "
            "RepulsiveForceConjecture docstring (citing a prior 2026-06-08 realism study). The default "
            "build_stack() uses matter_product, so every recent cycle that called build_stack() with no "
            "rfc_form argument inherited it -- the affected headlines are the FEASIBILITY verdicts that "
            "depended on the repulsive-force constraint (v2.312 'engine-preferred framework more robust "
            "than all community', v2.315 'all community infeasible / universality decisive', and the "
            "'only pure GR feasible' framing). Results that do not involve the repulsive-force conjecture "
            "-- the curvature carving (v2.292/v2.302/v2.303/v2.309), convexity (v2.304/v2.305), "
            "finite-cutoff Hausdorff (v2.306), and cosmology (v2.307/v2.308) -- are unaffected. lqg's "
            "boundary status (v2.310/v2.311) is partly robust: lqg is infeasible under both forms, and "
            "its outlier-g_R3 primary mechanism holds, but its repulsive-vs-anomaly box (v2.311 secondary) "
            "was matter_product-specific. The exact convex_hull margins still carry the O(1) prefactor "
            "caveat. Toy basis, O(1) prefactors. An honest correction of the recent arc's central "
            "feasibility claims."
        ),
        "references": [
            "src/itb/constraints/swampland_variants.py (RepulsiveForceConjecture docstring; the artifact note)",
            "this repo: v2.315 (scorecard, now corrected), v2.312 (preferred framework), v2.311 (lqg g_R3 outlier -- robust)",
            "docs/results/2026-06-08-* (the prior prefactor-realism study that found the matter_product artifact)",
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
    print(f"RFC-form correction (default form = {res['default_rfc_form']}):")
    print(f"  {'framework':<18} {'matter_product':>16} {'convex_hull (rec.)':>20}")
    for f in ["string_tree_eft", "asymptotic_safety", "cdt", "lqg_induced"]:
        bp = next(r for r in res["scores_matter_product"] if r["framework"] == f)
        cp = next(r for r in res["scores_convex_hull"] if r["framework"] == f)
        print(f"  {f:<18} {bp['min_margin']:>+10.4f} {str(bp['feasible']):>5}  "
              f"{cp['min_margin']:>+10.4f} {str(cp['feasible']):>5}")
    print(f"  newly feasible under recommended form: {res['newly_feasible_under_convex_hull']}")
    print(f"  still infeasible: {res['still_infeasible_under_convex_hull']} (lqg binding {res['lqg_binding_under_convex_hull']})")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
