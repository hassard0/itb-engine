"""Tests for the superstring fingerprint correction (v2.477)."""

from experiments.qnm_superstring_fingerprint_correction import run, susy_forward_residue


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_susy_residues_one_over_n():
    for n in range(1, 7):
        assert abs(abs(susy_forward_residue(n, 1e-7)) - 1.0 / n) < 1e-4


def test_superstring_differs_from_bosonic_and_worse_match():
    res = run()
    assert abs(res["susy_double_ratio"] - res["bosonic_double_ratio"]) > 0.1
    assert res["match_susy_pct"] > res["match_bosonic_pct"]
    assert res["match_susy_pct"] > 15.0   # ~24%, not a clean match


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "1/n" in f and "not flat" in f
    assert "bosonic" in f and "tachyonic" in f
    assert "overstated" in f or "retracted" in f or "tempered" in f
    sc = res["honest_scope"].lower()
    assert "not string-inconsistent" in sc or "not say the candidate is string" in sc
    assert "prefactor" in sc
    assert "other" in sc  # other heterotic supports still stand
