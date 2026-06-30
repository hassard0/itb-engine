"""Tests for the framework observational fingerprints (v2.359)."""

from experiments.qnm_framework_fingerprints import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_parity_is_the_discriminator():
    assert _RES["n_parity_even_excluded"] == 4
    # only the constructed theory and lqg are parity-consistent
    assert set(_RES["parity_consistent_frameworks"]) <= {"engine_constructed", "lqg_induced"}
    assert "engine_constructed" in _RES["parity_consistent_frameworks"]


def test_screening_is_generic():
    # every non-GR framework must screen -> screening does not discriminate the constructed theory
    assert _RES["n_non_gr_must_screen"] == _RES["n_non_gr"]
    assert _RES["n_non_gr"] >= 3


def test_constructed_has_mildest_ringdown():
    floors = {r["framework"]: r["ringdown_floor"] for r in _RES["fingerprints"]}
    nonzero = {k: v for k, v in floors.items() if v > 1e-9}
    assert floors["engine_constructed"] == min(nonzero.values())


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "parity channel is the unique discriminator" in f
    assert "generic" in f and "tempers" in f
    sc = _RES["honest_scope"].lower()
    assert "toy encodings" in sc
    assert "v2.329" in sc
