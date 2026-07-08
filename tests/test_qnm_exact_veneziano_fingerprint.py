"""Tests for the exact Veneziano fingerprint (v2.476)."""

import math
from experiments.qnm_exact_veneziano_fingerprint import run, veneziano_forward_residue


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_forward_residues_flat():
    # forward residue -> 1 as t -> 0 for every level
    for n in range(1, 8):
        assert abs(abs(veneziano_forward_residue(n, 1e-7)) - 1.0) < 1e-4


def test_exact_fingerprint_value_and_match():
    res = run()
    z2, z3, z4 = math.pi**2/6, 1.2020569, math.pi**4/90
    assert abs(res["exact_veneziano_forward_fingerprint"] - z2*z4/z3**2) < 1e-3
    assert res["frac_diff_pct"] < 10.0
    # candidate closer to Veneziano than to KK
    assert abs(1.322 - res["exact_veneziano_forward_fingerprint"]) < abs(1.322 - res["kk_value"])


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "exactly flat" in f
    assert "1.232" in f or "zeta(2)zeta(4)/zeta(3)^2" in f
    assert "v2.466" in f and "v2.475" in f
    sc = res["honest_scope"].lower()
    assert "open string" in sc or "open-string" in sc
    assert "closed" in sc and ("virasoro" in sc or "graviton pole" in sc)
    assert "chebyshev" in sc
