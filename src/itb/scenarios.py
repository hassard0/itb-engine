"""Scenario explorer: parameterized variants of constraint+framework
configurations, each producing its own full-battery report. Enables
sensitivity studies on the constraint set itself."""

from dataclasses import dataclass

from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.base import Constraint, ConstraintClass
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


@dataclass
class Scenario:
    label: str
    description: str
    constraints: list[Constraint]
    frameworks: list
    fixed_coefficients: dict[str, float]
    x_range: tuple[float, float] = (-1.0, 2.0)
    y_range: tuple[float, float] = (-1.0, 2.0)


def baseline_scenario() -> Scenario:
    return Scenario(
        label="baseline",
        description=(
            "All known constraints, all known frameworks, default tolerances, "
            "g_R2 fixed at 0.3."
        ),
        constraints=[
            ScalarPositivityG4(), ScalarPositivityG6(),
            ScalarConvexityG6vsG4(), GravitonMixedPositivity(),
            BekensteinTight(), EFTValidityBox(box=2.0),
            CausalityBound(gamma=1.0),
            AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        ],
        frameworks=[PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()],
        fixed_coefficients={"g_R2": 0.3},
    )


def amplitude_only_scenario() -> Scenario:
    """Class A only: drop info-theoretic and universality constraints."""
    return Scenario(
        label="amplitude-only",
        description="Only amplitude-bootstrap (class A) constraints active.",
        constraints=[
            ScalarPositivityG4(), ScalarPositivityG6(),
            ScalarConvexityG6vsG4(), GravitonMixedPositivity(),
            CausalityBound(gamma=1.0),
        ],
        frameworks=[PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()],
        fixed_coefficients={"g_R2": 0.3},
    )


def info_theoretic_only_scenario() -> Scenario:
    """Class B only: only info-theoretic constraints (Bekenstein)."""
    return Scenario(
        label="info-only",
        description="Only information-theoretic (class B) constraints active.",
        constraints=[BekensteinTight()],
        frameworks=[PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()],
        fixed_coefficients={"g_R2": 0.3},
    )


def strict_anomaly_scenario() -> Scenario:
    """Tighter anomaly tolerance — designed to be more discriminating."""
    return Scenario(
        label="strict-anomaly",
        description=(
            "Anomaly tolerance halved (0.10 instead of 0.20). Same other "
            "constraints. Should rule out frameworks whose anomaly residuals "
            "land in (0.10, 0.20)."
        ),
        constraints=[
            ScalarPositivityG4(), ScalarPositivityG6(),
            ScalarConvexityG6vsG4(), GravitonMixedPositivity(),
            BekensteinTight(), EFTValidityBox(box=2.0),
            CausalityBound(gamma=1.0),
            AnomalyCancellation(c_anom=1.0, tolerance=0.10),
        ],
        frameworks=[PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()],
        fixed_coefficients={"g_R2": 0.3},
    )


def loose_eft_scenario() -> Scenario:
    """Larger EFT validity box: less restrictive cutoff."""
    return Scenario(
        label="loose-eft",
        description=(
            "EFT validity box widened to 4.0 (vs default 2.0). Tests whether "
            "the cutoff was the binding constraint anywhere it appeared to be."
        ),
        constraints=[
            ScalarPositivityG4(), ScalarPositivityG6(),
            ScalarConvexityG6vsG4(), GravitonMixedPositivity(),
            BekensteinTight(), EFTValidityBox(box=4.0),
            CausalityBound(gamma=1.0),
            AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        ],
        frameworks=[PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()],
        fixed_coefficients={"g_R2": 0.3},
        x_range=(-2.0, 4.0),
        y_range=(-2.0, 4.0),
    )


SCENARIOS = [
    baseline_scenario,
    amplitude_only_scenario,
    info_theoretic_only_scenario,
    strict_anomaly_scenario,
    loose_eft_scenario,
]
