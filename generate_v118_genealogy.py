"""v1.18 - Constraint genealogy: which constraint does which work."""

from pathlib import Path

from itb.constraint_genealogy import trace_genealogy, render_genealogy_report
from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.anomaly_flow import (
    GeneralizedAnomalyInflow, tHooftAnomalyMatching,
)
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
from itb.constraints.cft_flat_space import CFTFlatSpaceBound
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


def main() -> None:
    constraints = [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarPositivityG8(),
        ScalarConvexityG6vsG4(), DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(), CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=1.0), SpinFourPositivity(),
        CFTFlatSpaceBound(alpha=0.5),
        BekensteinTight(), HolographicSubadditivity(), BNOSSWMonogamy(),
        QuantumFocusingConjecture(), GeneralizedSecondLaw(),
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
        ScalarWGC(beta=1.0), RepulsiveForceConjecture(gamma=1.0),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=1.5),
        DistanceConjecture(R_max=20.0),
    ]
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(),
                  LQGInduced(), CausalDynamicalTriangulation()]

    records = trace_genealogy(frameworks, constraints)
    print(f"Genealogy across {len(constraints)} constraints, {len(frameworks)} frameworks:\n")
    print(f"{'constraint':<35} {'binds':<35} {'sole violation':<25}")
    print("-" * 95)
    for r in records:
        if r.n_frameworks_active == 0:
            continue
        print(f"{r.constraint_name:<35} {','.join(r.binds_at_origin_for):<35} "
              f"{','.join(r.is_only_violation_for):<25}")

    n_active = sum(1 for r in records if r.n_frameworks_active > 0)
    n_inactive = len(records) - n_active
    print(f"\n{n_active} constraints active, {n_inactive} inactive at toy values")

    md = render_genealogy_report(records)
    md += f"\n\n## Summary\n\n- Active constraints: {n_active}\n"
    md += f"- Inactive constraints: {n_inactive}\n"
    md += f"- Of {len(constraints)} total: {100*n_active/len(constraints):.0f}% are doing visible work\n"
    out = Path("docs/results/2026-05-08-v1.18-constraint-genealogy.md")
    out.write_text(md, encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
