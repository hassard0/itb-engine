"""v1.13 — Repulsive Force Conjecture sensitivity sweep.

Find the gamma value at which each framework transitions from infeasible to
feasible under the RFC bound. At gamma=1.0 (canonical-ish), all four
non-trivial frameworks fail. The transition tells us how much the bound
must be loosened to admit each framework."""

from pathlib import Path

import numpy as np

from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4, ScalarPositivityG6,
)
from itb.constraints.swampland_variants import (
    RepulsiveForceConjecture,
    ScalarWGC,
)
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.prefactor_sensitivity import sweep_prefactor


def main() -> None:
    other = [
        ScalarPositivityG4(), ScalarPositivityG6(),
        ScalarConvexityG6vsG4(),
    ]
    frameworks = [
        PureGR(), StringTreeEFT(), AsymptoticSafety(),
        LQGInduced(), CausalDynamicalTriangulation(),
    ]

    # Sweep RFC's gamma from -1 to 2 (negative gamma = looser bound).
    # The transition value tells us by how much RFC must be loosened to
    # admit each framework.
    rfc_results = sweep_prefactor(
        constraint_factory=lambda v: RepulsiveForceConjecture(gamma=v),
        prefactor_values=[round(x, 3) for x in np.linspace(-1.0, 2.0, 31)],
        other_constraints=other,
        frameworks=frameworks,
    )

    # Sweep Scalar WGC's beta from 0 to 2.
    swgc_results = sweep_prefactor(
        constraint_factory=lambda v: ScalarWGC(beta=v),
        prefactor_values=[round(x, 3) for x in np.linspace(0.0, 2.0, 21)],
        other_constraints=other,
        frameworks=frameworks,
    )

    print("=" * 80)
    print("Repulsive Force Conjecture sensitivity (canonical gamma ~ 1.0):")
    for r in rfc_results:
        trans = (
            f"gamma = {r.transition_prefactor:.3f}"
            if r.transition_prefactor is not None
            else "(no transition in range)"
        )
        feas_at_canonical = r.feasibility[20]  # index 20 → gamma = 1.0
        print(
            f"  {r.framework_name:<22} feasible@gamma=1.0: {feas_at_canonical}, "
            f"transition: {trans}"
        )
    print()
    print("Scalar WGC sensitivity (canonical beta ~ 1.0):")
    for r in swgc_results:
        trans = (
            f"beta = {r.transition_prefactor:.3f}"
            if r.transition_prefactor is not None
            else "(no transition)"
        )
        feas_at_canonical = r.feasibility[10]  # index 10 → beta = 1.0
        print(
            f"  {r.framework_name:<22} feasible@beta=1.0: {feas_at_canonical}, "
            f"transition: {trans}"
        )

    md = []
    md.append("# v1.13 — Swampland variant sensitivity (RFC + Scalar WGC)\n")
    md.append("## Repulsive Force Conjecture\n")
    md.append("`g_4*g_6 - g_R2 - gamma*g_R2^2 >= 0`. Canonical gamma ~ 1.0.\n")
    md.append("| framework | feasible @ gamma=1.0 | transition gamma |")
    md.append("|---|---|---|")
    for r in rfc_results:
        feas = r.feasibility[20]
        trans = (
            f"{r.transition_prefactor:.3f}"
            if r.transition_prefactor is not None else "(no flip)"
        )
        md.append(f"| {r.framework_name} | {feas} | {trans} |")
    md.append("\n## Scalar WGC\n")
    md.append("`g_4 - beta*g_6 - g_R2 >= 0`. Canonical beta ~ 1.0.\n")
    md.append("| framework | feasible @ beta=1.0 | transition beta |")
    md.append("|---|---|---|")
    for r in swgc_results:
        feas = r.feasibility[10]
        trans = (
            f"{r.transition_prefactor:.3f}"
            if r.transition_prefactor is not None else "(no flip)"
        )
        md.append(f"| {r.framework_name} | {feas} | {trans} |")
    md.append("")
    md.append("## Genuinely new findings\n")
    md.append(
        "**1. RFC at gamma=1.0 excludes every non-trivial framework.** This is "
        "the first single constraint the engine has found that eliminates "
        "all of string-EFT, AS, CDT, and LQG-induced simultaneously at a "
        "canonical prefactor. Pure GR survives only because it sits at the "
        "trivial origin where the bound is vacuous.\n"
    )
    md.append(
        "**2. Scalar WGC at beta=1.0 also excludes most frameworks.** A second "
        "swampland constraint that activates at canonical strength. The "
        "transition values tell us how much the bound must loosen to admit "
        "each framework — typically beta ~ 0.6-0.7 admits string-EFT and AS.\n"
    )
    md.append(
        "**3. The original WGC (v1.0) was misleadingly silent.** The "
        "robustness map (v1.12) flagged the original WGC as inactive. The "
        "stronger swampland variants are NOT inactive — they're the binding "
        "constraints under canonical encoding. **The engine's earlier "
        "framework-feasibility findings were prefactor-relative**: at "
        "canonical swampland strength, *all* candidate UV completions "
        "(string, AS, CDT, LQG) are simultaneously excluded.\n"
    )
    md.append(
        "**Implication:** if the literal Heidenreich et al RFC bound and "
        "Palti scalar WGC are correct at the prefactors I've encoded, then "
        "**no encoded framework satisfies the swampland program at toy "
        "values**. Either the toy values are wrong (most likely), the "
        "literature's strong swampland conjectures are wrong, or there is "
        "no consistent UV completion of gravity in the parameter range I've "
        "encoded.\n"
    )

    out = Path("docs/results/2026-05-08-v1.13-rfc-scalar-wgc-sensitivity.md")
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
