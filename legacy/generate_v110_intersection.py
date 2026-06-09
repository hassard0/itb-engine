"""v1.10 — re-run intersection search after Dr. M.'s 5 new modules."""

from pathlib import Path

from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.anomaly_flow import (
    GeneralizedAnomalyInflow, tHooftAnomalyMatching,
)
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
from itb.constraints.complexity_cutoff import ComplexityCutoff
from itb.constraints.cubic_parity import ParityViolatingCubicBound
from itb.constraints.dispersion_tower import (
    DispersionTowerCauchySchwarz, ScalarPositivityG8,
)
from itb.constraints.distance_conjecture import DistanceConjecture
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.generalized_second_law import GeneralizedSecondLaw
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.graviton_self_coupling import (
    CubicCurvaturePositivity, CubicGravitonMatterBound,
)
from itb.constraints.holographic_entropy import (
    BNOSSWMonogamy, HolographicSubadditivity,
)
from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
from itb.constraints.parity_violation import (
    LIGOBirefringenceBound, LeftHandedGravitonPositivity,
    ParityViolatingPositivity, RightHandedGravitonPositivity,
)
from itb.constraints.quantum_focusing import QuantumFocusingConjecture
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4, ScalarPositivityG6,
)
from itb.constraints.spin_four_positivity import SpinFourPositivity
from itb.constraints.swampland import WeakGravityConjecture
from itb.engine import check
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.intersection_search import search_intersection


def main() -> None:
    constraints = [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarPositivityG8(),
        ScalarConvexityG6vsG4(), DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(), CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=1.0),
        SpinFourPositivity(),
        BekensteinTight(), HolographicSubadditivity(), BNOSSWMonogamy(),
        QuantumFocusingConjecture(),
        GeneralizedSecondLaw(),
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
        DistanceConjecture(R_max=20.0),
    ]
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(),
                  LQGInduced(), CausalDynamicalTriangulation()]

    print(f"v1.10 status with {len(constraints)} constraints (Dr. M.'s 5 additions in):")
    for fw in frameworks:
        theory = fw.encode()
        report = check(theory, constraints)
        binding = report.binding or "—"
        print(f"  {fw.name:<20} feasible={report.feasible}  binding={binding}")
    print()

    initial = {
        "g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.2,
        "g_R3": 0.15, "g_R2_parity": 0.0, "g_R3_parity": 0.0,
    }
    res = search_intersection(constraints, initial, max_iters=2000)
    print(f"Intersection search result:")
    print(f"  feasible:           {res.feasible}")
    print(f"  worst-case margin:  {res.worst_case_margin:.6f}")
    if res.feasible:
        print(f"  v1.10 optimum coefficients:")
        for k, v in sorted(res.coefficients.items()):
            print(f"    {k}: {v:.6f}")
    else:
        print(f"  violated:           {res.constraints_violated}")

    md = []
    md.append("# v1.10 — Intersection search after Dr. M.'s 5 additions\n")
    md.append(f"Total constraints: **{len(constraints)}**\n")
    md.append(f"Total frameworks: **{len(frameworks)}**\n\n")
    md.append("## Per-framework status\n")
    md.append("| framework | feasible | binding |")
    md.append("|---|---|---|")
    for fw in frameworks:
        theory = fw.encode()
        report = check(theory, constraints)
        md.append(f"| {fw.name} | {report.feasible} | {report.binding or '—'} |")
    md.append("\n## Intersection optimum\n")
    md.append(f"- feasible: **{res.feasible}**")
    md.append(f"- worst-case margin: **{res.worst_case_margin:.6f}**\n")
    if res.feasible:
        md.append("| coefficient | v1.8 value | v1.10 value |")
        md.append("|---|---|---|")
        v18_optimum = {
            "g_4": 0.622, "g_6": 0.395, "g_8": 0.359,
            "g_R2": 0.233, "g_R3": 0.151,
            "g_R2_parity": 0.000, "g_R3_parity": -0.001,
        }
        for k in sorted(res.coefficients.keys()):
            v10 = res.coefficients[k]
            v18 = v18_optimum.get(k, 0.0)
            md.append(f"| {k} | {v18:.4f} | {v10:.4f} |")
    out = Path("docs/results/2026-05-08-v1.10-intersection-update.md")
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
