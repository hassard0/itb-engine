import pytest
from itb.constraints.base import ConstraintClass
from itb.constraints.cft_flat_space import CFTFlatSpaceBound
from itb.theory import Theory


def test_class_a():
    assert CFTFlatSpaceBound().constraint_class is ConstraintClass.A_AMPLITUDE
    assert "Caron-Huot" in CFTFlatSpaceBound().citation


def test_string_eft_passes_default():
    """String: g_4+g_6=0.9, g_R2+g_R3=0.35. α*0.9=0.45 ≥ 0.35 ✓"""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = CFTFlatSpaceBound(alpha=0.5)
    assert c.evaluate(StringTreeEFT().encode()).satisfied is True


def test_lqg_close_at_default():
    """LQG: g_4+g_6=1.05, g_R2+g_R3=0.6. α*1.05=0.525 < 0.6 ✗"""
    from itb.frameworks.lqg_induced import LQGInduced
    c = CFTFlatSpaceBound(alpha=0.5)
    r = c.evaluate(LQGInduced().encode())
    assert r.satisfied is False


def test_lqg_passes_at_loose_alpha():
    from itb.frameworks.lqg_induced import LQGInduced
    c = CFTFlatSpaceBound(alpha=0.7)
    # alpha*1.05 = 0.735 ≥ 0.6 ✓
    assert c.evaluate(LQGInduced().encode()).satisfied is True


def test_pure_gr_trivially_passes():
    from itb.frameworks.pure_gr import PureGR
    c = CFTFlatSpaceBound()
    assert c.evaluate(PureGR().encode()).satisfied is True
