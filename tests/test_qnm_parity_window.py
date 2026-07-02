"""Tests for the parity-magnitude decomposition (v2.418)."""

from experiments.qnm_parity_window import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_rigorous_ceiling():
    w = _RES["parity_windows"]["rigorous_implied_no_data_no_toy"]
    assert 0.2 < w[1] < 0.35
    assert any("left_handed_graviton_positivity" in c for c in _RES["ceiling_binding_constraint"])


def test_toy_only_tightens_upper_edge():
    data = _RES["parity_windows"]["rigorous_implied_plus_birefringence_data_no_toy"]
    full = _RES["parity_windows"]["full_with_toy_inflow"]
    assert abs(full[0] - data[0]) < 0.005      # lower edge unchanged (set by data)
    assert full[1] < data[1]                    # toy only tightens the upper edge


def test_candidate_needs_no_toy():
    assert _RES["candidate_feasible_without_toy"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "rigorously capped" in f or "rigorous ceiling" in f
    assert "non-value-determining" in f
    sc = _RES["honest_scope"].lower()
    assert "birefringence" in sc
    assert "does not make the toy" in sc or "slice" in sc
