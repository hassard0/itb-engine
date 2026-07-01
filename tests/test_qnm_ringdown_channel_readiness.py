"""Tests for the ringdown-channel readiness synthesis (v2.365)."""

from experiments.qnm_ringdown_channel_readiness import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_floor_and_cap_live():
    assert abs(_RES["ringdown_floor_v2349"] - 0.09 ** 2 / 0.193) < 1e-3
    assert _RES["ringdown_floor_v2349"] <= _RES["ringdown_cap_v2351"]


def test_source_coefficients_present():
    assert _RES["source_p_qeft"] == 6
    assert _RES["parspec_source_axis"] == "ell_qEFT_km"


def test_map_is_the_single_blocker():
    led = _RES["readiness_ledger"]
    # exactly the engine->ParSpec map is not ready; the other three pieces are
    assert led["1_floor_present"] and led["2_cap_present"] and led["3_source_qeft_coefficients_present"]
    assert led["4_engine_to_parspec_map_present"] is False
    assert _RES["n_ready_of_4"] == 3
    assert _RES["ready_for_framework_claim"] is False


def test_engine_has_three_axes_parspec_rank1():
    assert len(_RES["engine_R4_axes"]) == 3
    assert _RES["consistency_checks"]["deep_research_question_is_the_map_blocker"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "rank-3 or rank-1" in f or "rank-3-vs-rank-1" in f
    assert "operator_basis_map" in f or "operator-basis map" in f
    assert "not claimable" in f
    sc = _RES["honest_scope"].lower()
    assert "non-claiming" in sc or "not a claim" in sc
    assert "toy basis" in sc
