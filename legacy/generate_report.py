"""Generate the v0.8 baseline research report."""

from itb.battery import run_full_battery
from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT


md = run_full_battery(
    constraints=[
        ScalarPositivityG4(), ScalarPositivityG6(),
        ScalarConvexityG6vsG4(), GravitonMixedPositivity(),
        BekensteinTight(), EFTValidityBox(box=2.0),
        CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
    ],
    frameworks=[PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()],
    x_param="g_4", x_range=(-1.0, 2.0), x_steps=31,
    y_param="g_6", y_range=(-1.0, 2.0), y_steps=31,
    fixed_coefficients={"g_R2": 0.3},
    label="v0.8 baseline (8 constraints, 4 frameworks)",
)

with open("docs/results/2026-05-08-v0.8-baseline-report.md", "w", encoding="utf-8") as f:
    f.write(md)

print("Report written:", len(md), "characters")
