"""Tests for the ghost-freedom / EFT-unitarity result (v2.338)."""

from experiments.qnm_ghost_freedom import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_all_amplitude_constraints_satisfied():
    assert all(d["margin"] >= 0 for d in _RES["amplitude_positivity_margins"])
    assert _RES["n_amplitude_constraints"] >= 12


def test_robustly_inside_unitarity_region():
    assert _RES["min_signed_distance_to_unitarity_boundary"] > 0.03


def test_key_unitarity_constraints_present_and_satisfied():
    names = {d["constraint"]: d["margin"] for d in _RES["amplitude_positivity_margins"]}
    for k in ("graviton_forward_positivity", "cemz_causality", "dispersion_tower_g6_squared_bound"):
        assert k in names
        assert names[k] >= 0


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "ghost-free" in f
    assert "ostrogradsky" in f
    assert "unitarity" in f and "positivity" in f
    sc = _RES["honest_scope"].lower()
    assert "eft / positivity sense" in sc or "eft/positivity" in sc or "eft / positivity" in sc
    assert "not claimed ghost-free as a fundamental" in sc or "fundamental" in sc
    assert "toy basis" in sc
