"""Tests for the new candidate framework encoders (v1.58)."""

from itb.frameworks.causal_set import CausalSet
from itb.frameworks.group_field_theory import GroupFieldTheory
from itb.frameworks.horava_lifshitz import HoravaLifshitz


def test_encoders_have_seven_coefficients():
    for fw in (HoravaLifshitz(), CausalSet(), GroupFieldTheory()):
        c = fw.encode().coefficients
        for k in ("g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"):
            assert k in c


def test_causal_set_is_parity_conserving_low_cubic():
    c = CausalSet().encode().coefficients
    assert c["g_R2_parity"] == 0.0 and c["g_R3_parity"] == 0.0
    assert c["g_R2"] / c["g_R3"] > 2.0          # high ratio: passes forward positivity


def test_horava_lifshitz_is_higher_derivative_heavy():
    c = HoravaLifshitz().encode().coefficients
    assert c["g_R2"] > 0.4 and c["g_R3"] > 0.35   # the defining large higher-derivative terms
    assert c["g_R2_parity"] != 0.0                 # Cotton-tensor parity sector


def test_gft_is_lqg_like_parity_violating():
    c = GroupFieldTheory().encode().coefficients
    assert c["g_R2_parity"] != 0.0                 # Immirzi parity
    assert c["g_R2"] / c["g_R3"] < 1.2             # cubic ~ leading (spin-foam vertex), like LQG


def test_three_distinct_names():
    names = {HoravaLifshitz().name, CausalSet().name, GroupFieldTheory().name}
    assert len(names) == 3
