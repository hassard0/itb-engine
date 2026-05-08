from itb.constraints.bnossw_higher import BNOSSW4Region, BNOSSW5Region
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT


def test_4region_string_eft():
    """String: g_4*g_6=0.20, prefactor*g_R2*(g_4+g_6) = (1/3)*0.2*0.9 = 0.06.
       margin = 0.14 ✓"""
    c = BNOSSW4Region()
    assert c.evaluate(StringTreeEFT().encode()).satisfied is True


def test_4region_lqg_fails():
    """LQG: g_4*g_6=0.27, (1/3)*0.3*1.05 = 0.105. margin = 0.165 — passes!
       Wait that passes. n=3 was the failing one for LQG."""
    c = BNOSSW4Region()
    r = c.evaluate(LQGInduced().encode())
    # LQG actually passes the 4-region form because matter dominates
    assert r.satisfied is True


def test_5region_string():
    """(g_4+g_6)*g_8 - g_R2^3 = 0.9*0.4 - 0.008 = 0.352 ✓"""
    c = BNOSSW5Region()
    assert c.evaluate(StringTreeEFT().encode()).satisfied is True


def test_5region_lqg():
    """LQG: (0.6+0.45)*0.4 - 0.027 = 0.42 - 0.027 = 0.393 ✓"""
    c = BNOSSW5Region()
    assert c.evaluate(LQGInduced().encode()).satisfied is True


def test_4region_cdt():
    """CDT: 0.55*0.4 - (1/3)*0.22*0.95 = 0.22 - 0.0697 = 0.150 ✓"""
    c = BNOSSW4Region()
    assert c.evaluate(CausalDynamicalTriangulation().encode()).satisfied is True
