"""Tests for the rigorous-cage quantification of option #2 (v2.431)."""

from experiments.qnm_rigorous_cage import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_parity_even_boxed_both_edges():
    cage = _RES["rigorous_cage"]
    for k in ("g_4", "g_6", "g_R2"):
        assert cage[k]["both_edges_rigorous"], k
        assert cage[k]["floor"] > 0.0 and cage[k]["ceiling"] > cage[k]["floor"]


def test_gR3_and_parity_capped_above_floor_free():
    cage = _RES["rigorous_cage"]
    for k in ("g_R3", "g_R2_parity"):
        assert cage[k]["ceiling_rigorous"]      # rigorous upper cap
        assert cage[k]["floor"] == 0.0          # floor free (data selects)


def test_g8_is_the_free_direction():
    assert _RES["g8_upper_free"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "rigor forces the candidate's parity-even shape" in f or "cage" in f
    assert "data forces the scale" in f
    sc = _RES["honest_scope"].lower()
    assert "slice" in sc or "1-d scan" in sc
    assert "parity-conserving" in sc
