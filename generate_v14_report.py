"""v1.4 battery + experimental priority with parity-violation sector active.

Now we have 5 framework predictions for g_R2_parity:
  - PureGR: 0
  - StringTreeEFT: 0 (tree-level bosonic string is parity-conserving)
  - AsymptoticSafety: 0 (FRG truncation parity-conserving)
  - LQGInduced: 0.08 (Holst-term parity violation)

The discriminator: LIGO birefringence bound at |g_R2_parity| < 0.1
nearly captures LQG. Tighter values (sigma=0.05) or lower thresholds
would rule it out."""

from pathlib import Path

from itb.battery import run_full_battery
from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
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
        LIGOBirefringenceBound(bound=0.1),
        EFTValidityBox(box=2.0), CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        WeakGravityConjecture(alpha=1.0),
        LIGOGravitonMassBound(bound=0.5),
    ]
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()]

    print("=" * 60)
    print("v1.4 Per-framework status with parity-violation sector active:")
    for fw in frameworks:
        theory = fw.encode()
        report = check(theory, constraints)
        binding = report.binding or "—"
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        print(f"  {fw.name:<20} g_R2_parity={gR2p:>5.2f}  feasible={report.feasible}  binding={binding}")

    md = run_full_battery(
        constraints=constraints,
        frameworks=frameworks,
        x_param="g_R2", x_range=(0.0, 1.0), x_steps=21,
        y_param="g_R2_parity", y_range=(-0.5, 0.5), y_steps=21,
        fixed_coefficients={"g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R3": 0.15},
        label="v1.4 — parity-violation sector active (g_R2 vs g_R2_parity slice)",
    )
    out = Path("docs/results/2026-05-08-v1.4-parity-violation-report.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"\nwrote {out}: {len(md)} chars")

    # Re-rank experiments with parity-violation experiments included
    experiments = [
        ExperimentForecast("LIGO_O5_graviton_mass", "g_R2", 0.0, 0.05),
        ExperimentForecast("LIGO_O4_birefringence_tight", "g_R2_parity", 0.0, 0.02),
        ExperimentForecast("LIGO_O5_birefringence_forecast", "g_R2_parity", 0.0, 0.005),
        ExperimentForecast("Eot_Wash_equivalence", "g_R2", 0.0, 0.02),
        ExperimentForecast("CMB_S4_inflationary_EFT", "g_4", 0.5, 0.10),
        ExperimentForecast("Bouwmeester_gravity_collapse", "g_R3", 0.15, 0.08),
    ]
    rankings = rank_experiments(
        base_constraints=constraints,
        experiments=experiments,
        x_param="g_R2", x_range=(0.0, 0.5), x_steps=21,
        y_param="g_R2_parity", y_range=(-0.2, 0.2), y_steps=21,
        fixed_coefficients={"g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R3": 0.15},
    )
    md2 = render_priority_list(rankings)
    md2 += (
        "\n\n## Notes\n\n"
        "v1.4 sweep is over the parity-violation slice (g_R2 × g_R2_parity)"
        " with all other coefficients fixed at string-EFT values. The two"
        " LIGO birefringence experiments rank highest because they directly"
        " constrain the new g_R2_parity dimension where current bounds are"
        " loosest.\n"
    )
    out2 = Path("docs/results/2026-05-08-v1.4-experimental-priorities.md")
    out2.write_text(md2, encoding="utf-8")
    print(f"wrote {out2}: {len(md2)} chars")
    print("\nTop 3 v1.4 priority experiments:")
    for r in rankings[:3]:
        print(
            f"  {r.label}: excludes {r.cells_excluded} "
            f"({100 * r.fraction_excluded:.1f}%)"
        )


if __name__ == "__main__":
    main()
