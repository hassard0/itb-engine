"""Tests for the dim-8 cross-sector EFThedron bound (v1.61, Dr. M.'s recommendation)."""

import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.cross_sector_efthedron import CrossSectorEFThedron
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.group_field_theory import GroupFieldTheory
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT


def test_class_and_citation():
    c = CrossSectorEFThedron()
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
    assert "EFThedron" in c.citation


def test_targets_lqg():
    """LQG: g_8*g_R2 = 0.4*0.3 = 0.12 < 1.1*g_6*g_R3 = 1.1*0.45*0.3 = 0.1485 -> fails."""
    r = CrossSectorEFThedron(alpha=1.1).evaluate(LQGInduced().encode())
    assert r.satisfied is False
    assert r.margin == pytest.approx(0.12 - 0.1485, abs=1e-4)


def test_parity_conserving_survivors_pass():
    c = CrossSectorEFThedron(alpha=1.1)
    for fw in (StringTreeEFT(), AsymptoticSafety(), CausalDynamicalTriangulation()):
        assert c.evaluate(fw.encode()).satisfied is True


def test_also_flags_gft_the_other_large_cubic():
    """GFT's actual encoder has g_R3=0.28 (LQG-like), so the cross-sector bound
    flags it too: g_8*g_R2=0.112 < 1.1*g_6*g_R3=0.132. The bound independently
    catches BOTH large-cubic spin-foam frameworks (LQG + GFT-if-LQG-like)."""
    assert CrossSectorEFThedron(alpha=1.1).evaluate(GroupFieldTheory().encode()).satisfied is False


def test_gradient_signs():
    g = CrossSectorEFThedron(alpha=1.1).gradient(LQGInduced().encode())
    assert g["g_8"] > 0 and g["g_R2"] > 0       # increasing g_8 or g_R2 helps
    assert g["g_6"] < 0 and g["g_R3"] < 0       # increasing g_6 or g_R3 hurts
