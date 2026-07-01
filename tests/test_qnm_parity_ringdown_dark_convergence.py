"""Tests for the parity-dark-to-ringdown convergence + v2.365 correction (v2.366)."""

from experiments.qnm_parity_ringdown_dark_convergence import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_rank3_unsourceable_from_v2209():
    assert _RES["full_rank_3_source_backed"] is False
    assert _RES["required_rank_for_claim"] == 3
    assert _RES["source_backed_observable_rank"] == 2


def test_parity_odd_axis_is_dark():
    assert _RES["dark_axes"] == ["g_R4_c3"]
    assert _RES["g_R4_c3"]["parity"] == "odd"
    assert _RES["g_R4_c3"]["public_qnm_observable"] is False


def test_engine_ringdown_floor_parity_blind():
    assert _RES["ringdown_floor_parity_blind"] is True


def test_finding_corrects_v2365_and_converges():
    f = _RES["finding"].lower()
    assert "answered" in f and "v2.365" in f
    assert "dark" in f
    assert "two independent ways" in f
    assert "v2.358" in f and "v2.209" in f
    sc = _RES["honest_scope"].lower()
    assert "read from the tested v2.209 artifact" in sc or "v2.209 artifact" in sc
    assert "self-correction" in sc
