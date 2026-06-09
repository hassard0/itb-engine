"""Tests for the sub-mm gravity DATA constraint (v1.77)."""
import sys
from pathlib import Path

import pytest

from itb.constraints.submm_gravity import SubmmGravityYukawaBound
from itb.theory import Theory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))


def _th(gR2):
    return Theory(coefficients={"g_R2": gR2, "g_4": 0.3, "g_6": 0.2})


def test_threshold_value():
    """The exclusion threshold is ~g_R2 = 0.063 (lambda ~ 50 um)."""
    c = SubmmGravityYukawaBound()
    assert c.g_R2_max == pytest.approx(0.0626, abs=0.01)
    assert 45 <= c.lambda_max_um <= 55


def test_unscreened_excludes_large_gR2():
    c = SubmmGravityYukawaBound(screened=False)
    assert c.evaluate(_th(0.20)).satisfied is False      # dark-energy scalaron excluded
    assert c.evaluate(_th(0.05)).satisfied is True       # heavier scalaron allowed


def test_screened_is_vacuous():
    c = SubmmGravityYukawaBound(screened=True)
    assert c.evaluate(_th(0.40)).satisfied is True       # screening evades the bound


def test_gradient_pushes_gR2_down():
    c = SubmmGravityYukawaBound(screened=False)
    g = c.gradient(_th(0.2))
    assert g["g_R2"] == -1.0
    assert c.gradient(_th(0.2)) is not None


def test_build_stack_data_optional():
    """Default stack is theoretical-only; include_data appends exactly one
    constraint (so all prior results/tests are unchanged)."""
    from stack import build_stack
    theo = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    data = build_stack(bnossw_mean="geometric", rfc_form="convex_hull",
                       include_data=True)
    assert len(data) == len(theo) + 1
    assert data[-1].name == "submm_gravity_yukawa_bound"
    assert "submm_gravity_yukawa_bound" not in [c.name for c in theo]
