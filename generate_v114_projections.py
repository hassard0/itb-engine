"""v1.14 — Project each encoded framework onto the feasible region.

For each of the 5 frameworks, find the L2-nearest feasible point in
7D Wilson-coefficient space under the full v1.13 constraint stack
(including Scalar WGC and Repulsive Force Conjecture at canonical
prefactors). The shift tells us where each framework's toy values
are most off from the engine-allowed region.

Publication-actionable output: a table per framework showing
'engine-corrected' Wilson coefficients to compare against literature
predictions."""

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
from itb.constraints.swampland_variants import (
    RepulsiveForceConjecture, ScalarWGC,
)
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.projection import (
    project_framework_to_feasible,
    render_projection_report,
)


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
        ScalarWGC(beta=1.0),
        RepulsiveForceConjecture(gamma=1.0),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=1.5),
        DistanceConjecture(R_max=20.0),
    ]
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(),
                  LQGInduced(), CausalDynamicalTriangulation()]

    print(f"Projecting 5 frameworks onto {len(constraints)}-constraint feasible region\n")
    projections = []
    for fw in frameworks:
        proj = project_framework_to_feasible(fw, constraints, max_iters=1000)
        projections.append(proj)
        print(f"  {fw.name:<20} feasible: {proj.feasible}, shift: {proj.shift_distance:.4f}")

    print("\nDetail per framework:")
    for p in projections:
        print(f"\n{p.framework_name}:")
        for k, shift in sorted(p.coefficient_shifts.items()):
            if abs(shift) > 1e-4:
                orig = p.original_coefficients[k]
                proj = p.projected_coefficients[k]
                print(f"  {k:<15} {orig:.4f} -> {proj:.4f}  (shift {shift:+.4f})")

    md = render_projection_report(projections)
    out = Path("docs/results/2026-05-08-v1.14-framework-projections.md")
    out.write_text(md, encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
