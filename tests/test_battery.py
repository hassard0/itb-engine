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


def test_battery_produces_markdown():
    md = run_full_battery(
        constraints=[
            ScalarPositivityG4(), ScalarPositivityG6(),
            ScalarConvexityG6vsG4(), GravitonMixedPositivity(),
            BekensteinTight(), EFTValidityBox(box=2.0),
            CausalityBound(gamma=1.0), AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        ],
        frameworks=[PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()],
        x_steps=11, y_steps=11,
        fixed_coefficients={"g_R2": 0.2},
        label="v0.8-baseline",
    )
    assert "ITB Engine" in md
    assert "Per-framework status" in md
    assert "Pairwise framework distance" in md
    assert "Constraint importance ranking" in md
    assert "Adversarial bootstrap" in md
    # all four frameworks appear
    for name in ("pure_gr", "string_tree_eft", "asymptotic_safety", "lqg_induced"):
        assert name in md


def test_battery_shorter_run_for_smoke():
    """Quick smoke run with small grid for CI speed."""
    md = run_full_battery(
        constraints=[
            ScalarPositivityG4(), ScalarPositivityG6(), BekensteinTight(),
        ],
        frameworks=[PureGR()],
        x_steps=5, y_steps=5,
        fixed_coefficients={"g_R2": 0.0},
        label="smoke",
    )
    assert "Boundedness" in md
