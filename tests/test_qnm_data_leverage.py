"""Tests for the data-leverage swing (v2.408)."""

from experiments.qnm_data_leverage import run

_RES = run(n_pts=2500)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_birefringence_is_sole_load_bearing():
    assert _RES["birefringence_opens_x"] > 3.0
    assert _RES["other_data_max_opens_x"] < 1.5
    assert _RES["birefringence_opens_x"] > 4 * _RES["other_data_max_opens_x"]


def test_other_data_non_binding():
    lev = _RES["per_datum_leverage"]
    for k in ("submm_screening", "gw_speed", "gw_dispersion"):
        assert lev[k]["opens_x"] < 1.5


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "only load-bearing datum" in f or "single load-bearing datum" in f
    assert "birefringence-contingent" in f
    assert "structure is robust" in f or "structurally robust" in f
    sc = _RES["honest_scope"].lower()
    assert "local" in sc
    assert "not that it is irrelevant" in sc or "role-vs-leverage" in sc or "mandates that the theory screen" in sc
