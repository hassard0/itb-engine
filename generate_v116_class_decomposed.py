"""v1.16 - Class-decomposed projection.

Run projection three ways: class-A-only constraints, class-B-only, class-C-only.
For each framework, compare the three projected coefficient sets to see which
class of physics is responsible for which part of the convergence."""

from pathlib import Path

import numpy as np

from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.anomaly_flow import (
    GeneralizedAnomalyInflow, tHooftAnomalyMatching,
)
from itb.constraints.base import ConstraintClass
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
from itb.constraints.swampland_variants import (
    RepulsiveForceConjecture, ScalarWGC,
)
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.projection import project_framework_to_feasible


def main() -> None:
    all_constraints = [
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
        ScalarWGC(beta=1.0),
        RepulsiveForceConjecture(gamma=1.0),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=1.5),
        DistanceConjecture(R_max=20.0),
    ]

    by_class = {
        "A": [c for c in all_constraints if c.constraint_class is ConstraintClass.A_AMPLITUDE],
        "B": [c for c in all_constraints if c.constraint_class is ConstraintClass.B_INFORMATION],
        "C": [c for c in all_constraints if c.constraint_class is ConstraintClass.C_UNIVERSALITY],
    }

    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(),
                  LQGInduced(), CausalDynamicalTriangulation()]

    print("Class membership:")
    for cls_label, cs in by_class.items():
        print(f"  Class {cls_label}: {len(cs)} constraints")
    print()

    for fw in frameworks:
        if fw.name == "pure_gr":
            continue
        print(f"=== {fw.name} ===")
        original = fw.encode().coefficients
        for cls_label in ("A", "B", "C"):
            proj = project_framework_to_feasible(fw, by_class[cls_label], max_iters=500)
            shifts = {
                k: proj.projected_coefficients.get(k, 0) - original.get(k, 0)
                for k in original
            }
            big_shifts = {k: v for k, v in shifts.items() if abs(v) > 0.005}
            print(f"  class {cls_label}: shift dist {proj.shift_distance:.4f}, "
                  f"big shifts: {big_shifts}")
        print()

    # Generate report
    md = []
    md.append("# v1.16 - Class-decomposed projection\n")
    md.append("Each framework projected onto class-A-only, class-B-only, class-C-only "
              "feasible regions. The shift differences identify which class is "
              "responsible for which convergence direction.\n")
    md.append("| framework | class | shift dist | dominant g_R2 shift | dominant g_4 shift |")
    md.append("|---|---|---|---|---|")
    for fw in frameworks:
        if fw.name == "pure_gr":
            continue
        original = fw.encode().coefficients
        for cls_label in ("A", "B", "C"):
            proj = project_framework_to_feasible(fw, by_class[cls_label], max_iters=500)
            gR2_shift = proj.projected_coefficients.get("g_R2", 0) - original.get("g_R2", 0)
            g4_shift = proj.projected_coefficients.get("g_4", 0) - original.get("g_4", 0)
            md.append(
                f"| {fw.name} | {cls_label} | {proj.shift_distance:.4f} | "
                f"{gR2_shift:+.4f} | {g4_shift:+.4f} |"
            )
    md.append("")
    md.append("## Reading\n")
    md.append("Each row: how does the framework move when only that class of "
              "constraint is active? The class causing the largest shift is the "
              "one driving that framework's convergence in v1.14's full-stack "
              "projection.\n")
    out = Path("docs/results/2026-05-08-v1.16-class-decomposed-projection.md")
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
