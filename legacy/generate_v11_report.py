"""Generate the v1.1 baseline report — full battery with three independent
class-B (information-theoretic) constraints: Bekenstein-tight, holographic
subadditivity, BNOSSW monogamy. Re-tests cross-class duality vs v1.0 (which
collapsed to IoU=0.007)."""

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
from itb.constraints.holographic_entropy import (
    BNOSSWMonogamy,
    HolographicSubadditivity,
)
from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.constraints.swampland import WeakGravityConjecture
from itb.duality import cross_class_duality_2d
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT


def main() -> None:
    constraints = [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarPositivityG8(),
        ScalarConvexityG6vsG4(),
        DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(),
        BekensteinTight(),
        HolographicSubadditivity(),
        BNOSSWMonogamy(),
        EFTValidityBox(box=2.0),
        CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        WeakGravityConjecture(alpha=1.0),
        LIGOGravitonMassBound(bound=0.5),
    ]
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()]
    md = run_full_battery(
        constraints=constraints,
        frameworks=frameworks,
        x_param="g_4",
        x_range=(-1.0, 2.0),
        x_steps=31,
        y_param="g_6",
        y_range=(-1.0, 2.0),
        y_steps=31,
        fixed_coefficients={"g_R2": 0.3, "g_8": 0.4},
        label="v1.1 — adds BNOSSW MMI + holographic subadditivity (class B with three constraints)",
    )
    out = Path("docs/results/2026-05-08-v1.1-bnossw-report.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"wrote {out}: {len(md)} chars")

    # Also run a focused duality test in the asymmetric region where MMI
    # should bite — at g_R2 = 0.5, the Bekenstein-tight bound gives a
    # different region than the harmonic-mean MMI bound.
    dual = cross_class_duality_2d(
        constraints=constraints,
        x_param="g_4", x_range=(0.0, 2.0), x_steps=31,
        y_param="g_6", y_range=(0.0, 2.0), y_steps=31,
        fixed_coefficients={"g_R2": 0.5, "g_8": 0.4},
    )
    print(
        f"DUALITY RECHECK at g_R2=0.5: IoU={dual.iou:.4f}, "
        f"A_only={dual.a_only_count}, B_only={dual.b_only_count}, both={dual.both_count}"
    )


if __name__ == "__main__":
    main()
