"""Generate the v1.3 experimental priority ranking — apply the new
ExperimentForecast machinery to a list of plausible upcoming experiments
and write the ranked priority list as a committed artifact.

The 'experiments' here are forecast measurements with realistic-shape
uncertainty estimates:

- LIGO O5 graviton-mass forecast      (g_R2 sensitive to graviton dispersion)
- CMB-S4 inflationary EFT bound        (g_4 sensitive to scalar self-interaction)
- Eot-Wash equivalence-principle test  (g_R2 sensitive to scalar-graviton coupling)
- Lattice QCD higher-curvature bound   (g_6 sensitive to next-order matter)
- Atomic-clock Lorentz-violation test  (g_8 sensitive to higher-order dispersion)
- Bouwmeester gravity-collapse test    (g_R3 sensitive to graviton-graviton coupling)

Output: a markdown priority list, ranked by cells excluded."""

from pathlib import Path

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
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.constraints.swampland import WeakGravityConjecture
from itb.experiment_priority import (
    ExperimentForecast,
    rank_experiments,
    render_priority_list,
)


def main() -> None:
    base_constraints = [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarPositivityG8(),
        ScalarConvexityG6vsG4(),
        DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(),
        CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=1.0),
        BekensteinTight(),
        HolographicSubadditivity(),
        BNOSSWMonogamy(),
        EFTValidityBox(box=2.0),
        CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        WeakGravityConjecture(alpha=1.0),
    ]
    experiments = [
        ExperimentForecast(
            label="LIGO_O5_graviton_mass",
            coefficient_name="g_R2",
            central_value=0.0,
            sigma=0.05,
        ),
        ExperimentForecast(
            label="CMB_S4_inflationary_EFT",
            coefficient_name="g_4",
            central_value=0.5,
            sigma=0.10,
        ),
        ExperimentForecast(
            label="Eot_Wash_equivalence",
            coefficient_name="g_R2",
            central_value=0.0,
            sigma=0.02,
        ),
        ExperimentForecast(
            label="Lattice_QCD_g6_bound",
            coefficient_name="g_6",
            central_value=0.4,
            sigma=0.15,
        ),
        ExperimentForecast(
            label="Atomic_clock_Lorentz",
            coefficient_name="g_8",
            central_value=0.4,
            sigma=0.10,
        ),
        ExperimentForecast(
            label="Bouwmeester_gravity_collapse",
            coefficient_name="g_R3",
            central_value=0.15,
            sigma=0.08,
        ),
    ]
    rankings = rank_experiments(
        base_constraints=base_constraints,
        experiments=experiments,
        x_param="g_4",
        x_range=(0.0, 2.0),
        x_steps=21,
        y_param="g_6",
        y_range=(0.0, 2.0),
        y_steps=21,
        fixed_coefficients={"g_R2": 0.2, "g_8": 0.4, "g_R3": 0.15},
    )
    md = render_priority_list(rankings)
    md += "\n\n## Notes\n\n"
    md += (
        "Rankings reflect *toy* central values and forecast uncertainties. "
        "Real experimental priority requires replacing each forecast with "
        "the published sensitivity from the corresponding instrument's "
        "design report. The architecture is research-grade; the input numbers "
        "are illustrative."
    )

    out = Path("docs/results/2026-05-08-v1.3-experimental-priorities.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"wrote {out}: {len(md)} chars")
    print("\nTop 3 priority experiments:")
    for r in rankings[:3]:
        print(
            f"  {r.label}: excludes {r.cells_excluded} "
            f"({100 * r.fraction_excluded:.1f}%) of currently-allowed cells"
        )


if __name__ == "__main__":
    main()
