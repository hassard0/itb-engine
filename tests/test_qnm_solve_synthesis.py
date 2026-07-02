"""Tests for the solve-synthesis + over-determination negative (v2.432)."""

from experiments.qnm_solve_synthesis import run

_RES = run(n_walk=12000)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_over_determination_is_weak():
    od = _RES["over_determination"]
    assert od["over_determined"] is False
    assert od["narrowing_factor"] < 2.0   # 2 fronts do NOT strongly predict the 3rd


def test_solve_options_state():
    o = _RES["solve_options"]
    assert o["1_empirical"]["status"] == "decision-ready"
    assert o["2_rigor"]["status"] == "at its ceiling"
    assert o["3_real_normalization"]["in_engine"] is False
    assert o["4_uv_embedding"]["in_engine"] is False
    assert o["5_write_up"]["status"] == "done"


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "honest negative" in f
    assert "conjunction" in f
    assert "at its ceiling" in f
    sc = _RES["honest_scope"].lower()
    assert "sampled" in sc
    assert "not a new computation" in sc or "synthesis of prior cycles" in sc
