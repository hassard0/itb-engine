"""v1.19 - Updated experimental priority ranking with v1.18 stack."""

from pathlib import Path

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
from itb.experiment_priority import (
    ExperimentForecast, rank_experiments, render_priority_list,
)


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
    experiments = [
        ExperimentForecast("LIGO_O5_graviton_mass", "g_R2", 0.0, 0.05),
        ExperimentForecast("LIGO_O5_birefringence_forecast", "g_R2_parity", 0.0, 0.005),
        ExperimentForecast("LIGO_O4_birefringence", "g_R2_parity", 0.0, 0.02),
        ExperimentForecast("Eot_Wash_equivalence", "g_R2", 0.0, 0.02),
        ExperimentForecast("CMB_S4_inflationary_EFT", "g_4", 0.5, 0.10),
        ExperimentForecast("CMB_S4_TIGHT", "g_4", 0.0, 0.03),
        ExperimentForecast("Lattice_QCD_g6_bound", "g_6", 0.4, 0.15),
        ExperimentForecast("Atomic_clock_Lorentz", "g_8", 0.4, 0.10),
        ExperimentForecast("Bouwmeester_collapse_test", "g_R2", 0.0, 0.005),  # Penrose-Diosi target
        ExperimentForecast("Bouwmeester_g_R3", "g_R3", 0.0, 0.005),
    ]
    rankings = rank_experiments(
        base_constraints=constraints,
        experiments=experiments,
        x_param="g_R2", x_range=(0.0, 0.5), x_steps=21,
        y_param="g_R2_parity", y_range=(-0.2, 0.2), y_steps=21,
        fixed_coefficients={"g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R3": 0.15},
    )
    md = render_priority_list(rankings)
    md += "\n\n## v1.4 → v1.19 ranking comparison\n\n"
    md += (
        "**v1.4 top three** (15 constraints): LIGO O5 graviton-mass forecast, "
        "Eöt-Wash equivalence, LIGO O4 birefringence (current).\n\n"
        "**v1.19 update** (31 constraints, including swampland program): see above.\n"
    )
    out = Path("docs/results/2026-05-08-v1.19-priority-update.md")
    out.write_text(md, encoding="utf-8")
    print(f"wrote {out}")
    print("\nTop 5 priority experiments at v1.19:")
    for r in rankings[:5]:
        print(f"  {r.label}: excludes {r.cells_excluded} ({100*r.fraction_excluded:.1f}%)")


if __name__ == "__main__":
    main()
