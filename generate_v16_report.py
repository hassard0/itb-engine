"""v1.6 battery + experimental priority with anomaly inflow + 't Hooft matching.

The big question: what changes when we add genuinely tight anomaly
constraints that *connect* the parity sector to the matter sector?
For parity-conserving frameworks (string, AS, GR) the new constraints are
trivially satisfied. For LQG-induced (parity-violating), they become a
real test."""

from pathlib import Path

from itb.battery import run_full_battery
from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.anomaly_flow import (
    GeneralizedAnomalyInflow,
    tHooftAnomalyMatching,
)
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
from itb.constraints.cmb_s4 import CMBS4Forecast
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
from itb.engine import check
from itb.experiment_priority import (
    ExperimentForecast,
    rank_experiments,
    render_priority_list,
)
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT


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
    ]
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()]

    print("=" * 60)
    print(f"v1.6 status with {len(constraints)} constraints (anomaly-flow active):")
    for fw in frameworks:
        theory = fw.encode()
        report = check(theory, constraints)
        binding = report.binding or "—"
        print(f"  {fw.name:<20} feasible={report.feasible}  binding={binding}")

    md = run_full_battery(
        constraints=constraints,
        frameworks=frameworks,
        x_param="g_R2_parity", x_range=(-0.3, 0.3), x_steps=21,
        y_param="g_R3_parity", y_range=(-0.2, 0.2), y_steps=21,
        fixed_coefficients={
            "g_4": 0.6, "g_6": 0.45, "g_R2": 0.3, "g_8": 0.4, "g_R3": 0.30,
        },
        label="v1.6 — anomaly-flow active (parity slice fixed at LQG-induced matter)",
    )
    out = Path("docs/results/2026-05-08-v1.6-anomaly-flow-report.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"\nwrote {out}: {len(md)} chars")


if __name__ == "__main__":
    main()
