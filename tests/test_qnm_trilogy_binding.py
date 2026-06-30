"""Tests for the trilogy-binding (which deep requirement bounds the family) result (v2.341)."""

from experiments.qnm_trilogy_binding import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_all_three_satisfied_everywhere():
    fm = _RES["family_worst_signed_distance"]
    for pillar in ("causality", "unitarity", "wgc"):
        assert fm[pillar] >= -1e-9


def test_causality_has_headroom():
    assert _RES["family_worst_signed_distance"]["causality"] > 0.03


def test_unitarity_and_wgc_bind():
    fm = _RES["family_worst_signed_distance"]
    assert fm["unitarity"] < 0.01     # binding
    assert fm["wgc"] < 0.02           # near-binding


def test_causality_is_least_constraining():
    fm = _RES["family_worst_signed_distance"]
    assert fm["causality"] > fm["unitarity"]
    assert fm["causality"] > fm["wgc"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "causality" in f and "headroom" in f
    assert "unitarity" in f and "binding" in f
    assert "wgc" in f or "weak gravity" in f
    sc = _RES["honest_scope"].lower()
    assert "ordering" in sc
    assert "toy basis" in sc
