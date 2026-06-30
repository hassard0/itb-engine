"""Tests for the data-leverage audit (v2.358)."""

from experiments.qnm_data_leverage_audit import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_birefringence_is_the_only_binding_data_constraint():
    # birefringence is tight; the GW constraints are not
    assert _RES["birefringence_signed_distance"] < 0.05
    assert _RES["gw_dispersion_signed_distance"] > 0.05


def test_gw_speed_is_blind_not_knife_edge():
    # the +0.0000 display was an artifact: the deviation is ~2e-5 of the bound (maximally slack)
    assert _RES["gw_speed_ratio_to_bound"] < 1e-3
    assert _RES["gw_speed_ratio_to_bound"] > 0.0


def test_classifications():
    by = {r["constraint"]: r["classification"] for r in _RES["data_constraint_rows"]}
    assert by["cosmic_birefringence_data"] == "BINDING"
    assert by["gw_speed_bound"] == "BLIND"
    assert by["gw_dispersion_bound"] == "SLACK"
    assert "VACUOUS" in by["submm_gravity_yukawa_bound"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "only one actively binds" in f or "only one" in f
    assert "blind" in f
    assert "display artifact" in f          # the recorded self-correction
    sc = _RES["honest_scope"].lower()
    assert "self-correction" in sc
    assert "toy basis" in sc
