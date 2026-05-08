"""v1.8 — the engine's sharpest answer.

Search for a theory in the 7-coefficient EFT space that satisfies ALL 24
constraints simultaneously. If one exists, report it. If not, report the
worst-case margin and which constraints are violated."""

from pathlib import Path

from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.anomaly_flow import (
    GeneralizedAnomalyInflow,
    tHooftAnomalyMatching,
)
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
from itb.constraints.complexity_cutoff import ComplexityCutoff
from itb.constraints.cubic_parity import ParityViolatingCubicBound
from itb.constraints.dispersion_tower import (
    DispersionTowerCauchySchwarz,
    ScalarPositivityG8,
)
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.graviton_self_coupling import (
    CubicCurvaturePositivity,
    CubicGravitonMatterBound,
)
from itb.constraints.holographic_entropy import (
    BNOSSWMonogamy,
    HolographicSubadditivity,
)
from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
from itb.constraints.parity_violation import (
    LIGOBirefringenceBound,
    LeftHandedGravitonPositivity,
    ParityViolatingPositivity,
    RightHandedGravitonPositivity,
)
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.constraints.swampland import WeakGravityConjecture
from itb.intersection_search import search_intersection


def main() -> None:
    constraints = [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarPositivityG8(),
        ScalarConvexityG6vsG4(), DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(), CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=1.0),
        BekensteinTight(), HolographicSubadditivity(), BNOSSWMonogamy(),
        ParityViolatingPositivity(kappa=1.0),
        LeftHandedGravitonPositivity(kappa=1.0),
        RightHandedGravitonPositivity(kappa=1.0),
        ParityViolatingCubicBound(kappa=1.0),
        LIGOBirefringenceBound(bound=0.1),
        EFTValidityBox(box=2.0), CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        GeneralizedAnomalyInflow(rho=0.06),
        tHooftAnomalyMatching(rho_match=0.5, slack=0.02),
        WeakGravityConjecture(alpha=1.0),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=1.5),
    ]

    print(f"Searching for a theory satisfying all {len(constraints)} constraints...")
    print()

    initial_guesses = {
        "near_pure_gr": {
            "g_4": 0.01, "g_6": 0.01, "g_8": 0.01, "g_R2": 0.01,
            "g_R3": 0.01, "g_R2_parity": 0.0, "g_R3_parity": 0.0,
        },
        "near_string_eft": {
            "g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.2,
            "g_R3": 0.15, "g_R2_parity": 0.0, "g_R3_parity": 0.0,
        },
        "near_asymptotic_safety": {
            "g_4": 0.4, "g_6": 0.3, "g_8": 0.3, "g_R2": 0.15,
            "g_R3": 0.10, "g_R2_parity": 0.0, "g_R3_parity": 0.0,
        },
    }

    results = []
    for name, guess in initial_guesses.items():
        res = search_intersection(
            constraints=constraints,
            initial_guess=guess,
            max_iters=2000,
        )
        results.append((name, res))
        print(f"== Starting from {name} ==")
        print(f"  feasible:           {res.feasible}")
        print(f"  worst-case margin:  {res.worst_case_margin:.6f}")
        print(f"  violated count:     {len(res.constraints_violated)}")
        print(f"  binding count:      {len(res.constraints_binding)}")
        if res.constraints_violated:
            print(f"  violated:           {res.constraints_violated[:5]}"
                  f"{'...' if len(res.constraints_violated) > 5 else ''}")
        print(f"  status:             {res.optimizer_status}")
        print()

    # Summary doc
    md: list[str] = []
    md.append("# v1.8 — The Engine's Sharpest Answer")
    md.append("")
    md.append(f"Constraint count: **{len(constraints)}**")
    md.append("Wilson coefficients: **7** (g_4, g_6, g_8, g_R2, g_R3, g_R2_parity, g_R3_parity)")
    md.append("")
    md.append("## Intersection-search results")
    md.append("")
    md.append("| starting point | feasible | worst margin | violated | binding |")
    md.append("|---|---|---|---|---|")
    for name, res in results:
        md.append(
            f"| {name} | {res.feasible} | {res.worst_case_margin:.6f} | "
            f"{len(res.constraints_violated)} | {len(res.constraints_binding)} |"
        )
    md.append("")
    md.append("## Final coefficients (best run)")
    md.append("")
    best_name, best_res = max(results, key=lambda r: r[1].worst_case_margin)
    md.append(f"Best result starting from `{best_name}`:")
    md.append("")
    md.append("| coefficient | value |")
    md.append("|---|---|")
    for k, v in sorted(best_res.coefficients.items()):
        md.append(f"| {k} | {v:.6f} |")
    md.append("")
    if best_res.feasible:
        md.append("**The intersection is non-empty.** A theory satisfying all 24 constraints exists in the 7-coefficient EFT space at toy values.")
    else:
        md.append(
            "**The intersection is empty (or numerically below margin) at toy "
            "values.** No theory in the 7-coefficient EFT space simultaneously "
            "satisfies all 24 constraints under the encodings tested. The "
            "violated constraints flag which physical principles are mutually "
            "incompatible at this encoding precision."
        )
        md.append("")
        md.append(f"**Constraints violated:** {best_res.constraints_violated}")
    out = Path("docs/results/2026-05-08-v1.8-intersection-search.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
