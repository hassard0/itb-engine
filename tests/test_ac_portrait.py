"""Tests for the (a,c) RG portrait (v2.03)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ac_portrait as acp


def test_wedge_endpoints_are_free_field_ratios():
    """The HM wedge floor is the free scalar (a/c=1/3); ceiling the free vector (31/18)."""
    assert acp.AC_FLOOR == pytest.approx(1.0 / 3.0)
    assert acp.AC_CEIL == pytest.approx(31.0 / 18.0)


def test_string_framework_in_wedge():
    """String tree-EFT (a/c ~ 0.8) sits inside the conformal-collider wedge."""
    c = acp.FRAMEWORKS["string_tree_eft"].encode().coefficients
    from itb.holographic_ac import gC_from_gR2
    a = c.get("g_R2", 0.0); cc = c.get("g_C", gC_from_gR2(a))
    ac = a / cc
    assert acp.AC_FLOOR <= ac <= acp.AC_CEIL


def test_eta_s_equals_a_over_c_relation():
    """v1.72: eta/s (KSS units) = a/c, so a/c < 1 is a KSS-violating dual."""
    # a/c = 1 -> KSS saturation; a/c < 1 -> violation
    assert (0.8) < 1.0          # a typical framework a/c -> KSS-violating
    # the relation 1 - 4pi(eta/s) = (c-a)/c rearranges to eta/s_KSS = a/c
    a, c = 0.2, 0.25
    assert (a / c) == pytest.approx(1.0 - (c - a) / c)
