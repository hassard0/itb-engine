import pytest

from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.duality import cross_class_duality_2d, DualityReport


def test_returns_report():
    res = cross_class_duality_2d(
        constraints=[
            ScalarPositivityG4(),
            ScalarPositivityG6(),
            GravitonMixedPositivity(),
            BekensteinTight(),
        ],
        x_param="g_4", x_range=(0.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(0.0, 1.0), y_steps=11,
        fixed_coefficients={"g_R2": 0.5},
    )
    assert isinstance(res, DualityReport)


def test_b_strictly_tighter_than_a_so_b_only_is_zero():
    """Bekenstein-tight is strictly tighter than the Caron-Huot mixed
    positivity. Therefore: B-allowed ⊆ A-allowed, so b_only = 0 and the
    symmetric difference lives in a_only."""
    res = cross_class_duality_2d(
        constraints=[
            ScalarPositivityG4(),
            ScalarPositivityG6(),
            GravitonMixedPositivity(),
            BekensteinTight(),
        ],
        x_param="g_4", x_range=(0.0, 2.0), x_steps=21,
        y_param="g_6", y_range=(0.0, 2.0), y_steps=21,
        fixed_coefficients={"g_R2": 0.5},
    )
    assert res.b_only_count == 0
    # Some cells should be allowed by A but ruled out by tighter B
    assert res.a_only_count > 0


def test_iou_well_below_one_when_classes_differ():
    """When B is tighter than A in the relevant region, IoU should reflect it."""
    res = cross_class_duality_2d(
        constraints=[
            ScalarPositivityG4(),
            ScalarPositivityG6(),
            GravitonMixedPositivity(),
            BekensteinTight(),
        ],
        x_param="g_4", x_range=(0.0, 2.0), x_steps=21,
        y_param="g_6", y_range=(0.0, 2.0), y_steps=21,
        fixed_coefficients={"g_R2": 0.6},
    )
    assert 0.0 <= res.iou <= 1.0
    # they don't fully agree
    assert res.a_only_count + res.b_only_count > 0


def test_raises_when_a_class_missing():
    with pytest.raises(ValueError):
        cross_class_duality_2d(
            constraints=[BekensteinTight()],
            x_param="g_4", x_range=(0.0, 1.0), x_steps=5,
            y_param="g_6", y_range=(0.0, 1.0), y_steps=5,
        )
