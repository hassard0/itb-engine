"""Tests for the TCC-inflation tension (v2.472)."""

from experiments.qnm_tcc_inflation_tension import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_candidate_violates_tcc():
    assert _RES["r_candidate"] > 1e-3
    assert _RES["orders_r_above_tcc_ceiling"] > 20
    assert _RES["N_starobinsky"] > _RES["N_tcc_bound"]


def test_swampland_non_uniform():
    sc = _RES["swampland_scorecard"]
    assert sc["trans_planckian_censorship"].startswith("VIOLATES")
    supports = [k for k, v in sc.items() if v.startswith("SUPPORTS")]
    assert len(supports) == 3   # refined-dS, AdS-distance, ESC


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "non-uniform" in f
    assert "litebird" in f and "disfavor" in f
    sc = _RES["honest_scope"].lower()
    assert "class-level" in sc
    assert "conjectural" in sc and "contested" in sc
    assert "not a new computation" in sc or "synthesis" in sc
